# Session list pagination + deep-link QA

Use when verifying that Hermes Web UI session-list pagination did not break direct links to sessions.

## Scope

Covers both:

- chat deep links: `/#/hermes/session/:sessionId?profile=<profile>`;
- history deep links: `/#/hermes/history/session/:sessionId?profile=<profile>`.

Hermes Web UI currently uses `createWebHashHistory()`, so the canonical browser URL includes `/#/...`. A plain path like `/hermes/session/...` is not equivalent unless the app/router mode changes.

## Probe pattern

1. Verify live-dev/prod runtime identity first (`/health`, branch/commit/service).
2. Use a profile that has more sessions than one page; otherwise pagination cannot be validated.
3. Confirm the first page request shape in the browser/API:
   - history: `/api/hermes/sessions/hermes?limit=25&profile=<profile>`;
   - chat: `/api/hermes/sessions?limit=25&profile=<profile>`.
4. Trigger `Load more sessions` and confirm the next request includes the offset, e.g. `offset=25`.
5. Pick a session from a later page and open its direct hash link in a fresh navigation:
   - history: `/#/hermes/history/session/<id>?profile=<profile>`;
   - chat: `/#/hermes/session/<id>?profile=<profile>`.
6. Confirm the session opens even if it was not present in the initial page. Strong evidence:
   - route remains on the requested session URL;
   - title/body contains the requested session content;
   - message endpoint was called, e.g. `/api/hermes/sessions/conversations/<id>/messages/paginated?...&profile=<profile>`.
7. Check browser console errors after the direct navigation.

## Source contract to inspect

- `packages/client/src/stores/hermes/chat.ts`: `loadSessions(profile, preferredSessionId, append)` should fetch `preferredSessionId` directly when it is absent from the current page, then unshift it into the list.
- `packages/client/src/views/hermes/HistoryView.vue`: direct history route should call `loadHistorySession(sessionId, profile)` and add the summary to the list if missing.
- `packages/client/src/router/index.ts`: route mode and paths define whether links need `/#/...`.

## Auth note for browser QA

Modern Web UI API auth uses user JWTs for most protected endpoints. The legacy server `.token` is not sufficient for ordinary `/api/hermes/*` probes except narrow server-token media paths. If password login is unavailable during local QA, generate/use a valid user JWT for the browser session rather than concluding the API is broken.

For pagination/deep-link QA, a code-contract inspection alone is only a preliminary answer. Strong evidence requires an authenticated browser/API probe with a real user JWT: first-page list, `offset=25` list, and direct `/#/.../session/<id>?profile=<profile>` navigation to a later-page session. If auth blocks the probe, report the result as preliminary and name auth as the verification gap; do not claim the live browser/API path is fully verified.

Do not persist generated JWTs or credentials in notes or skills.
