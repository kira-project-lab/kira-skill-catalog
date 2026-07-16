# Web UI chat latency context split

Use this when Hermes Web UI `/health` is fast but chat feels slow, especially for simple prompts such as “Привет, ты здесь?”. This is a broader prod/dev runtime diagnostic than the VM-vs-PC provider benchmark.

## Goal

Separate the delay into:

1. HTTP/browser/reverse-proxy health;
2. bridge ping and bridge worker backlog;
3. fixed context/tool-schema overhead;
4. raw session history size;
5. post-compression snapshot size;
6. provider/runtime first-token and total latency;
7. synchronous or nearby LLM compression duration.

Do not jump straight to provider switching. A fast `/health` only proves the Web UI process is alive; it says little about chat runtime latency.

## Minimal command sequence

```bash
curl -sS -o /dev/null -w 'local_health http=%{http_code} total=%{time_total}s starttransfer=%{time_starttransfer}s\n' http://127.0.0.1:8648/health
curl -sS -o /dev/null -w 'public_health http=%{http_code} total=%{time_total}s starttransfer=%{time_starttransfer}s\n' https://app.kiraproject.ru/health
python3 references/scripts/bridge_latency_benchmark.py \
  --endpoint ipc:///tmp/hermes-agent-bridge-prod.sock \
  --profile kira \
  --prompt 'Ответь ровно одним словом: готово' \
  --prompt 'Привет, ты здесь? Ответь одной короткой фразой.'
```

For context split against a known heavy session, use `references/scripts/chat_latency_context_split.py` from this skill. Copy it out or run it from the skill directory with explicit paths:

```bash
python3 references/scripts/chat_latency_context_split.py \
  --endpoint ipc:///tmp/hermes-agent-bridge-prod.sock \
  --profile kira \
  --db /home/werserk/.hermes-web-ui/hermes-web-ui.db \
  --session <heavy-session-id> \
  --out /tmp/kira-chat-latency.jsonl
```

## What to record

- `start_ack_s`: bridge accepted the chat request and returned `run_id`.
- `ttfb_s`: first output delta seen through `get_output`.
- `total_s`: run completed.
- `fixed_context_tokens`, `system_prompt_tokens`, `tool_tokens`, `tool_count` from `context_estimate`.
- Raw heavy session: messages, raw chars, estimated tokens.
- Compression snapshot shape: messages/chars/tokens after `chat_compression_snapshots` is applied.
- Recent bridge log compression durations for `compress_*` sessions.
- Bridge `ping` `running_sessions` and worker details; many running Kira sessions can explain large start-ack delays.

## Interpretation

- `/health` sub-second-ish + bridge ping near-zero + chat start ack several seconds: Web UI/Caddy are not the bottleneck; bridge worker/provider/runtime queue is.
- Empty-session `context_estimate` tens of thousands of tokens: fixed prompt/tool schema overhead is material before any user history.
- Raw heavy session hundreds of thousands of tokens: do not test only an empty session; compare the exact heavy session or its compressed snapshot.
- Compression snapshot greatly reduces tokens but still leaves >100k tokens: compression is working, but the resulting context can still be too large for snappy UX.
- `compress_*` runs lasting minutes: user-visible requests can feel stalled if compression is synchronous or competing for the same provider/runtime resources.
- OpenRouter/provider control still slow with the same start ack: the shared bridge/context/runtime overhead is significant; provider alone is not the whole story.

## Evidence pattern from 2026-06-29

A prod/home contour check showed:

- local `/health`: `200`, `0.423s`; public `/health`: `200`, `1.039s`; bridge ping: `0.0003s`.
- Empty `openai-codex / gpt-5.5` simple prompt: start ack `7.54s`, TTFB `11.39s`, total `11.79s`.
- Empty hello prompt: start ack `7.51s`, TTFB `18.25s`, total `18.85s`.
- Empty fixed context: `37,879` tokens: `10,654` system prompt + `27,225` tool schemas across 137 tools.
- Heavy session `mqyikoq1vbtzwp`: raw `1,728` messages / `2.8M` chars / `778,075` estimated tokens.
- Same session after compression snapshot: `333` messages / `533k` chars / `177,083` estimated tokens.
- Recent compression runs: `224.9s` and `279.7s`.

Conclusion for that incident: the slow “Привет, ты здесь?” symptom was real, and the bottleneck was chat runtime/context/compression/provider path, not browser, Caddy, or static Web UI delivery.
