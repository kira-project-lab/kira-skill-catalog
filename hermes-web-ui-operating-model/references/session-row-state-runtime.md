# Session row state runtime completion

Use when implementing or debugging Hermes Web UI chat/session-list row status (`row_state`, status dots, running/queued/read transitions).

## Durable contract

- `row_state` is server-authoritative business state. The client should render row dots from `session.rowState` when present, not from local `streaming` / `waiting` props.
- Read/idle states are not actionable and should not render a visible status dot in the session title row.
- Visual selection/current/pinned state is decoration, not business `row_state`.
- Success/running status dots should use the brighter salad-green tone (`#9cff57`) rather than the darker generic green.

## Runtime completion pitfall

Some run terminal paths emit Socket.IO events from local `emit` closures inside run handlers rather than through `ChatRunSocket.emitToSession()`. Those events can bypass central row-runtime syncing such as `applyRowRuntimeEvent()`.

If a row stays on a green pulsing `running` dot after the agent has finished:

1. Check terminal paths in both:
   - `packages/server/src/services/hermes/run-chat/handle-api-run.ts`
   - `packages/server/src/services/hermes/run-chat/handle-bridge-run.ts`
2. Ensure terminal completion/failure paths explicitly notify the row-state service, e.g. via a helper like `notifySessionRunCompleted({ profile, sessionId, queueRemaining, error })`.
3. The helper should clear runtime-only blockers when the run terminal event is real:
   - `working: false`
   - `approval_pending: false`
   - `clarification_pending: false`
   - `queued_count` from actual remaining queue length
   - `last_error: null` on success, error string on failure
4. Preserve queued continuation behavior: if a queued run is dequeued and `activeRunMarker` is set, do not prematurely settle the row to idle/read.

## Test contracts to add before fixing

- Client: a `read` row status / row state does not render `.session-item-status`.
- Client: success/running dot CSS contains `color: #9cff57;`.
- Server: after runtime `working: true`, applying a completion patch (`working: false`, `queued_count: 0`, `last_error: null`) makes row state fall back to `unread` or `idle/read` based on read receipt state.
- Store/sync: authoritative `session.row_state.changed` events update the session row and ignore other profiles.

## Browser/live-dev QA pattern

When password login blocks browser QA on the Kira live-dev host, do not reset real user passwords just to test UI state. Use a short-lived local-only JWT for the active dev DB/user, inject it into `localStorage.hermes_api_key`, set `localStorage.hermes_active_profile_name = 'kira'`, and navigate to the local frontend (`127.0.0.1:8649`) or the public dev URL as appropriate. Keep the helper outside the repo (for example under `/tmp`) and remove/stop it after QA.

For a real runtime-dot smoke test:

1. Open an existing chat or a new chat on profile `kira`.
2. Send a tiny prompt that completes quickly.
3. While the run is active, inspect the first session row:
   - `aria-label` should be `Status: running`.
   - status class should include `messenger-row-status--running`.
   - dot color should compute to `rgb(156, 255, 87)` / `#9cff57`.
4. After completion, poll the session API and DOM:
   - `row_state.runtime.working` is `false`.
   - `row_state.runtime.last_error` is `null` on success.
   - `row_state.primary` falls back to `unread` when the assistant produced a new unread output.
5. Submit a focused visible read receipt for the latest assistant/tool/command message and verify:
   - `row_state.primary` becomes `idle` or another non-dot read state.
   - the selected row has no `.session-item-status`.
   - neighbouring unread rows still show their dots.
6. Check browser console after the run and after read receipt settlement.

## Verification

Focused checks usually cover this class of change:

```bash
npm run test -- tests/client/session-list-item.test.ts tests/client/chat-store-session-sync.test.ts tests/server/session-row-status.test.ts
npm run build
```

For browser-visible runtime behavior, add the live-dev smoke above: running dot appears with salad green, completion settles to unread, and read receipt removes the dot without hiding neighbouring unread dots.
