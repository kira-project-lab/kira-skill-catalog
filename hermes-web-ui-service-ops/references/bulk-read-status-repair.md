# Bulk read-status repair / backfill

Use this when a bad deploy or schema regression marks many Hermes sessions unread and the user explicitly wants a one-time administrative repair.

## Scope

- Target the live Web UI SQLite DB only after verifying the active service, checkout, and state directory.
- Repair read state per `(user_id, profile_name, session_id)` by setting each session to its current latest agent-output message.
- Skip sessions with no agent-output messages (`assistant`, `tool`, `command`).
- Only touch the intended user/profile rows; do not rewrite other users' state.

## Safe repair pattern

1. Confirm the live service and state path.
2. Inspect `sessions`, `messages`, and `user_session_read_state` counts for the intended user/profile.
3. For each session with agent output, upsert `user_session_read_state` so `last_read_message_id` matches the latest agent-output message id and `read_at`/timestamps use a single repair timestamp.
4. Recompute the target user's read/unread totals from the DB and verify the unread count dropped as expected.
5. If new messages may still be arriving, expect some sessions to become unread again immediately; rerun only if the user wants the latest state normalized.

## Verification queries

```sql
SELECT COUNT(*) FROM user_session_read_state WHERE user_id = ?;
SELECT COUNT(*) FROM sessions;
SELECT COUNT(*) FROM messages;
SELECT id, profile FROM sessions;
SELECT id, timestamp
FROM messages
WHERE session_id = ? AND role IN ('assistant', 'tool', 'command')
ORDER BY timestamp DESC, id DESC
LIMIT 1;
```

## Pitfalls

- Do not try to fake a browser-visible read receipt when the goal is mass remediation; that is the wrong tool for a bulk repair.
- Do not include user-only sessions; they are not unread by this contract.
- Do not interpret a single repair pass as permanent if assistants are still posting messages.
