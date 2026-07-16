# Chat Session State Stability Debugging

Use this when Hermes Web UI has any of these symptoms:

- `/chat` opens or reopens an existing session when the route should show a fresh draft chat.
- Session-row status dots drift from Hermes runtime truth, especially approval/running/blocked/done/read transitions.
- The active chat switches from session A to B without user action, or clicking A still renders B until a third session is selected.

## Core rule

Treat these as one state-ownership problem, not three independent UI bugs. Do not patch the visible symptom first.

Separate and prove ownership for these axes:

- route intent: `/hermes/chat` draft mode vs `/hermes/session/:sessionId` persisted session mode;
- draft chat state;
- active session id;
- loaded active session detail;
- session-list rows and ordering;
- server-authoritative `row_state`;
- read receipt/read axis;
- live stream/runtime state.

## Known high-risk areas

Client:

- `packages/client/src/views/hermes/ChatView.vue`
  - `loadRouteSession()` and route watcher behavior.
- `packages/client/src/stores/hermes/chat.ts`
  - `loadSessions()` fallback selection.
  - `switchSession()` async resume/detail writes.
  - `startDraftChat()` and active-session storage clearing.
  - `subscribeSessionRowStateEvents()` handler.
  - visibility catch-up handler.
- `packages/client/src/stores/hermes/session-row-sync.ts`
  - row-state version comparison helpers.
- `packages/client/src/components/hermes/chat/SessionListItem.vue`
  - visible row-state projection.

Server:

- `packages/server/src/services/hermes/session-row-status.ts`
  - `resolveSessionPrimaryState()`.
  - `acceptVisibleReadReceipt()`.
  - `notifySessionRuntimeStateChanged()`.
  - `applySessionRuntimeEvent()`.
- `packages/server/src/services/hermes/session-status-events.ts`
  - `session.row_state.changed` event path.
- session controllers/routes that return list/detail/read receipt responses.

## First probe for `/chat` opening an existing session

Check whether route `hermes.chat` calls `loadSessions(..., null)` and whether `loadSessions()` falls back to a stored id or `sessions[0]?.id` and then calls `switchSession(targetId)`.

If yes, write a red test before changing code:

1. Mount or simulate `/hermes/chat` with existing sessions returned by the API.
2. Assert `activeSessionId === null` and draft mode remains active.
3. Trigger a session-list/status refresh.
4. Assert no persisted session becomes active.

Expected contract:

- `/hermes/chat` means draft/new-chat route.
- `/hermes/session/:sessionId` means persisted session route.
- Session-list refresh must not switch from draft to persisted mode.

## Stale session-detail response probe

Use controlled async callbacks around `switchSession()`:

1. Seed sessions A and B.
2. Start `switchSession('A')` and hold its resume/detail callback.
3. Start `switchSession('B')` and resolve B first.
4. Resolve A late.
5. Assert active id, active detail, route, and messages still point to B.
6. Repeat with A/B reversed and with clicking the same row again.

Likely fix if reproduced:

- add a monotonic session-detail request token;
- before every async write from `fetchSession()`, `resumeSession()`, visibility resume, or summary refresh, require both the token and `activeSessionId` to still match.

## Row-state drift probe

Write tests around version-gated row-state application:

- current version 10, REST/list/detail/socket gives version 9: ignore status fields;
- current version 10, read receipt response gives read/idle with version 9: ignore;
- current version 10, socket gives version 11: apply;
- equal version: do not demote visible runtime status.

Read receipts must update only the read axis. They must not clear runtime facts such as running, queued, approval pending, clarification pending, aborting, or error.

## Implementation order

1. Red test for `/chat` draft route.
2. Fix route/list loading contract.
3. Red test for A/B stale detail response.
4. Add request-token guards.
5. Red tests for row-state version gating.
6. Centralize row-state apply logic.
7. Server tests for read receipt vs runtime priority.
8. Patch server event paths only if tests prove a missing resolver/version bump.
9. Run focused tests, then `npm run test` and `npm run build`.
10. Restart `hermes-web-ui-dev.service` if needed and manually QA on `https://app.dev.kiraproject.ru`.

## Manual QA checklist

- `/hermes/chat` opens empty draft and stays draft while other sessions update.
- Two tabs converge on running/approval/clarification/completed/read status changes.
- Selecting A/B/C rapidly under throttled network always renders the selected session.
- Clicking A after a stale mismatch renders A directly, without requiring a C detour.
