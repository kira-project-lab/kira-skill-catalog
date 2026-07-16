# Session read-status / unread root cause pattern

Use this when a user expects opening a Hermes session route to mark the session as read.

## Key product fact

Opening `#/hermes/session/:sessionId` only makes the session active in the tab. That is not the same thing as a persisted read receipt.

## What to check

1. **Route handling**
   - Confirm the route only calls `loadSessions(...)` / `switchSession(sessionId)`.
   - A route-selected session is a UI selection, not a server-side read event.

2. **Client read-receipt path**
   - Search for `markRead`, `readReceipt`, `read_at`, `last_read`, `unread`, `visibleAt`, `latestMessageVisible`, `IntersectionObserver`, and `hasFocus`.
   - If none exist, the product has no read-status implementation.

3. **Server schema and API**
   - Check the Hermes session tables for fields such as `read_at`, `last_read_message_id`, `is_read`, or `unread_count`.
   - Check session APIs for a receipt endpoint or status update endpoint.
   - If the schema only has session metadata like `last_active`, `message_count`, `ended_at`, or `cost_status`, there is no persisted read/unread model.

4. **Row-status metadata**
   - Existing row status categories may only cover `current`, `streaming`, `waiting`, `error`, `archived`, or `group`.
   - That means the UI is rendering activity state, not read state.

5. **Visibility refresh is not a receipt**
   - `visibilitychange` handlers that reload the active session are just freshness sync.
   - They do not imply the backend was told the latest message was actually read.

## Root-cause pattern

When the user says "opening the session should make it read", the usual gap is:

- route selection exists;
- active-session UI state exists;
- status metadata exists;
- but there is **no persisted read receipt contract** end to end.

In that case, the correct explanation is:

> the app can track which session is open, but it cannot yet record that the latest message was visible long enough to count as read.

## Verification shortcut

If you need to prove the gap quickly, verify all three layers:

- client route/switch logic;
- client receipt emission;
- server schema/API support.

If any one is missing, read/unread cannot work reliably.
