# Session Card State Contract

Use this reference when the session card must show a stable preview plus a runtime status without flicker, blank rows, or premature completion.

## Product rule

A session card is the composition of two independent axes:

1. **Committed preview** — the last business-visible message that should represent the conversation in the list.
2. **Runtime status** — the current lifecycle state of the active run.

Do not derive one axis from the other.

## Committed preview rules

Only commit preview from:

- user message commits
- final assistant message commits
- terminal error outcomes

During an active run, the session-card preview should stay anchored to the latest user/queued-user message. Do not promote intermediate assistant text to the card preview just because a tool boundary closed the streaming assistant chunk; final assistant preview commits only after a terminal lifecycle event.

Do not let these override preview:

- reasoning / thinking deltas
- tool started / completed events
- command/system chatter
- partial assistant stream fragments
- subagent progress events
- other transient internal activity

If the active run is still in progress, keep the last committed preview instead of clearing it.

## Runtime status rules

Runtime status must always be one of:

- `error`
- `awaiting_user`
- `stopping`
- `running`
- `queued`
- `idle`

Priority order:

1. `error`
2. `awaiting_user`
3. `stopping`
4. `running`
5. `queued`
6. `idle`

If a run emits more reasoning, tool, or streaming activity after a partial answer, the lifecycle is still `running` until the terminal event arrives.

## Completion rules

A run is complete only when the server emits a terminal lifecycle transition:

- `run.completed`
- `run.failed`
- `abort.completed`

Partial generation, tool chatter, or command chatter does not count as completion.

## Snapshot rules

The server should publish a monotonic session-card snapshot, not raw tail reconstruction.

Recommended fields:

- `preview_message_id`
- `preview_message_role`
- `preview_message_at`
- `preview_text`
- `row_state.primary`
- `row_state.read`
- `row_state.updated_at`
- `snapshot_seq`

Client updates must only apply when the snapshot is newer than what is already rendered.

### Non-empty preview replacement rule

Once a business-visible message has been committed to a session card, the rendered preview is monotonic non-empty state:

- A non-empty preview may be replaced by a newer non-empty preview from a user or final assistant commit.
- An empty `loadSessions()`, `switchSession()`, socket-triggered refetch, local refresh, resume, or raw-tail reconstruction must not clear an already rendered non-empty preview.
- If a fresh snapshot lacks preview fields, preserve the prior rendered preview fields (`preview`, `lastMessagePreview`, role/id/time metadata) until a real replacement arrives.
- `refreshSessionPreview()`-style helpers may update on a visible-message replacement, but must be a no-op when no eligible message exists.

Practical client pattern: normalize incoming sessions, then run a helper equivalent to `preservePreviewIfReplacementEmpty(fresh, existing)` before committing rows to the store. Cover this with regression tests for empty summary/refetch snapshots, not only final assistant commits.

## UX invariants

- The second row in the session card must never disappear.
- `idle/read` should render as a neutral visible status, not as an empty row.
- `running` must not flicker away while the server still considers the run active.
- Treat the same lifecycle source that enables the Stop button as the strongest client-side evidence that the agent is still working; do not let slash-command echoes, tool chatter, partial assistant sends, or raw message-tail reconstruction reset the row to completed/idle while Stop is available.
- When the agent is still working but no longer actively thinking/streaming, prefer the latest user/queued-user preview as the stable card text until a terminal success/failure commits the final assistant/error preview.
- `stopping` must remain visible during abort windows.
- Preview and read state should be derived from the same business-visible message concept.

## Related files

- `references/session-preview-vs-runtime-state.md`
- `references/session-read-runtime-status.md`
- ADR-007 (Business-Visible Session Preview Contract)
