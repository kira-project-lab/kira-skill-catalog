# Hermes Web UI session/room deep-link routing notes

Captured from the May 2026 session deep-link implementation, clean URL migration, and follow-up architecture review.

## Product principle

For Web UI pages that show a selectable conversation-like object, the URL should be the tab-local source of truth. Shared `localStorage` can remain a fallback for legacy/default routes, but must not override an explicit id in the route. This allows multiple browser tabs to show and operate on different objects independently.

Prefer path-based canonical URLs with no `#` fragment and no `/hermes/` prefix.

## Entity boundaries

Hermes Web UI has separate entity classes:

- **Live chat sessions** from the normal chat store: `/session/:sessionId`
- **History sessions** from the Hermes/session browser, usually read-only and excluding `api_server`: `/history/:sessionId` or `/history/session/:sessionId`
- **Group chat rooms** from `gc_rooms`: `/group-chat/room/:roomId`

Group Chat internally creates bridge session ids like `gc_${roomId}_${profile}_${name}_${sessionSeed}` for individual agents. Treat those as implementation details, not user-facing room URLs.

## Clean URL migration pattern

When moving from old visible routes like `/hermes/chat` and `#/hermes/chat` to `/chat`, `/session/:id`, and `/group-chat/room/:id`, treat it as a full routing migration, not a copy-link-only change.

Key implementation files from the May 2026 migration:

- `packages/client/src/router/index.ts`
- `packages/client/src/main.ts`
- `packages/client/src/api/client.ts`
- `packages/client/src/views/LoginView.vue`
- `packages/client/src/components/hermes/chat/ChatPanel.vue`
- `packages/client/src/components/hermes/group-chat/GroupChatPanel.vue`
- `packages/client/src/components/layout/AppSidebar.vue`
- `tests/e2e/*.spec.ts`

Steps that worked:

1. Switch the Vue router to `createWebHistory()` and make top-level clean routes canonical.
2. Keep route names stable where possible (`hermes.chat`, `hermes.session`, `hermes.groupChatRoom`) so components can use named routes while paths change.
3. Add a route map for canonical paths and a catch-all legacy redirect from `/hermes/:pathMatch(.*)*` to the same path without the `/hermes` prefix.
4. In the legacy redirect, drop `#/hermes/...` hashes when redirecting `/hermes/...`; otherwise mixed links can become `/session/:id#/hermes/chat` and look only half-migrated.
5. In `main.ts`, normalize legacy hashes before app mount:
   - `/#/hermes/chat` -> `/chat`
   - `/#/hermes/session/:id` -> `/session/:id`
   - `/hermes/session/:id#/hermes/chat` -> `/session/:id`
6. For mixed path+hash deep links, preserve the path resource id over the generic hash route. Example: `/hermes/session/<id>#/hermes/chat` should become `/session/<id>`, not `/chat`.
7. Preserve auth redirects: on protected-route navigation without a token, send users to login with `?redirect=<original fullPath>`; after token/password login, return to that redirect if it is a same-origin relative path.
8. Update copy-link helpers to use `router.resolve({ name, params }).href` plus `window.location.origin`; do not manually concatenate stale `/hermes/...` prefixes.
9. Update sidebar/logo navigation to named routes instead of hard-coded strings.
10. Keep server API paths unchanged. Visible UI path migration should not rename `/api/hermes/...` endpoints.

## Live chat implementation pattern

Files involved:

- `packages/client/src/router/index.ts`
- `packages/client/src/views/hermes/ChatView.vue`
- `packages/client/src/stores/hermes/chat.ts`
- `packages/client/src/components/hermes/chat/ChatPanel.vue`
- `packages/client/src/components/layout/AppSidebar.vue`
- `tests/e2e/chat-session-multitab.spec.ts`

Key steps:

1. Add a named route for `/session/:sessionId` and point it at `ChatView.vue`.
2. In `ChatView`, read `route.params.sessionId` and pass it to the chat store so the route id is loaded before any stored fallback id.
3. In `chatStore.loadSessions`, select in this order:
   1. route/preferred session id if present in loaded sessions;
   2. current in-memory `activeSessionId`;
   3. stored localStorage active id / legacy id;
   4. latest session fallback.
