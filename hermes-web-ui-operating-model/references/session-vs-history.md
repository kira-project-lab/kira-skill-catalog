# Session vs History

## Purpose
Explain why Hermes Web UI can show a large number of sessions, and how the Chat/History surfaces relate to the same underlying records.

## Core rule
**History is a projection of sessions, not a separate data type.**

A session is the persisted conversation record. The history view is just another way to list and label those same session records.

## Where the UI reads from

- `packages/client/src/components/hermes/chat/ChatPanel.vue`
  - shows the active, working session list from the chat store.
- `packages/client/src/views/hermes/HistoryView.vue`
  - loads Hermes sessions with `fetchHermesSessions(...)`.
  - derives history status with `getHistorySessionStatus(...)`.
- `packages/client/src/shared/session-display.ts`
  - `getHistorySessionStatus()` labels a session as `completed` when `endedAt` exists, otherwise `archived`.

## Why there are so many sessions

Common reasons sessions accumulate:

- each new chat/run/thread is a separate persisted session;
- imports create additional session records;
- the default session listing path is intentionally broad (`limit = 2000` in the DB list helper);
- the UI does not auto-merge or auto-prune old sessions.

## How to explain the difference

When answering users:

- say **session** when referring to the underlying record or live conversation thread;
- say **history** when referring to the archive/listing view over those records;
- avoid implying data is moved between two stores;
- be explicit that a session can still appear in history even if it is not active.

## Useful phrasing

- “History is the archive view of the same sessions.”
- “A session is the stored conversation; history is how we browse stored sessions.”
- “Nothing is transferred from sessions to history — the same record is shown in a different UI.”

## Related files

- `packages/client/src/views/hermes/HistoryView.vue`
- `packages/client/src/components/hermes/chat/ChatPanel.vue`
- `packages/client/src/shared/session-display.ts`
- `packages/server/src/db/hermes/session-store.ts`
