# Session Card Committed Snapshot Contract

Use this reference when Hermes Web UI session rows flicker, preview text changes during active agent work, status dots disagree with the Stop button, or refetch/socket events race.

Canonical repo ADR: `docs/adr/ADR-008 — Committed Session Card Snapshot Contract.md`.

## Core rule

Session list rows should render one server-authored committed snapshot, not independently derive preview, runtime state, and read/unread on the client.

During an active run, the session card preview stays on the latest user-submitted message. Final assistant output is committed to the card only after terminal success.

## Active run definition

Treat a session as active when any of these are true:

- `working === true`
- `queued_count > 0`
- `approval_pending === true`
- `clarification_pending === true`
- `aborting === true`

While active, card preview priority is:

1. latest queued user message not yet persisted;
2. latest persisted user message;
3. previous committed idle business-visible preview;
4. empty.

Do not advance the card preview from:

- reasoning/thinking deltas;
- partial `message.delta` assistant output;
- assistant text closed by tool boundary;
- `tool.*` events;
- `subagent.*` events;
- `agent.event` or `session.command` telemetry;
- compression/title-generation events;
- approval/clarification prompt metadata.

## Terminal rules

- Terminal success: commit final non-empty assistant answer as preview and read target.
- Terminal failure: `error` status wins; use terminal error preview only if it is the final user-facing outcome.
- Abort: show `stopping` while aborting and keep latest user preview. After abort, follow queued/idle/error terminal state.

## Status priority

Use one dominant row state:

1. `error`
2. `needs_approval`
3. `needs_clarification`
4. `stopping`
5. `running`
6. `queued`
7. `unread`
8. `idle`

Unread is a read-state overlay after terminal/idle agent output; it must not hide active runtime states.

## Ordering guard

Every row snapshot should carry a monotonic `snapshot_seq` scoped by `(profile, session_id)`. Apply socket or REST snapshots only if newer than the current local snapshot. REST refetch must not overwrite a newer socket snapshot, and socket replay must not overwrite a newer REST snapshot.

## Implementation guidance

- Keep current `row_state` as compatibility while adding the richer card snapshot.
- Make `row_state` derivable from the snapshot.
- Move session list rendering to snapshot preview/runtime/read fields.
- Keep raw transcript rendering separate from card preview semantics.
- Use client optimistic state only before server confirmation and never over a newer snapshot.
- Replace row usage of client `refreshSessionPreview()`; leave it only for transcript/local optimistic display if needed.

## Test matrix

Cover at least:

- reasoning-only active run keeps latest user preview;
- partial assistant delta keeps latest user preview while active;
- tool boundary does not commit assistant partial as preview;
- tool/subagent/command/compression/title events do not advance preview;
- approval/clarification show request status with latest user preview;
- abort shows stopping with latest user preview;
- queued user message becomes preview before persistence;
- final assistant answer becomes preview after terminal success;
- terminal error status wins over unread;
- stale socket/refetch snapshots cannot overwrite newer state;
- Stop button and row runtime agree on active/idle transitions.
