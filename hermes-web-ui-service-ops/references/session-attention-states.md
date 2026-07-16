# Hermes Web UI session attention / row state

Session-list status is now a server-authoritative product contract, not a browser-derived convenience state.

## Canonical contract

Use `SessionRowState` / `row_state` as the row truth for chat sessions:

```ts
type SessionPrimaryState =
  | 'needs_approval'
  | 'needs_clarification'
  | 'error'
  | 'running'
  | 'queued'
  | 'unread'
  | 'idle'
```

Core semantics:

- `needs_approval` / `needs_clarification`: agent is blocked on Maxim; this outranks all other row states.
- `error`: terminal run error that needs attention.
- `running`: server knows a run is active.
- `queued`: user input is queued behind an active run.
- `unread`: latest agent-visible output has not been read.
- `idle`: no actionable row state.

Visual decorations are separate:

- Active/current row selection is not business row state.
- Pinned is not business row state.
- Read/idle rows should not show a dot.
- Running/success dot should use the bright salad green from the current UI contract (`#9cff57`).

## Read semantics

Unread/read should be based on latest agent-output roles, not user messages:

```text
assistant | tool | command
```

Do not mark rows unread for outgoing user messages or for metadata-only updates.

## Runtime lifecycle pitfall

The most common bug in this area is a stuck pulsing green `running` dot after the agent has finished. Fix at the source: terminal run paths must update/emit runtime row state, not only clear in-memory socket state.

Required pattern after a terminal run event (`run.completed`, `run.failed`, bridge terminal chunk, API terminal event):

1. Clear or update the run state (`working: false`, queue count, pending approval/clarification flags, error).
2. Recompute `row_state` from runtime + read status.
3. Emit `session.row_state.changed` so other tabs/devices update immediately.
4. Then the client should fall back to `unread` or `idle/read` according to server read state.

For queued continuations, only clear `working` when no new active run marker was started. If a next queued run starts immediately, keep row state aligned with the new run instead of briefly settling to idle.

## Client rules

- `SessionListItem` should render from `session.rowState` when present.
- Do not pass local `streaming`/`waiting` row props from `ChatPanel` as primary truth for chat rows.
- Filter `idle`, `current`, `archived`, and `read` out of title-row dot rendering.
- Subscribe to server `session.row_state.changed` events and update only matching profile/session rows.

## Browser QA pattern

When validating status dots on live-dev, prefer the real route/UI flow over direct API shortcuts:

1. Open the session route (`#/hermes/session/<session_id>`) and ensure the document/window is visible and focused.
2. If normal dev login is blocked by initialized DB credentials, generate or obtain a server-signed JWT for an active dev user and seed the browser with:
   - `localStorage.hermes_api_key = <jwt>`
   - `localStorage.hermes_active_profile_name = 'kira'` (or the profile under test)
   This is a QA unblocker only; do not change product auth code for it.
3. For manual read-receipt probes, include the same presence fields the UI sends. The server rejects receipts without active route context:

```js
fetch('/api/hermes/sessions/<session_id>/read-receipt', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    Authorization: 'Bearer ' + localStorage.getItem('hermes_api_key'),
    'X-Hermes-Profile': 'kira',
  },
  body: JSON.stringify({
    activeSessionId: '<session_id>',
    visibilityState: 'visible',
    focused: true,
    latestMessageVisible: true,
    lastMessageId: '<latest_agent_output_message_id>',
    visibleAt: Date.now(),
  }),
})
```

4. Verify both API truth and rendered UI:
   - `GET /api/hermes/sessions?profile=<profile>` reports `row_state.primary = idle` and `read = read` for the read row.
   - The read/idle row has no `.session-item-status` dot.
   - Neighboring unread rows still render `.messenger-row-status--unread`.
   - Check the browser console for new JS errors.
5. Clean up temporary auth helpers/processes after QA.

## Verification checklist

For changes in this area, add focused tests for:

- read state renders no dot;
- running/success dot uses the expected salad color;
- runtime completion clears `running` and falls back to unread/read/idle;
- realtime row-state events update only matching profile rows;
- browser QA confirms API `row_state` and rendered dots agree on live-dev;
- focused build passes.

Suggested commands:

```bash
npm run test -- tests/client/session-list-item.test.ts tests/client/chat-store-session-sync.test.ts tests/server/session-row-status.test.ts
npm run build
```
