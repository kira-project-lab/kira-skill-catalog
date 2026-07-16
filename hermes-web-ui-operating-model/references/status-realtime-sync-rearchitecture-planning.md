# Status realtime sync rearchitecture planning

Use when Maxim reports chat/session status dots are stale, delayed, inconsistent across tabs/windows, or require reload.

## Product bar

The target is not “mostly updates eventually.” The user-visible contract is:

> In any open tab/window/device, status indicators should converge to the current server truth without manual reload.

Connected visible tabs should update near-instantly; disconnected/hidden tabs must catch up on reconnect or visibility return.

## Planning pattern that worked

For this class of issue, do not jump straight into component fixes. Start with a deep plan containing four tracks:

1. **Best-practices research**
   - Socket.IO missed-event/reconnect guarantees.
   - Server-authoritative client cache invalidation patterns, e.g. TanStack Query/SWR/Apollo/Firebase/Supabase.
   - BroadcastChannel/localStorage cross-tab limitations.
   - Page Visibility/focus/read-receipt semantics.
   - Monotonic versioning/snapshot/event-log patterns.
2. **Current architecture audit**
   - Server resolver and event ingestion: `packages/server/src/services/hermes/session-row-status.ts`.
   - Socket namespace: `packages/server/src/services/hermes/session-status-events.ts`.
   - Client socket subscription: `packages/client/src/api/hermes/session-status-events.ts`.
   - Cross-tab local invalidation: `packages/client/src/utils/session-sync.ts`.
   - Store merge/race logic: `packages/client/src/stores/hermes/chat.ts`.
   - Dot projection/rendering: `packages/client/src/shared/session-row-state.ts`, `SessionListItem.vue`.
   - Read receipts: `session-read-receipt.ts` and server receipt store/routes.
3. **Architecture decision before implementation**
   - Keep server as source of truth.
   - Prefer versioned server row snapshots plus bounded catch-up/refetch on socket reconnect/visibility.
   - Treat BroadcastChannel as same-browser acceleration/invalidation only, not as source of truth.
   - Apply snapshots atomically and only if newer than the currently rendered snapshot.
4. **TDD + browser QA implementation plan**
   - Failing tests for reconnect catch-up, hidden-tab visibility catch-up, stale async REST response races, same-millisecond monotonic versioning, read-receipt sync, and socket-vs-BroadcastChannel responsibility boundaries.
   - Browser QA with two tabs/pages: running appears in both, completion clears in both, read receipt clears unread in the other tab, reconnect/visibility catches up.

## Likely target architecture

```txt
Server status facts
  -> server snapshot resolver with durable monotonic version
  -> sessions REST returns same latest snapshot
  -> socket emits row snapshot/status changed with version
  -> client status-sync service applies only newer snapshots or refetches
  -> SessionListItem renders pure projection
```

Default MVP: monotonic server snapshots + reconnect/visibility refetch + strict client merge. Escalate to durable event-log cursor replay only if tests prove snapshot catch-up is insufficient.

## High-risk pitfalls

- Timestamp-only `snapshot_seq` is not enough if two updates happen in the same millisecond or after process restart. Prefer durable monotonic version per `(user, profile, sessionId)`.
- Do not let an older REST `fetchSession()` response overwrite a newer socket status. All status/preview fields need version-aware atomic merge.
- Do not let `streamStates`, `serverWorking`, `queueLengths`, `streaming`, or `waiting` override present server `rowState`; they are fallback/non-status UI only.
- Do not make BroadcastChannel carry trusted full state. Same-browser tabs are not the source of truth and cannot help cross-device windows.
- Read receipt client/server “latest relevant message” roles must match; otherwise dots will look stale or wrong even if transport is correct.
- Visibility refresh should refresh session-row status/list truth, not only active transcript messages.

## Research deliverable shape

Save research under `.hermes/research/YYYY-MM-DD-status-realtime-sync-best-practices.md` with:

- verdict;
- source table with at least 10 qualifying sources;
- comparison matrix: full snapshot vs invalidation+refetch vs deltas vs event-log cursor vs BroadcastChannel mirroring;
- recommended Hermes architecture;
- anti-patterns;
- validation checklist.

## Implemented MVP pattern (2026-06-19)

The first shipped Hermes Web UI implementation uses:

- `session_row_versions` SQLite table for durable monotonic per `(user_id, profile_name, session_id)` versions.
- `row_state.version` and compatibility `row_state.snapshot_seq` set to the same server-authored version on every status-affecting emission.
- `packages/server/src/db/hermes/session-row-versions-store.ts` for bump/read helpers.
- `packages/client/src/stores/hermes/session-row-sync.ts` for version extraction, strict `>` apply decisions, and catch-up deduping.
- `/session-status` socket lifecycle hooks (`onConnect`, `onReconnect`) to trigger session-list catch-up.
- `document.visibilitychange` to trigger status catch-up when a tab returns to foreground.
- BroadcastChannel remains invalidation-only; it calls the same catch-up/refetch path rather than carrying trusted row state.
- Read targets remain visible final assistant messages only; tool/command messages can invalidate status but are not durable read receipt targets.

Key tests added/updated:

- `tests/server/session-row-status.test.ts` for same-millisecond monotonic runtime versions and read-receipt versioned emissions.
- `tests/client/session-row-sync.test.ts` for strict version apply rules.
- `tests/client/chat-store-session-sync.test.ts` for socket reconnect catch-up and visibility-return catch-up.

## Implementation validation gate

Do not report this class of fix complete until:

- REST and socket expose the same latest status snapshot/version;
- client ignores stale REST/socket responses;
- reconnect and visibility return trigger catch-up;
- two-tab browser QA proves running/completed/unread/read transitions without reload;
- focused client/server tests and build pass;
- ADR/docs are updated with the final sync contract.
