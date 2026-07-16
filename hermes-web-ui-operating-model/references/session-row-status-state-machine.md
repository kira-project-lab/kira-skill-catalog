# Session row status state machine

Use when changing Hermes Web UI chat/session-list row status, status dots, runtime/read/unread priority, queue display, abort/approval/clarification state, or coding-agent/API/CLI run completion behavior.

## Canonical repo decision

Canonical ADR: `docs/adr/ADR-012 — Unified Session Row Status State Machine.md`.

ADR-012 tightens ADR-005 and ADR-006:

- server owns the only status resolver;
- runtime/read/outcome facts are inputs, not separate visible-status systems;
- client renders a pure projection of `session.rowState`;
- local `streaming`, `waiting`, `serverWorking`, `streamStates`, and `queueLengths` must not override `rowState.primary`;
- `row_status` is legacy compatibility and must not be a new UI source of truth.

## Priority contract

Visible primary priority:

1. `error`
2. `needs_approval`
3. `needs_clarification`
4. `stopping`
5. `running`
6. `queued`
7. `unread`
8. `idle`

Important edge cases:

- `running + queued_count > 0` renders `running`; queue count is detail, not the dominant status.
- `idle/read` and `idle/not_applicable` render no attention dot.
- A new run clears a previous terminal error.
- Read receipts affect only read/unread; they do not clear runtime, errors, approval, clarification, abort, or queue state.

## Architecture guardrails

The intended flow is:

```txt
DB facts + server runtime facts
        ↓
server status state machine / resolver
        ↓
row_state snapshot + session.row_state.changed event
        ↓
client pure projection
        ↓
one dot / label / tooltip
```

Avoid this anti-pattern:

```txt
row_state + row_status + streamStates + serverWorking + queueLengths + component priority
```

## Runtime ingestion guardrails

Every runtime producer should settle row state through one server status path:

- CLI bridge runs;
- OpenAI-compatible API runs;
- coding-agent / external runs;
- queued-run creation/cancel/dequeue;
- approval requested/resolved;
- clarification requested/resolved;
- abort started/timeout/completed;
- run completed/failed;
- session destroy/runtime reset.

Coding-agent/external-run paths are a high-risk pitfall: emitting `run.completed`/`run.failed` and clearing `sessionMap` is not enough. The row-status runtime facts must also be settled through the same resolver path so `working: true` cannot remain stuck.

## Implementation landing pattern

Prefer a small, explicit status API over ad-hoc patches:

- server status module exposes a single event ingestion entrypoint such as `applySessionRuntimeEvent(...)` and keeps legacy wrappers (for example `notifySessionRuntimeStateChanged(...)`) as thin compatibility shells;
- run paths (`run-chat/index.ts`, API run, bridge run, abort, queued/external/coding-agent terminal paths) call the event ingestion API rather than patching runtime fields independently;
- client components should import a pure projection helper (for example `projectSessionRowDot(...)`) and avoid re-implementing the priority tree inside the Vue component;
- if `rowState` is absent, a narrow local runtime fallback (`streaming` / `waiting`) is acceptable for backward compatibility, but it must never win over a present server row state.

Testing pitfall: server status modules may import user-presence helpers such as `listUsers()`. Unit tests for status transitions often mock surrounding stores narrowly; make presence/user listing defensive or ensure tests mock it explicitly, otherwise unrelated mock-export failures can hide the status-machine regression being tested.

## Tests to require

Server:

- priority matrix for all primary states;
- new run clears previous error;
- completion with queue remains running;
- completion without queue falls back to unread/read/idle;
- API, CLI bridge, and coding-agent terminal events settle through the unified status service.

Client:

- `SessionListItem` uses `rowState` when present;
- local `streaming` does not override `error`, `needs_approval`, `needs_clarification`, or `stopping`;
- local `waiting` does not override `running`;
- `primary=running` with queue detail renders running;
- `primary=idle` renders no dot;
- rendered dots have localized accessible labels.
