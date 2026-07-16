---
name: hermes-token-economy
description: "Analyze and reduce Kira agent token usage: inspect live usage stores, separate input/output/cache/reasoning buckets, design lightweight tracing plugins, and identify high-leverage savings without logging sensitive raw prompts."
version: 1.0.0
author: Kira
license: MIT
metadata:
  trigger: "Use when Maxim wants to understand, trace, audit, profile, or reduce Hermes Agent token usage/cost/context bloat/reasoning tokens."
  related_skills: [hermes-agent]
---

# Hermes Token Economy

Use this skill when the task is to find why Hermes Agent consumes many tokens, compare sessions by usage, add telemetry, or design savings.

This is a companion skill for the protected `hermes-agent` skill. Do not patch bundled/hub Hermes skills from a live task; put local token-economy procedures here.

## Core stance

Optimize from measured buckets, not vibes.

Separate:

- **input tokens** — repeated context, system prompt, tools, memory, skill content, conversation history, tool outputs;
- **output tokens** — assistant visible text, tool calls, hidden/structured model output depending on provider;
- **reasoning tokens** — model-side reasoning budget when exposed by the provider;
- **cache read/write tokens** — prompt-cache accounting, often large and not equivalent to uncached billed tokens;
- **API calls** — repeated loop iterations can dominate even when individual calls look small.

Do not treat `cache_read_tokens` as ordinary token waste. It can indicate massive context reuse, but its billing and latency implications differ by provider.

For controlled A/B comparisons, use `input_tokens + cache_read_tokens` as the provider-reported context denominator. Compare `input_tokens` separately only to discuss uncached/billing behavior. A large fall in `input_tokens` accompanied by a comparable rise in `cache_read_tokens` is cache reuse, not proof that the request became smaller.

## Fast baseline

1. Confirm active version and profile if relevant:
   - `hermes --version`
   - inspect `HERMES_HOME` or use the profile path the user gave.
2. Run aggregate analytics:
   - `HERMES_HOME=<profile> hermes insights --days 7 --source cli`
   - widen to 30 days only if the user asks for trend, not a current hot spot.
3. Query the canonical SQLite store:
   - `<profile>/state.db`
   - `sessions` columns include `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_write_tokens`, `reasoning_tokens`, `api_call_count`, `tool_call_count`.
4. Rank sessions by both:
   - `input_tokens + output_tokens` for billable-ish pressure;
   - `input_tokens + output_tokens + cache_read_tokens + cache_write_tokens` for context/cache scale.
5. Rank tools by calls from `hermes insights` and message/tool-call tables.

## Latency tracing for Codex / Desktop slowness

When Maxim reports that Hermes, Hermes Desktop, TUI, or Codex feels slow, treat this as a timing attribution problem, not only a token/cost problem.

Use the existing profile telemetry before adding new tracing:

- `<profile>/token-audit/events.jsonl` can contain per-event timing:
  - `api_request`: model/API duration, provider, model, input/output/reasoning tokens, request size;
  - `api_request_error`: failed/errored API duration;
  - `tool_call`: tool duration and result size;
  - `session_start` / `session_end`.
- `<profile>/state.db` gives session-level aggregates and metadata: `source`, `title`, `started_at`, `ended_at`, `api_call_count`, `tool_call_count`, token buckets, model, and message counts.

Attribution shape for a slowness report:

1. Rank recent sessions by summed `api_request.duration_ms` plus `api_request_error.duration_ms`.
2. Rank the same window by summed `tool_call.duration_ms`.
3. Surface slowest single API calls separately from sessions with many moderate calls.
4. Compare `source`/platform (`tui`, `cli`, `telegram`, `subagent`, Desktop/Web UI labels when present) so UI/bridge delay is not blamed on Codex without evidence.
5. Compare `input_tokens`, `output_tokens`, and `reasoning_tokens` for the slow sessions, but do not assume tokens caused latency unless the pattern supports it.
6. State whether the current evidence points to model/API wait, local/external tool wait, too many agent-loop iterations, UI/bridge overhead, or a mix.

