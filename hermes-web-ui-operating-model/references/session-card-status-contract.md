# Session Card Status Contract

Use this reference when implementing or reviewing the Hermes Web UI session-card row. It records the product contract learned from the preview/status race work.

## Contract summary

A session card has **two separate axes**:

1. **Preview** — the last committed business-visible message.
2. **Status** — the current lifecycle state of the run.

Do not let technical chatter decide either axis.

## Preview rules

Preview may change only on:

- committed user message
- committed final assistant message
- terminal error / failure message when that is the final outcome

Preview must **not** change on:

- `thinking.delta`
- `reasoning.delta`
- `tool.started`
- `tool.completed`
- `/command` or other technical/system chatter
- partial assistant streaming fragments that are not yet committed

If a run is still active and no new committed business-visible message exists, keep the last committed preview instead of rendering an empty second line.

## Status rules

The card must always show a visible status, including the idle/complete case.

Suggested precedence:

1. `error`
2. `awaiting_user` (`approval` / `clarify`)
3. `stopping`
4. `running`
5. `queued`
6. `idle` / `read` fallback

Status is a lifecycle indicator, not a preview label.

## Runtime events vs preview events

Runtime events that only affect status:

- `run.started` → `running`
- `reasoning.delta` / `thinking.delta` → remain `running`
- `tool.started` / `tool.completed` → remain `running` unless a terminal request-required state exists
- `approval.requested` / `clarify.requested` → `awaiting_user`
- `abort.started` → `stopping`
- `abort.completed` → `idle` or `queued` depending on queue state
- `run.completed` → `idle`
- `run.failed` → `error`

Preview events are only those that commit visible content.

## Merge and freshness rules

The client must not blindly replace a stronger, already-committed card snapshot with a weaker transitional one.

Use monotonic merge guards:

- prefer newer server snapshots over older ones
- do not wipe a non-empty committed preview with an empty transitional preview
- do not downgrade a stronger status with stale refetch data

This matters most during:

- rapid send → stop
- reconnect/resume
- websocket replay after page visibility changes
- server refetch arriving after local live state

## Common failure modes

- Preview goes blank while the agent is still thinking.
- `running` disappears because the client briefly trusts a stale server snapshot.
- A tool or reasoning fragment becomes the visible preview.
- A completed run looks “done” but the row has no visible status.

## Implementation note

The session-card row should be rendered from a server-authoritative snapshot and updated by live events only when they improve or advance that snapshot. Transcript noise may remain in the message stream, but it must not become the card contract.
