# 2026-06-22 Current-Setup Token Audit Plan Notes

Context captured from a planning session with Maxim.

## User constraint

Maxim accepted the tracing/optimization direction but explicitly excluded:

- adding paid resources;
- adding/switching to cheap models as the optimization path.

For this class of task, optimize the current setup first: observability, compression, tool-output compaction, skill payload hygiene, session/delegation limits, and auxiliary-call attribution.

## Observed Kira profile baseline

Runtime/profile:

- Hermes Agent `v0.17.0 (2026.6.19)`.
- Active profile: `/home/werserk/.hermes/profiles/kira`.
- Config: `/home/werserk/.hermes/profiles/kira/config.yaml`.
- Enabled plugins at the time: `agentmemory`, `tokenjuice`.

Config posture:

- `compression.enabled: true`
- `compression.threshold: 0.875`
- `compression.target_ratio: 0.2`
- `compression.protect_last_n: 20`
- `agent.max_turns: 150`
- `delegation.max_iterations: 100`
- `delegation.max_concurrent_children: 1`

Recent 7-day pattern:

- CLI sessions used roughly `51.3M input`, `3.38M output`, `622k reasoning`, and `1.28B cache_read`.
- API-server auxiliary sessions used roughly `8.1M input`, `570k output`, and `275k reasoning`.
- High-frequency tools: `terminal`, `read_file`, `skill_view`, `execute_code`, `search_files`.

Interpretation: do not assume hidden reasoning is the main waste. Input/context and repeated tool/skill payloads are likely larger levers.

## Recommended activation plan shape

1. Freeze a baseline report from `hermes insights` and direct `state.db` SQL.
2. Build a profile-local `token-audit` plugin under `/home/werserk/.hermes/profiles/kira/plugins/token-audit/`.
3. Use Hermes hooks:
   - `pre_api_request`
   - `post_api_request`
   - `api_request_error`
   - `post_tool_call`
   - optionally `transform_tool_result` only after measurement proves a specific tool-output problem.
4. Write metadata-only JSONL events to `/home/werserk/.hermes/profiles/kira/token-audit/events.jsonl`.
5. Enable the plugin by adding `token-audit` to `plugins.enabled` in the Kira profile config.
6. Restart/start a fresh session to load hooks.
7. Trace one normal workday before changing compression/limits.
8. Produce a Markdown report and apply only evidence-backed changes.
9. Re-measure after changes.

## Default event fields

API events:

- timestamp
- session_id, turn_id, api_request_id when available
- source/platform
- model/provider/base_url/api_mode
- input/output/reasoning/cache_read/cache_write tokens
- request message count
- approximate serialized request bytes
- finish_reason, latency, retry/error status

Tool events:

- timestamp
- session_id/task_id when available
- tool_name
- duration_ms
- status
- args_bytes
- result_bytes
- error type/message length

Privacy default: no raw prompts, no raw tool results, no secrets, no full system prompts. If deep debugging is ever needed, make it a short opt-in window such as `HERMES_TOKEN_AUDIT_CAPTURE_RAW=1`, disabled by default.

## Evidence-backed tuning targets

Prefer this order after tracing:

1. Lower/adjust compression threshold if long sessions repeatedly build huge input contexts.
2. Compact or truncate noisy tool outputs before they re-enter context.
3. Slim oversized local skills by moving rare detail into `references/` while preserving mandatory safety/workflow rules.
4. Reduce runaway loops with session/delegation limits if top sessions show high `api_call_count`/`tool_call_count`.
5. Attribute API-server auxiliary sessions before tuning compression/title prompts.

Do not recommend cheaper model routing when the user asked to improve the current setup.
