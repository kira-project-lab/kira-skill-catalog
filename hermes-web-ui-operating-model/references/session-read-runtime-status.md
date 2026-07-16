# Session Read and Runtime Status Semantics

Use this reference when a task touches Hermes Web UI session row status, read/unread behavior, row dots, or read receipts.

## Core rule

Do not model read state and runtime state as the same thing.

### Visible priority

1. Error
2. Any request / request required
3. Working
4. Unread
5. Read

### Meaning

- **Read**: no dot. The latest relevant message was actually visible in a focused, visible tab long enough to count as read.
- **Unread**: green dot. Agent already sent a new relevant message; the user has not satisfied the read contract.
- **Working**: pulsing blue dot. The agent is currently generating or streaming.
- **Any request**: yellow dot. The session needs user action, such as approval or clarification.
- **Error**: red dot. Failure or broken state takes precedence over everything else.

## Read receipt gate

A receipt should only be sent when all are true:

- `document.visibilityState === 'visible'`
- `document.hasFocus() === true`
- the active route matches the session
- the latest relevant business-visible assistant message is visible in the viewport
- the condition survives a short dwell time
- the receipt names the latest relevant message id

Relevant messages for read-state tracking are business-visible assistant outputs with non-empty content. Do **not** treat tool/command chatter as the read target; that content can appear during agent execution but should not advance read/unread by itself.

The client and server must use the same read target. Prefer the server-authoritative `rowState.latest_message_id` / latest non-empty assistant message as the DOM element to observe. Do not let the client independently pick `tool`/`command` as the latest target while the server validates only `assistant`; that can mark a session read even when the actual assistant reply was not visible.

## Client implementation pitfalls

- Split the gate into two functions:
  - **start dwell**: route/focus/visibility/latest-message-visible/latest-message-id/not-already-read;
  - **issue receipt**: all of the above plus `visibleForMs >= SESSION_READ_RECEIPT_DWELL_MS`.
- Do not require the dwell duration before starting the dwell timer. That creates a deadlock: the timer never starts, `visibleSince` resets, and sessions stay unread even when the user is on the page.
- Keep `latestRelevantMessageId` reactive to `chatStore.messages` changes. A `ref` initialized once can stay `null` after messages load/resume, so the IntersectionObserver never binds.
- For strict chat-view read receipts, the receipt payload must name the server-authoritative assistant target: send `lastMessageId` and `observedMessageId` with `rowState.latest_message_id`. Prefer binding the observer to `#message-${rowState.latest_message_id}`, but if live UI messages still use a local transient id, bind the observer to the latest local assistant DOM message while keeping the submitted receipt ids server-authoritative.
- Do not let `tool` or `command` messages advance read state. They may appear after the assistant output, but read/unread should be based on the latest business-visible assistant message that the server also recognizes.
- For long assistant messages, avoid a fixed high intersection ratio such as `0.75`; a large message may never fit enough of itself into the viewport. Use a meaningful visible slice check instead: enough intersecting pixels for long messages, and a proportional slice for short messages.
- Server acceptance should require `lastMessageId === latest assistant message id` and `observedMessageId === lastMessageId`; otherwise visible tool/command tails can falsely mark an assistant reply as read.
- After a successful read-receipt response, update the local session/list `rowState` from the returned `row_state` immediately. Do not wait only for socket/refetch; otherwise the dot can remain stale until the next event.
- If the latest relevant message is virtualized, bind the observer after `nextTick` and retry briefly until `#message-<id>` and `.virtual-message-list` exist.
- Include an explicit observed/read target in the receipt payload (for example `observedMessageId`) and require it to equal both the submitted `lastMessageId` and the current server latest assistant message. The server cannot verify DOM visibility, but it can reject mismatched or stale targets.
- Use a dwell that represents a real opportunity to read. `100ms` is useful for tests/smoke behavior but is too short for product semantics; prefer roughly `700–1000ms` unless Maxim explicitly wants instant acknowledgement.

## UX guardrails

- Keep current/open session highlight separate from read/unread.
- Use one dominant status in the list row, not multiple conflicting badges.
- Do not rely on color alone; pair dot color with tooltip/aria text.
- Treat request subtypes as detail-level information; keep the list row class simple.
- Prefer server-authoritative read/runtime state plus invalidation/refetch across tabs.

## Common mistakes

- Marking a session read just because the route opened.
- Letting working and unread fight for the same visual slot.
- Using localStorage as the source of truth for read state.
- Replacing the dot model with a text-only label in the list, which makes scanability worse.
- Collapsing approval/clarification into unrelated runtime noise without a clear request-required class.
- Coupling read receipts to a non-reactive message id, causing unread to persist after session resume.
