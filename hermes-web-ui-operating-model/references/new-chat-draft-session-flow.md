# New chat draft-to-session flow

## Why this matters

For UX that begins with an empty composer, creating a persistent session record too early makes the session list noisy and can imply a completed conversation before the user has typed anything.

## Recommended pattern

- Keep a temporary **draft** state for the selected profile/provider/model, composer text, and pre-send attachments.
- Do **not** insert a persistent session row until the first meaningful send.
- Materialize the session at first send, then route into `hermes.session/:sessionId` and focus the composer / conversation view as needed.
- If the draft is abandoned, discard it without creating history clutter.

## When to use

Use this pattern when a new chat flow would otherwise create blank rows, blank titles, or placeholder sessions that the user may never use.

## Pitfalls

- Do not treat the draft shell as the canonical session record.
- Do not require a session id just to let the user start typing.
- Do not forget to preserve the selected model/profile/provider across draft finalization.
- Do not create a second session when the first send happens; finalization should upgrade the draft, not duplicate it.
- If the implementation changes the route shape, session list visibility, or composer focus behavior, update those contracts together.
- If the existing composer persists unsent text by `activeSessionId`, add the draft id as an allowed draft-storage key while the session is not materialized, then explicitly clear that draft key after first-send route replacement. Otherwise draft text can be lost before send or left behind under a `draft_*` key.
- When `newChat()` changes from returning a materialized `Session` to starting a draft, update older tests and call sites that mutate the returned session directly. For tests that need an existing session, insert one through `addOrUpdateSession()` / active-session setup instead of calling `newChat()`.
- For first-send route promotion, prefer returning a narrow result such as `{ sessionId, materializedFromDraft }` from `sendMessage()` and use `router.replace(...)`, not `push`, so Back does not reopen a dead draft route.
