#!/usr/bin/env python3
"""Benchmark Hermes Web UI Agent Bridge latency through an ipc:// socket.

Runs ping, context_estimate, and one or more chat prompts. Intended for
Hermes Web UI prod/dev/VM service diagnosis where HTTP health is fast but chat
feels slow.

Example:
  python3 scripts/bridge_latency_benchmark.py \
    --endpoint ipc:///tmp/hermes-agent-bridge-prod.sock \
    --profile kira \
    --prompt 'Привет, ты здесь? Ответь одной короткой фразой.'
"""
from __future__ import annotations

import argparse
import json
import socket
import time
import uuid
from typing import Any


def send(endpoint: str, payload: dict[str, Any], timeout: int = 300) -> dict[str, Any]:
    if not endpoint.startswith('ipc://'):
        raise SystemExit('Only ipc:// endpoints are supported by this helper')
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
        line = raw.split(b'\n', 1)[0].decode()
        return json.loads(line)
    finally:
        sock.close()


def context_estimate(endpoint: str, profile: str | None, provider: str | None, model: str | None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        'action': 'context_estimate',
        'session_id': 'perf_estimate_' + uuid.uuid4().hex[:8],
        'messages': [],
    }
    if profile:
        payload['profile'] = profile
    if provider:
        payload['provider'] = provider
    if model:
        payload['model'] = model
    started = time.perf_counter()
    response = send(endpoint, payload, timeout=120)
    return {
        'event': 'context_estimate',
        'elapsed_s': round(time.perf_counter() - started, 3),
        'ok': response.get('ok') is True,
        'profile': response.get('profile'),
        'provider': response.get('provider'),
        'model': response.get('model'),
        'fixed_context_tokens': response.get('fixed_context_tokens'),
        'system_prompt_tokens': response.get('system_prompt_tokens'),
        'tool_tokens': response.get('tool_tokens'),
        'tool_count': response.get('tool_count'),
        'system_prompt_chars': response.get('system_prompt_chars'),
        'error': response.get('error'),
    }


def run_chat(endpoint: str, prompt: str, profile: str | None, provider: str | None, model: str | None, timeout: int) -> dict[str, Any]:
    session_id = 'perf_' + uuid.uuid4().hex[:12]
    payload: dict[str, Any] = {
        'action': 'chat',
        'session_id': session_id,
        'message': prompt,
        'wait': False,
        'timeout': timeout,
    }
    if profile:
        payload['profile'] = profile
    if provider:
        payload['provider'] = provider
    if model:
        payload['model'] = model

    started_at = time.perf_counter()
    started = send(endpoint, payload, timeout=30)
    if not started.get('ok'):
        return {
            'event': 'chat',
            'ok': False,
            'stage': 'start',
            'session_id': session_id,
            'elapsed_s': round(time.perf_counter() - started_at, 3),
            'response': started,
        }

    run_id = str(started.get('run_id'))
    cursor = 0
    event_cursor = 0
    first_delta_s: float | None = None
    output = ''
    status = None
    last: dict[str, Any] = {}
    deadline = time.perf_counter() + timeout

    while time.perf_counter() < deadline:
        out = send(endpoint, {
            'action': 'get_output',
            'run_id': run_id,
            'cursor': cursor,
            'event_cursor': event_cursor,
        }, timeout=30)
        last = out
        if not out.get('ok'):
            return {
                'event': 'chat',
                'ok': False,
                'stage': 'get_output',
                'session_id': session_id,
                'run_id': run_id,
                'elapsed_s': round(time.perf_counter() - started_at, 3),
                'response': out,
            }
        cursor = int(out.get('cursor', cursor) or cursor)
        event_cursor = int(out.get('event_cursor', event_cursor) or event_cursor)
        delta = out.get('delta') or ''
        if delta and first_delta_s is None:
            first_delta_s = time.perf_counter() - started_at
        output = out.get('output') or output
        status = out.get('status')
        if out.get('done'):
            total_s = time.perf_counter() - started_at
            return {
                'event': 'chat',
                'ok': status != 'error',
                'status': status,
                'session_id': session_id,
                'run_id': run_id,
                'ttfb_s': round(first_delta_s, 3) if first_delta_s is not None else None,
                'total_s': round(total_s, 3),
                'output_chars': len(output),
                'excerpt': output[:160].replace('\n', ' '),
                'last_error': out.get('error'),
                'prompt': prompt,
                'profile': profile,
                'provider': provider,
                'model': model,
            }
        time.sleep(0.2)

    try:
        send(endpoint, {'action': 'interrupt', 'session_id': session_id, 'message': 'latency benchmark timeout'}, timeout=10)
    except Exception:
        pass
    return {
        'event': 'chat',
        'ok': False,
        'status': status,
        'session_id': session_id,
        'run_id': run_id,
        'ttfb_s': round(first_delta_s, 3) if first_delta_s is not None else None,
        'total_s': None,
        'output_chars': len(output),
        'excerpt': output[:160].replace('\n', ' '),
        'last_error': last.get('error'),
        'prompt': prompt,
        'profile': profile,
        'provider': provider,
        'model': model,
        'timeout_s': timeout,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', required=True)
    parser.add_argument('--profile')
    parser.add_argument('--provider')
    parser.add_argument('--model')
    parser.add_argument('--timeout', type=int, default=300)
    parser.add_argument('--repeat', type=int, default=1)
    parser.add_argument('--prompt', action='append', required=True)
    parser.add_argument('--skip-context-estimate', action='store_true')
    args = parser.parse_args()

    print(json.dumps({'event': 'ping', 'response': send(args.endpoint, {'action': 'ping'}, timeout=10)}, ensure_ascii=False), flush=True)
    if not args.skip_context_estimate:
        print(json.dumps(context_estimate(args.endpoint, args.profile, args.provider, args.model), ensure_ascii=False), flush=True)
    for prompt in args.prompt:
        for repeat_index in range(args.repeat):
            result = run_chat(args.endpoint, prompt, args.profile, args.provider, args.model, args.timeout)
            result['repeat'] = repeat_index + 1
            print(json.dumps(result, ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