Useful Python probe pattern:

```python
import json, sqlite3, statistics, datetime
profile = '/home/werserk/.hermes/profiles/kira'
events = f'{profile}/token-audit/events.jsonl'
state = f'{profile}/state.db'
# Parse JSONL defensively: skip corrupt/partial lines, group by session_id,
# sum api_request/api_request_error durations, sum tool_call durations,
# then join state.db sessions for source/title/tokens.
```

If telemetry is missing for older sessions, fall back to `state.db` timestamps and aggregates, and mark the result as coarse. Do not claim per-request latency for sessions that predate token-audit events.

For deeper Desktop-specific tracing, add bridge/UI spans only after the baseline separates model wait from tool wait: user submit → bridge accepted → agent loop started → API request started/ended → tool started/ended → UI received/rendered response.

## Useful SQL probes

Top sessions by non-cache tokens:

```sql
SELECT id, source, model, datetime(started_at,'unixepoch','localtime') started,
       message_count, tool_call_count, api_call_count,
       input_tokens, output_tokens, reasoning_tokens,
       (input_tokens + output_tokens) AS io_tokens,
       cache_read_tokens, cache_write_tokens
FROM sessions
ORDER BY io_tokens DESC
LIMIT 20;
```

Aggregate by source/model:

```sql
SELECT source, model, COUNT(*) sessions,
       SUM(message_count) msgs,
       SUM(tool_call_count) tools,
       SUM(api_call_count) api_calls,
       SUM(input_tokens) input,
       SUM(output_tokens) output,
       SUM(reasoning_tokens) reasoning,
       SUM(cache_read_tokens) cache_read
FROM sessions
WHERE started_at >= strftime('%s','now','-7 days')
GROUP BY source, model
ORDER BY (SUM(input_tokens)+SUM(output_tokens)) DESC;
```

Reasoning share:

```sql
SELECT COUNT(*) sessions,
       SUM(input_tokens) input,
       SUM(output_tokens) output,
       SUM(reasoning_tokens) reasoning,
       ROUND(100.0 * SUM(reasoning_tokens) / NULLIF(SUM(output_tokens),0), 2)
         AS reasoning_pct_of_output
FROM sessions
WHERE started_at >= strftime('%s','now','-7 days');
```

## Tracing strategy

Prefer a narrow Hermes plugin over raw debug dumps.

Good plugin hooks:

- `pre_api_request` — inspect request shape before model call;
- `post_api_request` — record provider usage, model, latency, finish reason;
- `api_request_error` — capture failed/retried calls;
- `post_tool_call` — attribute large/slow tool outputs;
- `transform_tool_result` — optionally compact noisy results before they re-enter context.

Default trace payload should be metadata-only:

- timestamp;
- session_id / turn_id / api_request_id if available;
- source/platform;
- model/provider/base_url/api_mode;
- usage buckets: input, output, cache_read/write, reasoning;
- request message count;
- rough character/token estimates by role and large sections;
- tool names and result sizes;
- latency, finish_reason, retry count.

When reporting latency, be precise about what the metric proves. In current Hermes token-audit traces, `api_request.duration_ms` is wall-clock time from the agent's API-call boundary until the provider transport returns a complete response or error. It includes provider/network/queue/generation/stream time and some local preflight/hook overhead; it does not by itself prove whether the delay was model generation, connect gap, provider idle time, SDK retry, or stream stall. Phrase it as “model/provider API wait” or “Hermes waited for the provider call to complete,” not “the model thought for N seconds.” For deeper diagnosis, add spans for request sent, first delta, last delta, stream finish, SDK retries, and UI/bridge receipt. See `references/2026-07-01-model-api-latency-attribution.md`.

Avoid storing raw prompts, tool outputs, secrets, emails, private chat content, and full system prompts unless the user explicitly approves a short diagnostic window.

