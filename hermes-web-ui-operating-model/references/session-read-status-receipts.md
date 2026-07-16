# Session read-status receipts and realtime sync

Use when shaping or implementing Hermes Web UI session-row read/unread status.

## Product semantics

`read` must mean: the latest relevant message was actually visible to the user in an active focused tab/window long enough to be reasonably readable.

Do not mark read from any of these alone:

- message receipt;
- active session id stored in localStorage;
- background tab;
- hidden/minimized tab/window;
- blurred browser window;
- opening a session route while the latest message is not in viewport.

Browsers cannot prove the user looked at the screen or that another OS window did not cover the browser. The implementable contract is "visible opportunity to read", not literal eye-tracking.

## Recommended client gate

Send a read receipt only when all are true:

1. `document.visibilityState === 'visible'`.
2. `document.hasFocus() === true`.
3. The active route/session id matches the session.
4. The latest relevant message element is visible via `IntersectionObserver` above the agreed threshold, e.g. 60–80%.
5. The visibility condition remains true for a dwell time, e.g. 700–1500 ms.
6. The receipt names the specific latest message id.

Suggested payload:

```json
{
  "sessionId": "...",
  "lastMessageId": "...",
  "visibilityState": "visible",
  "focused": true,
  "latestMessageVisible": true,
  "visibleAt": 1710000000000
}
```

Cancel the dwell timer on `visibilitychange`, `blur`, route change, session switch, latest-message change, or intersection loss.

## Server contract

Keep read/unread server-authoritative and scoped by user + profile + session. Do not trust client-side gating alone.

- Accept a receipt only when the route/session id and payload `sessionId` strictly match the target session.
- Require explicit visible/focused/latest-message-visible evidence in the receipt (`visibilityState === 'visible'`, `focused === true`, `latestMessageVisible === true` or the snake_case equivalent).
- Accept a receipt only if `lastMessageId` is still the latest relevant message when message ids are available.
- Ignore stale receipts for older messages.
- New assistant / other-user messages after a read receipt flip the session back to unread.
- The user's own outgoing message should not make that same user's session unread.
- Return session-row status metadata and `lastMessageAt`/latest activity time from session list/detail APIs.
- Publish a lightweight status/invalidation event to every connected client for the same user/profile; clients refetch rather than mirroring full stores.

## Sync pattern

Follow the pinned-session pattern:

```text
client visibility detector
  -> server read receipt
  -> server-authoritative read state
  -> socket / event invalidation
  -> all tabs/windows/devices refetch session list
```

Use BroadcastChannel/storage events only as local acceleration/fallback, not as the source of truth.

## Acceptance checks

- Background/hidden tab never marks read.
- Blurred window never marks read.
- Opening the session but not seeing the latest message never marks read.
- Latest message visible in focused tab for dwell time marks read.
- Newer incoming message flips back to unread.
- Read status renders no dot; unread/runtime statuses may render a dot.
- Status updates appear in two tabs, two windows, and a second browser/device without reload.
