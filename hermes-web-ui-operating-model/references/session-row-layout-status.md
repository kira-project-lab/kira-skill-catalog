# Session row layout and status affordances

Use when changing Hermes chat session-list cards, row actions, timestamps, profile metadata, or unread/runtime status dots.

## Layout contract

Prefer a two-line session card:

1. Top line: status dot + session title. The title should match the chat header title treatment when Maxim asks for visual parity (`16px`, `600`, `text-primary` in the current UI), not an arbitrary "larger" style.
2. Bottom line: left side profile avatar/name, right side latest activity time.
3. Default session-list width should be wide enough for the two-line row; `275px` is the current good default (`220px + 25%`). Keep resize persistence, but use the wider default for fresh state/reset.

Use the latest activity timestamp (`row_status.timestamp`, then read-status `last_message_at`/equivalent) instead of `createdAt` for the visible time. `createdAt` makes active older sessions look stale.

## Overflow/action controls pitfall

The row action menu (`...`) can accidentally participate in flex width and render outside the card. Keep row actions contained by making the card `position: relative` and placing actions as an absolutely positioned affordance. Do not reserve persistent row/content width for the hidden action; keep the action width at `0` until hover/focus so the session title/meta reclaim the space, then let the menu overlay inside the card.

Do not solve this by globally hiding overflow if it clips focus rings, menus, status-dot glow, or tooltips; fix the row's internal layout first.

## Status dot visual contract

The status dot is a scan target, not decoration. For unread/runtime status rows, keep it large and high-contrast enough to be visible at sidebar density (10px worked better than the earlier 7px). Strengthen color/glow while preserving the existing semantic status mapping (`kind`/`tone`) so API/i18n contracts do not change. If the glow/dot clips inside a compact row, add local safe padding with a negative vertical margin on the compact status wrapper (for example `padding: 4px; margin: -4px 0`) instead of shrinking the dot or globally hiding overflow.

Pitfall: bigger/glowing dots can clip inside compact rows because the glow exceeds the dot box. Add local padding/negative margin around compact status affordances (for example `padding: 4px; margin: -4px 0`) rather than shrinking the dot or hiding overflow.

## Status architecture pitfall

When Maxim asks about chat/session row statuses, do not assume the current UI status dot contract is the intended product model. Inspect the actual API, store, and row component first. If `read_status`, `row_status`, runtime maps (`streamStates`, `serverWorking`, queue/approval/clarify maps), and row rendering diverge, treat it as an architectural cleanup candidate rather than a small visual bug.

For a durable messenger-like status system, prefer a server-authoritative row-state contract:

- server owns the business status for ordinary chat rows;
- client renders status and keeps active/current selection and pinned state as separate UI concepts;
- primary status priority should be business-oriented: needs user action > error > running/queued > unread > idle;
- read/unread should be scoped by user/profile/session and created only by agent-output messages, not by user messages;
- realtime sync should push server-authored row-state changes across devices/windows/tabs, with BroadcastChannel/storage only as lightweight invalidation fallback;
- after backend restart, unrecoverable runtime state should clear truthfully instead of showing fake persistent running state.

Canonical decision: `docs/adr/ADR-005 — Server-Authoritative Chat Row State.md`.

## Test expectations

Add/keep focused client/server tests for:

- title before metadata in DOM/source order;
- action controls present but not part of normal row-width flow;
- latest-activity timestamp rendering;
- status-row inputs using latest activity metadata, not session creation time;
- session list default width when the visible sidebar density changes (current chat default: `275px`; remember existing localStorage/user prefs may override the initialization width);
- assistant/agent output creates unread state across windows;
- user messages do not create unread state;
- focused visible read receipts clear unread state across windows;
- stale read receipts are rejected;
- approval/clarification/running/error transitions propagate via realtime row-state events;
- active/current and pinned states do not affect the primary business row status.
