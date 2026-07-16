# 2026-06-22 Kira token baseline

Context: Maxim asked how to trace which Hermes Agent processes consume many tokens during thinking and where to improve token economy.

## Observed live baseline

Profile: `/home/werserk/.hermes/profiles/kira`

Hermes version at the time:

- `Hermes Agent v0.17.0 (2026.6.19)`
- binary: `/home/werserk/.hermes/hermes-agent/.venv/bin/hermes`
- active profile root: `/home/werserk/.hermes/profiles/kira`

Last 7 days from `state.db` and `hermes insights --days 7 --source cli`:

- CLI sessions: `93`
- CLI messages: `17,533`
- CLI tool calls: `8,131`
- CLI input tokens: `51,164,951`
- CLI output tokens: `3,373,627`
- CLI cache read tokens: about `1,276,745,728`
- CLI reasoning tokens: `620,962`
- All sources in the same 7-day window: `60,482,043` input, `4,012,391` output, `909,746` reasoning
- Reasoning was about `22.67%` of output tokens across all sources, but input/context was much larger than reasoning.

Top CLI tools by call count in the same window:

1. `terminal` — 3,174
2. `read_file` — 1,139
3. `skill_view` — 936
4. `execute_code` — 857
5. `search_files` — 658
6. `patch` — 528
7. `todo` — 411
8. `write_file` — 356
9. `skill_manage` — 143

Top loaded skills included `using-superpowers`, `critical-expert-judgment`, study/math skills, `kira-obsidian-vault`, `hermes-web-ui-service-ops`, and `anti-meta-spotlight`.

## Interpretation

The strongest first hypothesis was not “reasoning tokens are the main burn.” The visible data pointed to:

- long sessions with thousands of messages/tool calls;
- repeated large input context;
- large tool outputs entering the conversation;
- mandatory skill boot and repeated `skill_view` calls;
- huge prompt-cache reads that need separate interpretation from normal token spend.

## Recommended tracing shape

Build a profile plugin such as `token-audit` rather than enabling raw trajectories.

Use Hermes plugin hooks:

- `pre_api_request`
- `post_api_request`
- `api_request_error`
- `post_tool_call`
- optional `transform_tool_result`

Write JSONL metadata, not raw prompts, by default:

```json
{
  "timestamp": 0,
  "session_id": "...",
  "turn_id": "...",
  "api_request_id": "...",
  "source": "cli",
  "model": "gpt-5.5",
  "provider": "...",
  "api_mode": "...",
  "latency_ms": 0,
  "usage": {
    "input_tokens": 0,
    "output_tokens": 0,
    "cache_read_tokens": 0,
    "cache_write_tokens": 0,
    "reasoning_tokens": 0
  },
  "request_shape": {
    "message_count": 0,
    "system_chars": 0,
    "tools_count": 0,
    "tool_result_chars": 0
  },
  "tool_context": {
    "recent_tool_names": [],
    "large_results": []
  }
}
```

Then report:

- top sessions by `input + output`;
- top sessions by total with cache;
- top API calls by input and by output;
- top tool result sizes;
- tokens per user turn;
- tokens per tool call;
- skill loading frequency and approximate size;
- compression trigger timing.

## Safety choice

Do not make raw trajectory/session JSON dumps the default diagnostic. They can store private user text, tool outputs, secrets, emails, and full prompts. Use metadata-only tracing first; add a short raw-sample window only after explicit approval.
