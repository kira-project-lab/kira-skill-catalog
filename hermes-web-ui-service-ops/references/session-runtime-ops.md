# Session runtime ops

Use for a specific Hermes Web UI chat session that must be inspected, recovered, resumed, compressed, or verified across UI, API, Socket.IO, bridge run state, and persistence.

## Scope

Covers:

- session id extraction from UI routes/links;
- profile/auth/JWT pairing;
- API/session metadata lookup;
- SQLite persistence checks;
- Socket.IO `/chat-run` command flow;
- stuck `already running` lifecycle state;
- `/compress` and compression snapshot verification;
- cases where UI route state differs from persisted session history.

## Mental model

Keep four layers separate:

1. **UI route/client state** — selected/open session, stale browser state, localStorage.
2. **Persisted history** — SQLite session row/messages/snapshots.
3. **Live run state** — bridge/session manager in memory.
4. **Compression state** — runtime event completed vs persisted snapshot usable for the next turn.

A session can have valid history while its live run state is gone, stale, blocked, or still active.

## Baseline workflow

1. **Identify profile and session id**
   - Confirm active Hermes profile.
   - Extract session id from `/session/:id`, History, Group Chat, or copied link.
   - Verify the user/profile/JWT pairing before protected API calls.

2. **Read persisted session state first**
   - Fetch session metadata through the Web UI API when possible.
   - Check concrete fields: message count, `ended_at`, provider, model, token usage, updated time.
   - If API is ambiguous, inspect SQLite only after confirming the DB path from service environment.

3. **Separate route issue from data issue**
   - A redirect to a generic chat route does not prove the session is missing.
   - Browser state/cache/localStorage can mask the real persisted session.
   - Reopen or hard-refresh before changing backend state.

4. **Check live run state**
   - If UI says `already running`, confirm whether the bridge still considers the session active.
   - If work is live, wait or interrupt cleanly.
   - If the bridge says unknown session, do not edit message history; stale browser state is likely.

5. **Use app command paths**
   - Trigger interrupt/destroy/compress through the Web UI/bridge control path, not by manual DB edits.
   - Observe socket events when possible (`compression.started`, `compression.completed`, run status changes).

6. **Verify compression persistence**
   - A runtime `compression.completed` event is not enough.
   - Re-read session metadata/message counts/token counts.
   - Check that a compression snapshot row exists and that `snapshot.lastMessageIndex` is near the current message count.
   - If the next turn re-expands context, look for stale snapshot fallback or post-compression abort.

## Pitfalls

- Missing auth or wrong profile often looks like generic `401 Unauthorized`.
- A successful runtime compression may not advance the persisted snapshot enough for the next turn.
- Usage counters may lag if API and event stream read different sources.
- Session lifecycle locks are in-memory run state, not history corruption.
- Do not delete or edit messages to clear a live-run lock.

## Verification checklist

- Correct profile/session id confirmed.
- Session metadata fetched through API or verified DB path.
- UI route state separated from persisted data.
- Live bridge/run state checked.
- Recovery command used the app/bridge path.
- Compression snapshot verified if compression was involved.
- Browser reopened/refreshed if client state could be stale.

## Related references

- `session-compression-example.md`
- `session-already-running.md`
- `stale-session-recovery.md`
- `session-deep-links-routing.md`
- `session-attention-states.md`
