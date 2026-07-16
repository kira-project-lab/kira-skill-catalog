# Session Row Active Status and Quiet Read Rows

Use when changing Hermes Web UI chat/session list status indicators, preview rows, or row-state rendering.

## Durable UI contract

1. Active runtime status must never disappear from the session row.
   - If a session is locally `streaming`, server-working, queued, stopping, waiting for approval, or waiting for clarification, the row must render a visible status indicator and the preview row must stay present.
   - A transient persisted `rowState` of `read` / `idle` must not erase an active local runtime indicator.
   - The Stop button and session-row status should use compatible runtime evidence; if Stop can still stop the run, the row cannot visually look complete/empty.

2. Read/complete rows must be visually quiet.
   - Do not render a gray/neutral dot just to say “read”.
   - Do not render an attention rail for ordinary read/idle rows.
   - Use no dot for read/idle/no-row-state rows unless another active/error/unread condition exists.

## Implementation pattern

- Keep server-authoritative `rowState` as the primary state contract.
- Pass local runtime fallback props from the session list parent to `SessionListItem`, e.g.:
  - `streaming="chatStore.isSessionLive(s.id)"`
  - `waiting="(chatStore.queueLengths.get(s.id) || 0) > 0"`
- In `SessionListItem`, check active fallback props before suppressing dots for `read` rows.
- Return `null` for no-row-state/read/idle status dots; do not create a `neutral`/gray dot as a fallback.

## Tests to protect this

Add/keep focused component tests that assert:

- read `idle` rows have no `.session-item-status-dot` and no `data-attention-tone`;
- rows without `rowState` have no gray neutral dot;
- `streaming=true` still renders a running dot even if persisted `rowState` is temporarily `idle/read`;
- the parent list passes runtime fallback props into `SessionListItem` for both pinned and unpinned rows.

## Pitfall

A previous fix made row state server-authoritative but removed the parent-to-row runtime fallback. That solved some preview races but allowed active rows to briefly render as quiet/read when a stale or transitional row snapshot arrived. Keep the fallback narrow: it should only preserve active runtime visibility, not redefine terminal/read semantics.