## Existing compression surfaces

Check these before inventing a new reducer:

- `compression.threshold`, `target_ratio`, `protect_last_n`, `hygiene_hard_message_limit`;
- `display.resume_*` only changes display, not necessarily model context;
- enabled plugins, especially output reducers such as tokenjuice;
- skill loading frequency and size;
- large tool outputs from `terminal`, `execute_code`, `read_file`, `search_files`, browser snapshots, and vision tools.

## Skill-view attribution

When `skill_view` appears high in tool-result bytes, trace it as its own class of cost. Query `state.db.messages` for `tool_name='skill_view'`, parse the JSON result content for `name`, and rank by bytes, calls, per-session duplicates, and failed/ambiguous loads.

Treat repeated loads of the same unchanged skill inside one session as likely waste unless the skill file changed or the agent needed a linked file. For Maxim, aggregate token totals are not enough; report which skills caused the cost and whether each load was rational for the task.

See `references/2026-06-22-skill-view-attribution.md` for SQL/Python probes and interpretation rules.

## Control-plane overthinking audits

When Hermes feels over-deliberative, do not assume the model's reasoning budget is the cause. Decompose the control plane:

1. fixed system prompt segments;
2. directly exposed tool/MCP schemas;
3. full skill results loaded into conversation history;
4. API/tool-loop behavior.

Measure a fresh one-call session as the real baseline. Compare SOUL's raw size with its **induced cost**: a small boot rule can force several large meta, cognitive, or render skills into every session. Also inspect the hardcoded runtime skill-routing clause; broad language such as “even partially relevant” can defeat progressive disclosure independently of SOUL.

For MCP-heavy profiles, group serialized schema bytes by server. Test forced Tool Search before removing servers or patching runtime: it can defer MCP/plugin schemas while preserving capability. Measure the resulting bridge round trips on tasks that actually need deferred tools.

If forced MCP/plugin Tool Search still misses the target, evaluate opt-in deferral of **exact rare core tool names** rather than broad core-tool removal. Keep the default allowlist empty, keep essential file/web/terminal/process tools direct, preserve unknown-tool visibility and session scoping, and require search → describe → call tests for every deferred capability class. Change core deferral in a separate runtime slice so its effect remains attributable.

Run profile A/B tests in a neutral working directory with the same model and exact prompt. Record instruction characters, visible tool count, serialized schema bytes, request-body bytes, `input + cache_read` context tokens, API/tool calls, and task correctness. Change core context, Tool Search, core deferral, and reasoning effort in separate stages.

Verify optimizers operationally: config entries alone do not prove a plugin or hook is discovered, accepted, emitting telemetry, or transforming the result that enters model context.

See `references/2026-07-10-control-plane-overthinking-audit.md` for the measurement pattern, interpretation rules, fix order, and A/B validation targets.

## Common high-leverage savings

1. **Tool-output compaction**
   - Compact terminal/test/build output before it enters the conversation.
   - Prefer targeted `read_file`/`search_files` over dumping broad command output.
   - For web lookups, prefer purpose-built tools before ad-hoc Python fetch/search loops: Context7 for library docs, GitHub MCP for GitHub, Firecrawl/web tools for public-page scraping and crawling, browser/Playwright for interactive pages, and raw `curl` only for simple endpoints. Use `execute_code` for web only when batching/filtering many requests reduces total tool calls and returns a compact result.

2. **Skill boot discipline**
   - Mandatory skills can be a real input cost.
   - Keep class-level skills concise in SKILL.md and move long session detail to `references/`.
   - Do not load large unrelated skills for simple factual checks.

3. **Session hygiene**
   - Compress before very long sessions hit repeated high-context loops.
   - Start a new session for unrelated work if continuity is not valuable.
   - Watch `api_call_count` and `tool_call_count`; runaway loops multiply the same context.

