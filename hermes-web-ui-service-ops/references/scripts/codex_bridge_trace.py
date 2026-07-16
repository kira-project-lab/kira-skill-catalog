#!/usr/bin/env python3
"""Trace Hermes agent-bridge latency for a forced provider/model.

Runs ping, context_estimate, and one or more empty-history chat prompts against an ipc://
bridge socket. It records socket roundtrip, start ack, first event, first text delta,
and total completion time as JSONL.

Example PC:
  python3 scripts/codex_bridge_trace.py \
    --surface pc-prod \
    --endpoint ipc:///tmp/hermes-agent-bridge-prod.sock \
    --profile kira \
    --provider openai-codex \
    --model gpt-5.5 \
    --out /tmp/pc-codex-gpt55-trace.jsonl

Example VM tenant:
  sudo -u kira-u-polina python3 scripts/codex_bridge_trace.py \
    --surface vm-usr-polina \
    --endpoint ipc:///data/kira/users/usr_polina/assistants/kira/web-ui-state/agent-bridge.sock \
    --profile default \
    --provider openai-codex \
    --model gpt-5.5 \
    --out /tmp/vm-codex-gpt55-trace.jsonl
"""
import argparse
import json
import socket
import time
import uuid

PROMPTS = {
    "simple": "Ответь ровно одним словом: готово",
    "hello": "Привет, ты здесь? Ответь одной короткой фразой.",
    "medium": "Без инструментов. В 5 коротких пунктах объясни, зачем переносить Киру и Web UI с домашнего ПК на VM.",
}


def _now() -> float:
    return time.perf_counter()


def call(endpoint: str, payload: dict, timeout: int = 300):
    if not endpoint.startswith("ipc://"):
        raise RuntimeError("only ipc:// endpoints are supported")
    path = endpoint[len("ipc://"):]
    t0 = _now()
    sock = socket.socket(socket.AF_UNIX)
    sock.settimeout(timeout)
    sock.connect(path)
    t_conn = _now()
    try:
        sock.sendall((json.dumps(payload, ensure_ascii=False) + "\n").encode())
        t_sent = _now()
        raw = b""
        first_byte = None
        while b"\n" not in raw:
            chunk = sock.recv(65536)
            if not chunk:
                break
            if first_byte is None:
                first_byte = _now()
            raw += chunk
        t_done = _now()
        response = json.loads(raw.split(b"\n", 1)[0]) if raw else {"ok": False, "error": "empty response"}
        timing = {
            "socket_connect_s": round(t_conn - t0, 4),
            "write_to_first_byte_s": round((first_byte or t_done) - t_sent, 4),
            "roundtrip_s": round(t_done - t0, 4),
            "bytes": len(raw),
        }
        return response, timing
    finally:
        sock.close()


def emit(out, record: dict) -> None:
    line = json.dumps(record, ensure_ascii=False)
    out.write(line + "\n")
    out.flush()
    print(line, flush=True)


def compact_response(response: dict) -> dict:
    compact = {key: response.get(key) for key in ["ok", "session_id", "run_id", "status", "done", "cursor", "event_cursor", "error"] if key in response}
    result = response.get("result")
    if isinstance(result, dict):
        text = result.get("final_response") or result.get("response") or result.get("error")
        if text:
            compact["result_excerpt"] = str(text)[:160]
    if response.get("output"):
        compact["output_excerpt"] = str(response.get("output"))[:160]
    if response.get("delta"):
        compact["delta_excerpt"] = str(response.get("delta"))[:80]
    return compact


def context_estimate(endpoint: str, profile: str, provider: str, model: str, out) -> None:
    session_id = "trace_est_" + uuid.uuid4().hex[:8]
    payload = {
        "action": "context_estimate",
        "session_id": session_id,
        "messages": [],
        "profile": profile,
        "provider": provider,
        "model": model,
    }
    t0 = _now()
    response, timing = call(endpoint, payload, timeout=240)
    emit(out, {
        "kind": "context_estimate",
        "session_id": session_id,
        "elapsed_s": round(_now() - t0, 3),
        "socket": timing,
        "provider": provider,
        "model": model,
        **{key: response.get(key) for key in ["ok", "profile", "token_count", "fixed_context_tokens", "system_prompt_tokens", "tool_tokens", "message_count", "tool_count", "system_prompt_chars", "error"]},
    })