4. Change session-list clicks and New Chat creation to `router.push({ name: 'session', params: { sessionId } })` instead of directly mutating store state.
5. Keep `/chat` as the general landing view if you still want an overview page; do not keep `/hermes/chat` as the canonical URL.
6. Map the session route to the sidebar's Conversation section so active-state highlighting still works.
7. Add `Copy Session Link` alongside `Copy Session ID`.

## Async/socket safety

When route changes can race with socket resume callbacks, guard callbacks by both the expected event id and the current active id before mutating active state. Prefer updating the target session object by id before assigning it active, instead of blindly mutating `activeSession.value!`.

Example guard:

```ts
if (data.session_id !== sessionId || activeSessionId.value !== sessionId) {
  resolve()
  return
}
const target = sessions.value.find(s => s.id === sessionId)
if (!target) return
// update target, then activeSession.value = target
```

## History integration recommendation

`HistoryView.vue` keeps its own local `historySessionId` / `historySession` independent from `chatStore` and loads details via `fetchHermesSession(sessionId)`. To add or maintain deep links:

1. Add `/history/:sessionId` or `/history/session/:sessionId`, depending on whether you want a flat or nested history namespace.
2. On mount and route changes, fetch that history session id.
3. If not found, fallback to the history index view.
4. On list item click, push the route instead of only setting local refs.
5. Add `Copy Session Link` for history.
6. Avoid state leaks where collapsed-group logic reads `chatStore.activeSession?.source`; it should use `historySession.value?.source` for History details.

## Group Chat integration recommendation

`GroupChatView.vue` connects to `/group-chat` and `GroupChatPanel.vue` keeps `store.currentRoomId`. The backend isolates socket events by Socket.IO room id (`socket.join(roomId)`, `this.nsp.to(roomId).emit(...)`), and the client filters events by `data.roomId === currentRoomId`.

To add room deep links:

1. Add `/group-chat/room/:roomId`.
2. In `GroupChatView` or panel, after `connect()` and `loadRooms()`, join the route room id.
3. On room click/create/clone/join-by-code, push the route instead of only calling `joinRoom`.
4. Add `Copy Room Link`.
5. Map the room route to the sidebar's Group Chat section.
6. Add e2e coverage for two tabs opening different room ids and receiving only their room's stream/status events.

## Migration test coverage

Add tests for both canonical behavior and legacy normalization:

- Direct `/session/:id` opens the selected live session and wins over shared `localStorage`.
- `/hermes/session/:id#/hermes/chat` normalizes to `/session/:id` and opens that session.
- Two tabs can show different `/session/:id` or `/group-chat/room/:id` resources after reload.
- Clicking another resource updates the URL.
- Unknown route ids fall back to the parent list route when that is the product behavior.
- Protected `/session/:id` without auth redirects to login with a `redirect=/session/:id` query and returns there after login.

When bulk-updating tests for UI paths, do not blindly replace `/hermes/` in API expectations. Runtime API endpoints intentionally remain under `/api/hermes/...`; visible browser URLs are what become clean top-level paths.

## Verification commands

Use the package manager and scripts already used by the repo. In the local Hermes Web UI fork, the May 2026 route migration was verified with:

```bash
pnpm run build
pnpm exec playwright test --project=chromium --workers=1
```

Focused checks before the broad suite:

```bash
pnpm exec playwright test tests/e2e/chat-session-multitab.spec.ts --project=chromium --workers=1
pnpm exec playwright test tests/e2e/history-session-deeplink.spec.ts tests/e2e/group-chat-room-deeplink.spec.ts --project=chromium --workers=1
```

Older notes may mention npm commands; prefer the repo's current package manager when package-lock/pnpm-lock and existing scripts indicate one.

Full suites may surface unrelated failures; separate failures caused by the route migration from pre-existing server/UI failures before reporting.