4. **Model/routing choices**
   - Only suggest cheaper/auxiliary models when the user has not ruled them out. Maxim may explicitly want optimization of the current model/setup instead; in that case focus on tracing, compression timing, tool-output compaction, skill-size hygiene, session splitting, and loop limits.
   - Keep main-model reasoning effort proportional to task stakes when the provider/profile exposes a safe control.

5. **Database-backed attribution**
   - Compare top sessions first. Do not optimize a minor tool if one long coding session dominates the week.

## Pitfalls

- Do not say “reasoning tokens are the main problem” until the buckets prove it. In Hermes sessions, input/context often dominates.
- Do not treat prompt-cache reads as plain wasted tokens.
- Do not report A/B context reduction from `input_tokens` alone; include `cache_read_tokens` and request/schema sizes.
- Do not change core prompt, tool exposure, reasoning effort, and safety policy in one measurement stage. Separate them so regressions and savings remain attributable.
- For multi-phase control-plane rollouts, commit and update the durable plan after every validated phase. A tool-iteration limit must end in an honest resumable checkpoint, never a partial live promotion.
- Do not score raw CLI stdout in profile A/B work. Read the final assistant message and tool/skill attribution from `state.db`; CLI stdout may contain reasoning and warnings. Validate chunk merges for missing and duplicate cases.
- Do not compare a one-call fresh baseline with a multi-call tool session's aggregate `sessions.input_tokens`. For live progressive-disclosure closure, measure one-call request context separately, bootstrap the real MCP/plugin registry for schema counts, and report pre-assembly grants versus model-visible schemas.
- Do not compare an isolated runtime to upstream until the actually imported source is resolved from the same environment (`hermes --version`, module `__file__`, `PYTHONPATH`, worktree/editable-install state).
- Do not promote a lower reasoning effort from reasoning-token savings alone. Preserve the current setting when total context, safety, tool loops, or answer quality regress.
- Do not copy an isolated profile wholesale into live. Stage an exact allowlist, rewrite isolation-specific paths/labels, exclude runtime artifacts, checksum overwrite targets, and dry-run the copy.
- Do not enable full trajectory/session JSON dumps as the first move. They create privacy and disk bloat risks.
- Do not save one-off environment failures as durable rules.
- Do not patch protected bundled/hub skills; create or update a local companion skill instead.
- Verify plugin hook signatures against the live Hermes source before blaming a plugin. In Hermes v0.17, `transform_terminal_output` passes `returncode` and `env_type`, not necessarily `exit_code` and `cwd`; local plugins should accept both shapes and fail open.
- If Maxim rejects paid resources or cheap-model routing, do not keep them as default recommendations. Treat that as a scope constraint and optimize the current setup first.
- In plan mode, save an activation plan under `.hermes/plans/` and include baseline, plugin activation, one-day trace, evidence-backed tuning, validation, and rollback. Do not implement the plugin during the planning turn.

## References

- `references/package-hermes-token-observability/OVERVIEW.md` — absorbed observability-focused token diagnostics package (archived reference material, not an importable skill); use it for detailed live-observability notes not promoted above.
- `references/2026-06-22-kira-token-baseline.md` — baseline observations from Maxim's Kira profile and recommended token-audit plugin shape.
- `references/2026-06-22-current-setup-token-audit-plan.md` — plan-mode notes for improving the current Kira setup without paid resources or cheap-model routing.
- `references/2026-06-22-token-audit-activation-and-tokenjuice-hook.md` — activation/smoke workflow, disk preflight, JSONL validation, and the Hermes v0.17 `transform_terminal_output` `returncode/env_type` compatibility pitfall.
- `references/2026-06-22-skill-view-attribution.md` — SQL/Python probes for ranking `skill_view` payload by skill name, session, duplicates, and failed/ambiguous loads.
- `references/2026-07-10-progressive-disclosure-profile-ab.md` — neutral profile A/B method, safe clone isolation, exact core-tool deferral contract, measured staged results, and resumable checkpoint discipline.
