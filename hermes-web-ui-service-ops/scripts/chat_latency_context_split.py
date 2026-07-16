#!/usr/bin/env python3
"""Split Hermes Web UI chat latency into empty/heavy/context/compression signals.

Reads a Web UI SQLite DB for a selected heavy session, compares raw history with
chat_compression_snapshots, runs bridge context_estimate for each shape, and
benchmarks a few prompts through an ipc:// Agent Bridge endpoint.

This helper does not mutate the selected real session; it creates temporary
perf_* bridge sessions.
"""
from __future__ import annotations

import argparse
import json
import socket
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any

SUMMARY_PREFIX = '[Previous conversation compressed summary]'

PROMPTS = {
    'simple': 'Ответь ровно одним словом: готово',
    'hello': 'Привет, ты здесь? Ответь одной короткой фразой.',
    'medium': 'Без инструментов. В 5 коротких пунктах объясни, зачем переносить Киру и Web UI с домашнего ПК на VM.',
}


def bridge(endpoint: str, payload: dict[str, Any], timeout: int = 300) -> dict[str, Any]:
    if not endpoint.startswith('ipc://'):
        raise RuntimeError('Only ipc:// endpoints are supported')
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect(endpoint[len('ipc://'):])
    try:
        sock.sendall((json.dumps(payload, ensure_ascii=False) + '\n').encode())
        raw = b''
        while b'\n' not in raw:
            chunk = sock.recv(65536)
            if not chunk:
                break
            raw += chunk
        if not raw:
            return {'ok': False, 'error': 'empty bridge response'}
        return json.loads(raw.split(b'\n', 1)[0].decode())
    finally:
        sock.close()


def context_estimate(endpoint: str, messages: list[dict[str, str]], profile: str, provider: str | None, model: str | None, timeout: int) -> dict[str, Any]:
    payload: dict[str, Any] = {
        'action': 'context_estimate',
        'session_id': 'perf_est_' + uuid.uuid4().hex[:8],
        'messages': messages,
        'profile': profile,
    }
    if provider:
        payload['provider'] = provider
    if model:
        payload['model'] = model
    started = time.perf_counter()
    resp = bridge(endpoint, payload, timeout=timeout)
    elapsed = round(time.perf_counter() - started, 3)
    keys = [
        'ok', 'profile', 'provider', 'model', 'token_count', 'fixed_context_tokens',
        'system_prompt_tokens', 'tool_tokens', 'message_count', 'tool_count',
        'system_prompt_chars', 'error',
    ]
    return {
        'elapsed_s': elapsed,
        **{key: resp.get(key) for key in keys},
        'raw_chars': sum(len(str(message.get('content', ''))) for message in messages),
    }


def chat(endpoint: str, prompt: str, history: list[dict[str, str]] | None, profile: str, provider: str | None, model: str | None, timeout: int) -> dict[str, Any]:
    session_id = 'perf_' + uuid.uuid4().hex[:12]
    payload: dict[str, Any] = {
        'action': 'chat',
        'session_id': session_id,
        'message': prompt,
        'wait': False,
        'timeout': timeout,
        'profile': profile,
    }
    if history is not None:
        payload['conversation_history'] = history
    if provider:
        payload['provider'] = provider
    if model:
        payload['model'] = model

    started = time.perf_counter()
    start_resp = bridge(endpoint, payload, timeout=60)
    start_ack_s = time.perf_counter() - started
    if not start_resp.get('ok'):
        return {'ok': False, 'stage': 'start', 'start_ack_s': round(start_ack_s, 3), 'response': start_resp, 'session_id': session_id}

    run_id = str(start_resp.get('run_id'))
    cursor = 0
    event_cursor = 0
    first_delta: float | None = None
    done_at: float | None = None
    output = ''
    last: dict[str, Any] = {}
    polls = 0
    deadline = time.perf_counter() + timeout
    while time.perf_counter() < deadline:
        polls += 1
        out = bridge(endpoint, {'action': 'get_output', 'run_id': run_id, 'cursor': cursor, 'event_cursor': event_cursor}, timeout=60)
        last = out
        if not out.get('ok'):
            return {'ok': False, 'stage': 'get_output', 'response': out, 'session_id': session_id, 'run_id': run_id, 'elapsed_s': round(time.perf_counter() - started, 3)}
        cursor = int(out.get('cursor', cursor) or cursor)
        event_cursor = int(out.get('event_cursor', event_cursor) or event_cursor)
        delta = out.get('delta') or ''
        if delta and first_delta is None:
            first_delta = time.perf_counter() - started
        output = out.get('output') or output
        if out.get('done'):
            done_at = time.perf_counter() - started
            break
        time.sleep(0.2)

    if done_at is None:
        try:
            bridge(endpoint, {'action': 'interrupt', 'session_id': session_id, 'message': 'perf benchmark timeout'}, timeout=10)
        except Exception:
            pass
    return {
        'ok': done_at is not None and (last or {}).get('status') != 'error',
        'session_id': session_id,
        'run_id': run_id,
        'status': (last or {}).get('status'),
        'start_ack_s': round(start_ack_s, 3),
        'ttfb_s': round(first_delta, 3) if first_delta is not None else None,
        'total_s': round(done_at, 3) if done_at is not None else None,
        'polls': polls,
        'output_chars': len(output),
        'excerpt': output[:200].replace('\n', ' '),
        'error': (last or {}).get('error'),
    }


