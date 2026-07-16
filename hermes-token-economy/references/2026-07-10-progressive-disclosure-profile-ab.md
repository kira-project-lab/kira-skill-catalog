# Progressive-disclosure profile A/B rollout

Session: 2026-07-10. This reference records the detailed experiment behind the class-level procedure in `hermes-token-economy`.

## Measurement contract

Use the same model, exact prompt, and neutral working directory for both profiles. Measure:

- `instructions` characters;
- visible tool count;
- serialized tool-schema bytes;
- serialized request-body bytes;
- `input_tokens`;
- `cache_read_tokens`;
- API/tool-call counts;
- exact task result.

For context-size comparisons, use:

```text
total_context_tokens = input_tokens + cache_read_tokens
```

Do not claim a large reduction from `input_tokens` alone when the provider moved repeated prompt tokens into `cache_read_tokens`.

If a short approved diagnostic uses request dumps, retain aggregate metrics only and keep raw dumps out of Git. Use a neutral directory without project instructions so profile changes are isolated from project-context changes.

Do not compare a one-call baseline with a tool-using session's aggregate `sessions.input_tokens`: after a tool call, the session row combines multiple provider requests and may also split repeated prefixes into `cache_read_tokens`. For a fresh-request claim, use an exact one-call session or a captured first request. Use the paired task suite for multi-turn totals.

For final live tool/schema counts, bootstrap the same plugin/MCP registry as the real entrypoint before calling `get_tool_definitions`; a bare import can undercount MCP tools. Report both pre-assembly session-granted count/schema bytes and post-Tool-Search model-visible count/schema bytes, then shut down the temporary MCP manager cleanly. This proves progressive disclosure rather than accidental capability loss.

## Attribution sequence

Change one variable at a time:

1. Measure the live profile.
2. Clone to an isolated profile with no gateway/delivery process.
3. Change only core context; remeasure.
4. Force Tool Search on for MCP/plugin schemas; remeasure.
5. Only if the target is still missed, test opt-in deferral of exact rare core tools; remeasure.
6. Test one lower reasoning-effort level separately.
7. Run the quality/safety suite before promotion.

This sequence prevents prompt, tool, reasoning, and cache effects from being misattributed to each other.

## Safe profile isolation

Before structural edits:

- make a profile rollback snapshot;
- create a separate profile and confirm it has no gateway process;
- inspect clone semantics before trusting them;
- remove messaging and write-capable integration credentials from the clone;
- copy only the model authentication required for evaluation;
- keep `.env`, auth stores, databases, sessions, logs, caches, generated snapshots, and hook-consent files out of the profile Git repository;
- verify an exact-output model call writes only to the clone.

Hermes profile cloning may copy `.env`, config, SOUL, memories, and skills while omitting runtime history/auth databases. Treat this as behavior to inspect against the installed version, not an assumption.

## Exact core-tool deferral contract

If MCP/plugin Tool Search alone is insufficient, preserve capability by adding an opt-in exact-name allowlist such as `defer_core_tools`; do not broadly redefine all core tools as deferrable.

Required invariants:

- default allowlist is empty;
- existing profiles retain directly visible core tools;
- bridge tools can never defer themselves;
- unknown/unclassified tools remain visible;
- only exact configured names move behind Tool Search;
- session toolset scope and approval gates still constrain search and invocation;
- direct essential file/web/terminal/process tools remain available unless explicitly justified;
- deferred core tools pass search → describe → call end-to-end tests.

Minimum tests:

1. config parsing, deduplication, empty-name removal, and bridge-name filtering;
2. default core visibility regression;
3. exact allowlisted classification;
4. assembly retains unlisted tools and injects bridges;
5. search, describe, call-resolution, and scoped-name checks;
6. existing Tool Search and model-tool suites;
7. real isolated CLI model call for search/describe and one read-only invocation.

## Observed staged result

Representative neutral exact-output task:

| Stage | Instructions | Visible tools | Tool schema | Total context tokens |
|---|---:|---:|---:|---:|
| Live | 44,230 chars | 64 | 84,137 bytes | 24,870 |
| Lean core only | 41,498 chars | 64 | 84,152 bytes | 24,116 |
| MCP/plugin Tool Search | 41,498 chars | 26 | 55,077 bytes | 20,009 |
| Exact rare-core deferral | 40,925 chars | 16 | 24,139 bytes | 13,726 |

