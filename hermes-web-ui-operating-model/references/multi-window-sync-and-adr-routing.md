# Hermes Web UI: multi-window sync and ADR routing

## What changed in this session

- The canonical ADR location for Hermes Web UI work is the repo `docs/adr/` directory.
- Active Obsidian ADR notes for this project were treated as archival/reference material, not the source of truth.
- The multi-window/session-status sync implementation should use event-driven invalidation, not mirrored mutable state.

## Durable implementation pattern for multi-window sync

Use this pattern when adding or reviewing cross-tab behavior:

1. **Server remains source of truth** for session list and status-bearing fields.
2. **Per-session live updates stay socket-room scoped** so the active session can keep streaming normally.
3. **Cross-tab signals are for invalidation/refetch**, not for replicating the entire store across windows.
4. **BroadcastChannel with `storage` fallback** is enough for signaling create/delete/rename/update/status-change events.
5. **Keep active session and local UI state tab-local**; do not force all tabs to mirror the same active session.
6. **Broadcast on state transitions that change shared truth**:
   - session create/delete/rename
   - workspace/model changes that affect session list presentation
   - run/approval/clarify/abort/compression lifecycle transitions that affect visible status

## Verification pattern used here

- Add a focused client test for incoming/outgoing sync signals.
- Verify the targeted Vitest suite first.
- Finish with a repo build so the change is validated end-to-end.

## Notes

- This is a session-specific knowledge bank for Hermes Web UI work.
- Keep the repo docs canonical; use Obsidian for broader context and archive history only.
