# Session row status source-of-truth audit

Use when Maxim asks whether chat/session-list statuses conflict, feel stuck, or appear as the wrong dot/state.

## Contract

The session list should resolve one visible business status from server-authoritative `session.rowState.primary` first:

```txt
error
→ needs_approval / needs_clarification
→ stopping
→ running
→ queued
→ unread
→ no dot for idle/read/not_applicable
```

`rowState.runtime` can contain multiple true facts at once (`working`, `queued_count`, `approval_pending`, `last_error`, etc.), but the UI should not independently re-prioritize them. The server `primary` is the collapsed decision.

## High-risk conflict pattern

Do not let client-local runtime props override server `rowState.primary`:

- `streamStates` / `serverWorking` / `isSessionLive()`
- `queueLengths`
- `props.streaming` / `props.waiting` in `SessionListItem.vue`
- legacy `row_status`

These may be useful as a narrow fallback when `rowState` is missing, but they must not beat `error`, `needs_approval`, `needs_clarification`, `stopping`, or `running` from `rowState.primary`.

Concrete failure: if `waiting` is checked before `streaming` or before `rowState.primary`, a running session with queued follow-up messages renders as `queued` instead of `running`.

## Known external-run pitfall

Coding-agent / external-run paths can bypass central row runtime synchronization:

- `emitExternalEvent()` emits socket events but does not necessarily apply row runtime events.
- `markExternalRunCompleted()` can clear `sessionMap` without clearing `session-row-status` process-local `runtimeStates`.

If a coding-agent row sticks on `running`, check whether the terminal path calls `notifySessionRunCompleted({ profile, sessionId, queueRemaining, error })` or an equivalent row-runtime completion helper.

## Audit checklist

1. Read server collapse logic in `packages/server/src/services/hermes/session-row-status.ts` (`primaryFrom`, `notifySessionRunCompleted`).
2. Trace every terminal path (`cli`, `api`, `coding_agent`, abort, queued continuation) and confirm it clears/sets row runtime via the same service.
3. Read `SessionListItem.vue` and ensure `rowState.primary` is the first-class source; local `streaming`/`waiting` is fallback only.
4. Ensure `idle`, `read`, and `not_applicable` do not render a neutral dot unless the product explicitly defines an unknown/stale status.
5. Add regression tests for:
   - `running + queued_count > 0` renders running, not queued;
   - external/coding-agent completion clears running;
   - error/request statuses beat local streaming/waiting;
   - idle/read/not_applicable has no dot.

## Useful files

- Server source: `packages/server/src/services/hermes/session-row-status.ts`
- Run socket source: `packages/server/src/services/hermes/run-chat/index.ts`
- Bridge run source: `packages/server/src/services/hermes/run-chat/handle-bridge-run.ts`
- API run source: `packages/server/src/services/hermes/run-chat/handle-api-run.ts`
- Coding agent source: `packages/server/src/services/hermes/run-chat/handle-coding-agent-run.ts`
- Client row component: `packages/client/src/components/hermes/chat/SessionListItem.vue`
- Client store: `packages/client/src/stores/hermes/chat.ts`
- Server tests: `tests/server/session-row-status.test.ts`
- Client tests: `tests/client/session-list-item.test.ts`
