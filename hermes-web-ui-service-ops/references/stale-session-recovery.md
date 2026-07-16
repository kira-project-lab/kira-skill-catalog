# Stale "already running" session recovery

Session-specific notes from the mpjokupykh271n investigation.

## Symptom

The UI can show `session <id> is already running` even after the underlying bridge has moved on or been restarted.

## What to check

Use the live bridge socket, not only the browser page or the DB:

- `list` shows current in-memory bridge sessions.
- `interrupt` and `destroy` only work if the bridge still knows the session.
- If they return `unknown session`, the stale lock is already gone from the live bridge.

## Safe recovery sequence

1. Query live bridge state with `list`.
2. If the session exists and is running, prefer `interrupt` first.
3. If it still remains after interrupt, use `destroy`.
4. If the session is `unknown` to the bridge but the browser still shows `already running`, treat it as stale UI state and hard-refresh / reopen the page.
5. Do **not** touch the SQLite message history for this symptom; the issue is the in-memory run lock, not the saved conversation data.

## Verification

After cleanup, the bridge should no longer list the session as running, and a fresh page load should allow a new run.
