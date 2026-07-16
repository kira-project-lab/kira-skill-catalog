# Chat Status Source Audit

Use this reference when Maxim asks why chat/session status dots, rails, row colors, Stop visibility, or completion styling flicker/reset during an agent run.

## Product target

The user-visible status should be a projection over a single run lifecycle source, not a reconstruction from whichever message/event arrived last.

Desired rule:

- If the Stop affordance says an agent run is still active, the UI must keep an in-progress runtime status.
- While active but not currently thinking/streaming, the stable text projection should remain the latest user/queued-user message.
- Only after a terminal run outcome should the UI switch to terminal success/failure/idle styling and commit final assistant/error preview.

## Audit sequence

1. Identify every status consumer:
   - session row dot/rail/classes
   - active chat header/status area
   - Stop button enabled/visible state
   - composer disabled/running state
   - inspector/run trace status, if present
2. Identify every status producer:
   - server run lifecycle events (`run.*`, abort events, approval/clarification waits)
   - socket session snapshots/refetches
   - message append/update events
   - slash-command echoes and command-result messages
   - tool/reasoning/assistant partial events
3. Compare each consumer against the Stop-button source. Treat Stop availability as the strongest client-side signal that the server still considers the run active.
4. Find reset paths where a non-terminal event writes `idle`/`complete`/`read` or rebuilds row state from the raw message tail.
5. Replace competing derivations with a small normalized lifecycle projection and monotonic snapshot/version guard.

## Fix shape

Prefer a central projection helper/store field over scattered component conditionals:

- Normalize raw inputs into `runStatus`: `error | awaiting_user | stopping | running | queued | idle`.
- Keep committed preview and runtime status as separate axes.
- Apply priority order from `session-card-state-contract.md`.
- Preserve active `running/stopping/awaiting_user` while Stop is visible, even if a slash command, tool result, or assistant chunk boundary arrives.
- Commit final assistant/error preview only on terminal lifecycle events.
- Use snapshot sequence / updated-at checks so stale refetches cannot overwrite newer active state.

## Tests to add

Cover event sequences, not just final snapshots:

- user message -> run starts -> slash command echo -> tool event -> partial assistant text: status remains running and preview remains latest user message.
- active run -> socket refetch returns stale idle/read row: active row remains running while Stop is available.
- run completes successfully: preview commits final assistant text and terminal styling appears.
- run fails/aborts: status commits error/stopping/idle according to terminal event contract.

## Pitfalls

- Do not treat a message append as run completion.
- Do not let read/unread state determine runtime status.
- Do not infer terminal success from “agent sent something”; agents can send partial text and continue using tools.
- Do not fix flicker by hiding dots/rails if the real issue is competing lifecycle sources.
