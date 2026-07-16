# Hermes Web UI chat/session state stabilization notes

Use this reference when a Hermes Web UI task involves chat routing, session row state, realtime session sync, draft/new-chat behavior, or Playwright drift around chat fixtures.

## Durable debugging pattern

1. Treat `/hermes/chat` as a draft route. If a no-session route should show a fresh chat, create/maintain the draft before refreshing session rows, and refresh with fallback selection disabled.
2. Separate explicit route ownership from background list/catch-up ownership:
   - explicit `/hermes/session/:id` may load/fetch the selected session;
   - background row/list catch-up must not select another session or fetch a missing local/transient session just because `activeSessionId` exists.
3. Guard session detail/resume callbacks with a monotonic request sequence and the target session id before mutating `activeSession`, messages, focus, or loading flags.
4. Preserve local-only, not-yet-persisted sessions across list refreshes only when they still match the current profile. Do not fetch them from server during background catch-up.
5. Apply row-state snapshots only when the incoming snapshot version is newer than the current one. Equal/older REST or socket snapshots must not demote a newer local/runtime state.
6. Read receipts must not demote runtime states such as `running`, `needs_approval`, or `needs_clarification`; server tests should lock this.

## E2E/fixture lessons

- If chat Socket.IO is mocked in Playwright, include enough of the real `Socket` shape for every socket client used on the page. Session status sockets may access `socket.io?.on('reconnect', ...)`; mocks should either provide that shape or client code should tolerate it.
- Shared e2e API fixtures should cover session-detail endpoints (`/api/hermes/sessions/:id` and `/api/hermes/sessions/hermes/:id`) when tests seed session summaries; otherwise new explicit-session code can look like an app bug but is fixture drift.
- Voice-dialogue UI may replace the original record toggle with explicit cancel/confirm controls while recording. Tests should assert the recording state via visible recording UI and confirm through the accessible confirm button, not assume the same toggle remains mounted.
- Session-row layout tests should assert usable content/right-edge behavior, not compare content width to full link width when an avatar/profile column is intentionally present.

## Verification ladder used successfully

- Focused unit tests around chat store/session row status.
- Focused Playwright specs for chat/session/native navigation.
- Full `npm run test`.
- `npm run build`.
- Full `npm run test:e2e`.
- `codegraph sync` and `codegraph status` after code changes.
- Restart `hermes-web-ui-dev.service` and verify `/health` reports the pushed commit.

## Commit/push expectation

When the user explicitly says to reach the goal and not forget commit/push, verification + commit + push are part of the deliverable. Do not stop at a dirty verified worktree.