def load_history(db_path: Path, session_id: str, mode: str) -> list[dict[str, str]]:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    rows = list(con.execute('select role, content from messages where session_id=? order by id', (session_id,)))

    def normalize(row: sqlite3.Row) -> dict[str, str] | None:
        content = row['content'] or ''
        role = row['role']
        if role in ('user', 'assistant'):
            return {'role': role, 'content': content}
        # Avoid invalid tool-message shape when replaying synthetic history.
        if role == 'tool':
            return {'role': 'user', 'content': f'[tool output omitted in synthetic perf replay]\n{content}'}
        return None

    raw = [msg for row in rows if (msg := normalize(row)) is not None]
    if mode == 'raw':
        return raw

    snap = con.execute(
        'select summary, last_message_index from chat_compression_snapshots where session_id=?',
        (session_id,),
    ).fetchone()
    if not snap:
        return raw
    return raw[:3] + [{'role': 'user', 'content': SUMMARY_PREFIX + '\n\n' + snap['summary']}] + raw[snap['last_message_index'] + 1:]


def emit(handle, kind: str, data: dict[str, Any]) -> None:
    record = {'kind': kind, 'ts': time.time(), **data}
    line = json.dumps(record, ensure_ascii=False)
    print(line, flush=True)
    handle.write(line + '\n')
    handle.flush()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', required=True)
    parser.add_argument('--profile', default='kira')
    parser.add_argument('--db', required=True)
    parser.add_argument('--session', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--provider')
    parser.add_argument('--model')
    parser.add_argument('--timeout', type=int, default=360)
    parser.add_argument('--context-timeout', type=int, default=240)
    parser.add_argument('--openrouter-control-model', default='google/gemini-3-flash-preview')
    parser.add_argument('--skip-provider-control', action='store_true')
    args = parser.parse_args()

    out_path = Path(args.out)
    with out_path.open('w', encoding='utf-8') as handle:
        emit(handle, 'ping', {'response': bridge(args.endpoint, {'action': 'ping'}, timeout=10)})
        empty: list[dict[str, str]] = []
        emit(handle, 'context_estimate', {'case': 'empty', **context_estimate(args.endpoint, empty, args.profile, args.provider, args.model, args.context_timeout)})
        for name in ['simple', 'hello', 'medium']:
            emit(handle, 'chat', {'case': 'empty', 'prompt_name': name, **chat(args.endpoint, PROMPTS[name], None, args.profile, args.provider, args.model, args.timeout)})

        raw_history = load_history(Path(args.db), args.session, 'raw')
        snapshot_history = load_history(Path(args.db), args.session, 'snapshot')
        emit(handle, 'history_shape', {
            'session_id': args.session,
            'raw_messages': len(raw_history),
            'raw_chars': sum(len(m['content']) for m in raw_history),
            'snapshot_messages': len(snapshot_history),
            'snapshot_chars': sum(len(m['content']) for m in snapshot_history),
        })
        emit(handle, 'context_estimate', {'case': 'heavy_raw', 'session_id': args.session, **context_estimate(args.endpoint, raw_history, args.profile, args.provider, args.model, args.context_timeout)})
        emit(handle, 'context_estimate', {'case': 'heavy_after_compression_snapshot', 'session_id': args.session, **context_estimate(args.endpoint, snapshot_history, args.profile, args.provider, args.model, args.context_timeout)})
        emit(handle, 'chat', {'case': 'heavy_after_compression_snapshot', 'session_id': args.session, 'prompt_name': 'hello', **chat(args.endpoint, PROMPTS['hello'], snapshot_history, args.profile, args.provider, args.model, args.timeout)})

        if not args.skip_provider_control:
            emit(handle, 'chat', {
                'case': 'empty_openrouter_control',
                'prompt_name': 'simple',
                'provider': 'openrouter',
                'model': args.openrouter_control_model,
                **chat(args.endpoint, PROMPTS['simple'], None, args.profile, 'openrouter', args.openrouter_control_model, args.timeout),
            })
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
