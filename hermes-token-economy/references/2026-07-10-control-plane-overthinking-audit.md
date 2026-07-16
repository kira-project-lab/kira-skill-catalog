# Control-plane overthinking audit — 2026-07-10

Use this reference when Hermes feels hesitant, over-deliberative, or expensive and the user suspects SOUL/skills complexity.

## Durable diagnostic lesson

Do not equate “overthinking” with reasoning tokens. Separate four layers:

1. **Fixed system prompt** — SOUL, runtime contracts, skill catalog, project context, USER/MEMORY.
2. **Fixed tool schemas** — built-in tools and every directly exposed MCP/plugin tool.
3. **Variable procedure context** — full `skill_view` results that remain in later model calls.
4. **Loop behavior** — API calls, tool calls, retries, reasoning effort, and max-turn ceilings.

A short SOUL can still be the main causal lever if it mandates several full skill loads. Report both raw footprint and induced downstream footprint.

## Measurement pattern

Use the canonical profile `state.db` plus recent request dumps when available.

Measure:

- a fresh one-call session's `input_tokens` as the real baseline;
- `LENGTH(sessions.system_prompt)` and segment it by stable markers;
- request `tools` count and serialized schema bytes;
- tool-schema bytes grouped by built-in vs each MCP server;
- visible skill count and skill-catalog characters in `<available_skills>`;
- `skill_view` calls/bytes by skill and the share caused by cognitive/render skills;
- seven-day input, output, cache-read, reasoning, API-call, and tool-call totals;
- compacted-message/session counts before blaming compression;
- plugin/hook discovery and actual telemetry files before crediting optimizers.

Do not treat cache reads as ordinary waste. Use them as evidence of repeated context scale.

## Interpretation rules

- Compare SOUL against the skill catalog and tool schemas; do not blame the most visible file without decomposition.
- Full installed skill-library size is not prompt cost. The recurring costs are the metadata index and skills actually loaded.
- A hardcoded runtime instruction such as “load anything even partially relevant” can defeat progressive disclosure even when the skill system supports it technically.
- If most `skill_view` bytes come from meta/cognitive/render skills, fix routing policy before compressing domain skills.
- If MCP schemas dominate, prefer server tool allowlists or disabling redundant servers before enabling an extra model-driven tool-search round trip.
- Before forcing Tool Search on, check whether an MCP tool must run on every user turn. Deferring such a tool can save static tokens while adding search/describe/call loops and latency.
- High `reasoning_effort` and large `max_turns` are enabling factors, not proven causes. Verify token buckets and high-loop sessions.
- Configured optimization plugins are not evidence of active optimization. Verify registry discovery, hook acceptance, output files, and saved-byte events.

## Recommended fix order

1. Remove universal meta-skill boot and broad “err on the side of loading” policy.
2. Route simple tasks to zero skills; normal tasks to one process skill plus domain skills.
3. Keep render skills for substantial artifacts, not ordinary chat.
4. Reduce MCP schema exposure with allowlists; keep frequently mandatory tools direct.
5. Make the skill index names-only or conditionally hide connector skills when integrations are absent.
6. Lower default reasoning effort and loop ceilings only after context causes are measured.
7. Repair or remove inert optimization hooks/plugins.
8. Tune compression last unless the data shows it dominates.

## Validation targets

A/B test on a cloned profile rather than rewriting the live profile first. Use representative simple, judgment, web, file, browser, code, memory, and long-execution tasks.

Track:

- fresh-call input tokens;
- visible tool count/schema bytes;
- skill loads and skill-result bytes;
- API/tool calls and latency;
- completion quality and user corrections.

Prefer percentage targets over universal absolute numbers because model context windows and tool inventories change. A useful initial goal is 25–40% lower fresh-call input, zero skill loads for simple tasks, and under 30% of tool-result bytes coming from `skill_view`, with no quality or safety regression.

## Safety boundary

Do not trade token savings for weaker destructive-action, production, public, credential, or approval gates. Audit permissive safety settings separately from cognitive efficiency.