def chat(endpoint: str, profile: str, provider: str, model: str, prompt_name: str, out, timeout: int) -> None:
    session_id = "trace_" + uuid.uuid4().hex[:10]
    payload = {
        "action": "chat",
        "session_id": session_id,
        "message": PROMPTS[prompt_name],
        "profile": profile,
        "provider": provider,
        "model": model,
        "wait": False,
        "timeout": timeout,
    }
    t0 = _now()
    started, start_timing = call(endpoint, payload, timeout=90)
    start_ack = _now() - t0
    run_id = started.get("run_id")
    emit(out, {
        "kind": "chat_start",
        "prompt_name": prompt_name,
        "session_id": session_id,
        "run_id": run_id,
        "elapsed_s": round(start_ack, 3),
        "socket": start_timing,
        "response": compact_response(started),
        "provider": provider,
        "model": model,
    })

    cursor = 0
    event_cursor = 0
    polls = 0
    first_delta = None
    first_event = None
    done_at = None
    last = {}
    output = ""
    events_seen = 0
    deadline = _now() + timeout
    while run_id and _now() < deadline:
        polls += 1
        chunk, poll_timing = call(endpoint, {"action": "get_output", "run_id": run_id, "cursor": cursor, "event_cursor": event_cursor}, timeout=90)
        elapsed = _now() - t0
        last = chunk
        events = chunk.get("events") if isinstance(chunk.get("events"), list) else []
        if events and first_event is None:
            first_event = elapsed
        delta = chunk.get("delta") or ""
        if delta and first_delta is None:
            first_delta = elapsed
        output = chunk.get("output") or output
        cursor = chunk.get("cursor", cursor)
        event_cursor = chunk.get("event_cursor", event_cursor)
        events_seen += len(events)
        if polls <= 3 or delta or chunk.get("done") or events:
            emit(out, {
                "kind": "poll",
                "prompt_name": prompt_name,
                "session_id": session_id,
                "run_id": run_id,
                "poll": polls,
                "elapsed_s": round(elapsed, 3),
                "socket": poll_timing,
                "delta_chars": len(delta),
                "events": len(events),
                "done": chunk.get("done"),
                "status": chunk.get("status"),
                "cursor": cursor,
                "event_cursor": event_cursor,
                "error": chunk.get("error"),
            })
        if chunk.get("done"):
            done_at = elapsed
            break
        time.sleep(0.2)

    if done_at is None and run_id:
        try:
            call(endpoint, {"action": "interrupt", "session_id": session_id, "message": "codex trace timeout"}, timeout=20)
        except Exception:
            pass

    result = last.get("result") if isinstance(last.get("result"), dict) else {}
    final_response = result.get("final_response") or result.get("response") or output or ""
    emit(out, {
        "kind": "chat_done",
        "prompt_name": prompt_name,
        "session_id": session_id,
        "run_id": run_id,
        "ok": bool(done_at is not None and last.get("status") != "error"),
        "status": last.get("status"),
        "start_ack_s": round(start_ack, 3),
        "first_event_s": round(first_event, 3) if first_event else None,
        "ttfb_s": round(first_delta, 3) if first_delta else None,
        "total_s": round(done_at, 3) if done_at else None,
        "polls": polls,
        "events_seen": events_seen,
        "output_chars": len(output),
        "final_response_chars": len(final_response),
        "final_response_excerpt": str(final_response)[:240].replace("\n", " "),
        "error": last.get("error"),
        "provider": provider,
        "model": model,
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--surface", required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--profile", default="kira")
    parser.add_argument("--provider", default="openai-codex")
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--out", required=True)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--prompts", nargs="+", default=["simple", "hello"])
    args = parser.parse_args()

    with open(args.out, "w", encoding="utf-8") as out:
        ping, ping_timing = call(args.endpoint, {"action": "ping"}, timeout=20)
        emit(out, {
            "kind": "ping",
            "surface": args.surface,
            "socket": ping_timing,
            "response": {key: ping.get(key) for key in ["ok", "mode", "active_sessions", "running_sessions", "sessions_by_profile", "running_sessions_by_profile"]},
            "workers": ping.get("workers"),
        })
        context_estimate(args.endpoint, args.profile, args.provider, args.model, out)
        for prompt in args.prompts:
            chat(args.endpoint, args.profile, args.provider, args.model, prompt, out, args.timeout)


if __name__ == "__main__":
    main()