The core-only change was about 3%, not the misleading 63% suggested by uncached input alone. Progressive tool disclosure produced the large reduction. The final isolated request was about 44.8% below live by total context tokens.

## Long-run checkpoint discipline

Control-plane work can exceed an agent turn or tool-iteration budget. After every validated phase:

- commit the isolated profile slice;
- update the durable execution plan and measurement artifact;
- record exact tests and session IDs needed to resume;
- leave live promotion until the full gate is complete.

An iteration-limit interruption should produce an honest partial checkpoint, never a partial live promotion or a “done” claim.

## Verification caveat

Treat CLI teardown warnings as an independent runtime-quality gate. Do not attribute them to token reduction without evidence. Reproduce, trace cleanup ownership, add a failing regression test, and require clean shutdown before promoting a runtime patch.

## A/B harness correctness

Use `state.db` as the authoritative session record after each CLI case. In current Hermes schemas:

- the cost column is `estimated_cost_usd`;
- the final user-visible answer is the last non-empty `messages` row with `role='assistant'`;
- tool names and result sizes come from `messages` rows with `role='tool'`;
- `skill_view` names are recovered from assistant `tool_calls` JSON, while returned bytes come from the matching tool-result rows.

Do not score raw CLI stdout: quiet CLI output can still contain warnings, reasoning panels, or lifecycle noise that never appears as the final assistant message. Generate blind A/B pairs from persisted final messages, randomize profile labels deterministically, and keep the answer key separate.

For long suites, run bounded chunks and merge them through a validator that fails on duplicate, missing, extra, or model-mismatched `(task_id, profile)` pairs. A pipeline failure before result persistence invalidates that case even if an unlabelled session exists in SQLite; rerun it rather than guessing which row belongs to which profile.

## Runtime identity during research

An isolated profile does not prove which source checkout executes it. Before comparing a local fork with upstream, resolve the code imported by the exact evaluation command:

1. inspect the install directory reported by `hermes --version` when available;
2. under the same environment, inspect the relevant module's `__file__`;
3. account for `PYTHONPATH`, editable installs, and worktrees;
4. run Git comparisons against that resolved checkout.

Do not silently substitute the canonical live checkout for an active worktree. Include one research task in the quality suite that must distinguish official behavior from local uncommitted/feature-branch behavior; this catches routing mistakes that exact-output probes miss.

## Reasoning-effort decision rule

Test lower reasoning effort only after the high-reasoning profile already passes the quality suite. Compare task outputs, safety, total processed context, API/tool loops, and latency—not reasoning tokens alone. Keep the existing effort when the lower setting saves reasoning tokens but increases total context or weakens a safety-first action. The null option is preferable when progressive disclosure already meets the efficiency target.

## Promotion staging

Build an exact allowlist staging tree instead of copying the isolated profile wholesale. Before live copy:

- rewrite isolation-specific absolute hook paths to the live profile path;
- rewrite any `HERMES.md` language that describes the workspace as an experiment;
- exclude auth, state databases, sessions, logs, caches, request dumps, hook-consent state, bytecode, and validation-generated runtime directories;
- run config and hook validation, then remove any artifacts those checks created in staging;
- take and checksum a fresh targeted backup of every live overwrite target;
- dry-run the copy and reject unexpected parent-directory metadata changes or deletions.

Register a new shell hook through Hermes's exact explicit approval path after copy, then run hook doctor or inspect registration and execute synthetic clean/changed/repeat events. File presence alone does not prove the hook is active, and a broad auto-accept can approve unrelated configured hooks.

For final live acceptance, do not trust exact-output markers alone. Query `state.db` and verify the persisted tool-result names prove the intended paths actually ran: one no-tool session, direct core tool, Tool Search bridge plus deferred underlying tool, nested `execute_code`, MCP, skill load, and browser. Add direct fail-closed probes for hidden direct calls and empty/incompatible sandbox grants. Scope post-restart error checks to the current service PID/start time so an earlier denied or partial restart is not misclassified as the replacement process's failure.
