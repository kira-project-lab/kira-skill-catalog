---
name: hermes-token-observability
description: "Diagnose and reduce Hermes Agent token waste without heavy core rewrites: usage tracing, state.db analysis, skill_view payload audits, compression-cost attribution, and profile-local plugin mitigations. Use when Maxim asks where Hermes tokens go, why context is large, whether skills/compression/tool schemas are wasteful, or how to optimize Kira's Hermes profile safely."
version: 1.0.0
author: Kira
license: MIT
metadata:
  hermes:
    tags: [hermes, token-audit, observability, skills, compression, plugins, context]
---

# Hermes Token Observability

Use this skill when the task is to understand, explain, or reduce token usage in Hermes Agent/Kira sessions.

Goal: find the real waste source before changing models, prompts, or core Hermes code.

## Default stance

Prefer profile-local, reversible mitigations before upstream/core changes:

1. measure with `hermes insights`, `state.db`, and token-audit events;
2. attribute cost to context/history/tools/skills/compression/model output/reasoning;
3. fix the largest repeated payload class first;
4. keep raw prompt/tool-result capture off unless Maxim explicitly approves it;
5. avoid broad plugin/tool bundles without a specific measured gap.

## Key model of context loading

A Hermes API call can include:

- SOUL/USER/project context;
- current conversation history;
- tool results already appended to history;
- available tool schemas;
- compressed summaries of older history;
- provider/model request metadata.

`skill_view` is expensive because it returns full `SKILL.md` as a tool result. That result becomes history, so repeated skill loads multiply future input tokens.

## Skill payload diagnosis

When `skill_view` looks expensive, separate these cases:

1. first relevant load: usually valid;
2. repeated load in the same live session before compaction: usually waste;
3. repeated load after compaction/handoff: may be defensive, but should use a compact summary or cache-hit marker;
4. linked-file load: often valid, treat separately from main `SKILL.md`;
5. failed/ambiguous skill lookup: pure waste and a skill-library cleanup signal.

Do not assume compression caused repeated skill loading. Check whether session messages have `compacted=1` or inactive rows, and whether `compress_*` sessions themselves called `skill_view`.

## Diagnostic checklist

Use the smallest query set that answers the question:

- aggregate usage: `hermes insights --days N --source cli`;
- traced events: profile `token-audit/events.jsonl` and report generator if present;
- session totals: `sessions.input_tokens`, `output_tokens`, `reasoning_tokens`, `cache_read_tokens`, `api_call_count`;
- tool payloads: `messages.tool_name`, byte length of `messages.content`;
- skill payloads: parse `skill_view` JSON result `name`, count duplicates by session;
- compaction: inspect `messages.compacted`, `messages.active`, and `compress_%` sessions.

See `references/skill-view-dedupe-analysis.md` for SQL/Python patterns and interpretation notes.

## Common findings

If recent Kira sessions resemble the measured baseline, expect:

- input/context dominates total cost;
- reasoning is usually a small share;
- `skill_view` and large terminal/search/read outputs dominate tool payload;
- compression sessions can be expensive, but often pay for earlier context growth rather than causing it;
- repeated mandatory cognitive/render skill loads are a major waste pattern.

## Preferred mitigations

Order of operations:

1. **SOUL wording fix**: require relevant skills to be available, not blindly reloaded. If a skill was loaded in the current session and has not changed, reuse it.
2. **Profile-local `skill_view` dedupe plugin**: use `transform_tool_result` to replace repeat `skill_view` results with compact cache-hit JSON.
3. **Compact summaries for heavy skills**: on repeated loads or post-compaction uncertainty, return a short summary rather than the full skill.
4. **Trace cache hits**: record `skill_name`, `session_id`, `original_bytes`, `emitted_bytes`, `saved_bytes`, `cache_hit`, and `content_hash` in token-audit metadata.
5. **Then consider LLM-request middleware** to compact old duplicate `skill_view` messages before API calls, but only after the simpler transform hook proves insufficient.
6. **Core Hermes PR** only after the profile-local design proves useful and safe.

## Plugin design notes

A safe `skill_view` dedupe plugin should:

- hook `transform_tool_result`;
- affect only `tool_name == "skill_view"`;
- cache by `session_id + skill_name + file_path + content_hash`;
- pass through first loads unchanged;
- pass through failed results unchanged unless explicitly tracing failures;
- pass through linked-file requests by default;
- return compact cache-hit JSON for repeated unchanged main skill loads;
- fail open on errors;
- store state under the active profile, not another Hermes profile.

Compact result shape can be:

```json
{
  "success": true,
  "name": "hermes-agent",
  "cached": true,
  "full_content_loaded_earlier": true,
  "message": "Skill already loaded earlier in this session; reuse prior content unless a linked file or fresh reload is needed."
}
```

For post-compaction safety, prefer adding a short summary field for high-value skills instead of returning only a cache marker.

## Pitfalls

- Do not optimize by switching models first; measured waste often comes from repeated context, not model reasoning.
- Do not enable raw prompt/tool-result logging by default.
- Do not blame compression without checking `messages.compacted` and `compress_%` sessions.
- Do not treat `cache_read_tokens` as free context; it may be cheaper, but it still indicates repeated payload pressure.
- Do not patch Hermes core before a profile-local plugin can prove the behavior.
- Do not create one narrow skill per report/session. Keep token observability patterns here and put detailed one-off analysis in `references/`.

## Verification

After a mitigation:

1. run a smoke Hermes session that intentionally requests the same skill twice;
2. confirm first `skill_view` result is full and repeated one is compact;
3. confirm no hook errors in profile logs;
4. regenerate a token-audit report;
5. compare `skill_view` result bytes and repeated skill counts before/after;
6. keep a rollback path: remove the profile plugin from `plugins.enabled` and restart the session/gateway.
