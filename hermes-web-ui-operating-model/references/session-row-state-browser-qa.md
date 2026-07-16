# Session Row State Browser QA

Use this reference when validating Hermes Web UI chat-row status dots against the server-authoritative `row_state` contract.

## Scope

Covers browser-visible QA for:

- no-dot states: `idle`, `read`;
- attention states: `unread`, `needs_approval`, `needs_clarification`, `error`;
- runtime states: `running`, `queued`, run completion settling;
- realtime/refetch behavior across another same-user app instance.

## Live-dev setup

1. Verify live-dev is serving the intended commit via `hermes-web-ui-service-ops` before browser QA.
2. If login credentials are unavailable on the initialized dev DB, do **not** change product auth code or reset passwords just for QA. For local live-dev browser QA, seed a short-lived user JWT into `localStorage.hermes_api_key` using the dev `.token` secret and an active DB user, then set `localStorage.hermes_active_profile_name = 'kira'`.
3. Remove any temporary JWT helper files/processes after QA. If the command is destructive and the tool guard asks for approval, stop and ask; do not retry around the guard.

## Read/unread receipt contract

Direct `POST /api/hermes/sessions/:id/read-receipt` needs the same presence payload the UI route would provide. Include:

```json
{
  "activeSessionId": "<session_id>",
  "visibilityState": "visible",
  "focused": true,
  "latestMessageVisible": true,
  "lastMessageId": "<latest readable message id>",
  "visibleAt": 1780000000000
}
```

If `activeSessionId` is missing or does not match the route session id, the server returns `400` with `Read receipts require the active route session id`. That is expected; continue through the active session route/UI or include the correct payload.

## Browser probes

Useful DOM/API checks from the browser console:

```js
// Inspect visible rows and their rendered dot state.
Array.from(document.querySelectorAll('.session-item')).map(el => ({
  text: el.innerText,
  status: el.querySelector('.session-item-status')?.textContent?.trim() || null,
  cls: el.querySelector('.session-item-status')?.className || null,
}))

// Compare API source of truth with rendered UI for a session.
const sid = location.hash.split('/').pop()
const sessions = await fetch('/api/hermes/sessions?profile=kira', {
  headers: {
    Authorization: 'Bearer ' + localStorage.getItem('hermes_api_key'),
    'X-Hermes-Profile': 'kira',
  },
}).then(r => r.json())
sessions.sessions.find(s => s.id === sid).row_state

// Verify running dot color and pulse.
const row = Array.from(document.querySelectorAll('.session-item')).find(el => el.className.includes('active'))
const status = row?.querySelector('.session-item-status')
const dot = status?.querySelector('.messenger-row-status__dot')
({
  status: status?.outerHTML,
  color: dot && getComputedStyle(dot).backgroundColor,
  animation: dot && getComputedStyle(dot).animationName,
  duration: dot && getComputedStyle(dot).animationDuration,
})
```

For `running`, expected computed evidence is `rgb(156, 255, 87)` (`#9cff57`) plus a non-`none` pulse animation.

## Scenario recipes

- **Idle/read no dot:** use an existing read/idle fixture row or post a valid read receipt for the latest readable message. The UI row should have no `.session-item-status`.
- **Unread assistant/tool/command:** verify `row_state.primary === 'unread'`, `read === 'unread'`, latest role in `assistant | tool | command`, and a rendered dot.
- **Stale read receipt:** post a receipt for an older readable message. The server should reject/stale it and the row should stay `unread`.
- **User message:** latest own user message alone must not create `unread`; if a run starts, the row should become `running` instead.
- **Running:** send a message that keeps the run alive long enough for inspection, for example asking the agent to run a short `sleep` command through the terminal. Confirm `primary === 'running'`, `runtime.working === true`, salad-green pulsing dot, and Stop button visible.
- **Completion settling:** after terminal event, refetch sessions. `runtime.working` must become `false`; the row must not stay `running`. It should settle to `unread`, `idle`, `queued`, `needs_approval`, `needs_clarification`, or `error`.
- **Queued while running:** send a second message while the first run is active. Expected API: `queued_count > 0`; expected visible primary while the first run is still active: `running` (higher priority than `queued`). After both runs complete, queue should return to `0` and state should recalc from read/latest output.
- **Clarification:** ask the agent to use `clarify`; expected `needs_clarification` warning dot while waiting, then `unread` or another recalculated state after answering.
- **Approval:** ask the agent to perform an action that triggers tool approval; expected `needs_approval` warning dot while waiting, then recalculated state after allow/deny.
- **Realtime same-user sync:** with one browser session, a same-origin iframe can simulate a second app instance when the browser tool cannot manage two tabs. Load `http://127.0.0.1:8649/#/hermes/chat` in the iframe, then post a read receipt or trigger a runtime transition in the main app. Both main document and iframe should update without manual reload. Remove the iframe after QA.
- **Missed events/refetch:** reload the second instance after a transition. It should recover the authoritative `row_state` from `GET /api/hermes/sessions`.
- **Profile mismatch:** prefer automated tests for profile-filtered events unless you have a real second user/profile permission setup. Browser-checking as super_admin only proves visibility, not denial.

## Pitfalls

- Do not trust only screenshots for status dots. Pair visual evidence with API `row_state` and DOM class/computed-style checks.
- Do not treat pinned/current/selected row visuals as business status. A selected row may be highlighted, but dot rendering must still come only from `row_state.primary`.
- Do not keep polling a failing read-receipt request with the same body; missing route-presence fields are the usual cause.
- A fast model response can complete before you capture `running`. Use a deliberately long but harmless command (`sleep N; echo OK`) when validating pulse/color.
- For `error`, avoid breaking live-dev config just to force a browser failure. Prefer a focused automated test or a controlled, reversible failing run path.