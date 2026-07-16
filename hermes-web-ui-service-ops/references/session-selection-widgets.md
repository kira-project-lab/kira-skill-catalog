# Hermes Web UI session selection widgets

Use this note when a user asks which control opens the current-session list or how session picking works in the Web UI.

## Current chat view

- The **toggle button** that opens/closes the current session list in `ChatPanel.vue` is a **`NButton`** in the chat header.
- It flips the local `showSessions` state: `@click="showSessions = !showSessions"`.
- This header `NButton` is only the list toggle; it is not a per-session navigation/link control.
- The actual list entries are rendered with **`SessionListItem`**.
- `SessionListItem.vue` currently renders each row as a native `<button class="session-item">`, emits `select` from `@click`, and the parent routes with `router.push({ name: 'hermes.session', params: { id: sessionId } })`.
- Because the session row is a `<button>` with programmatic Vue Router navigation rather than an `<a href="/session/:id">`/`RouterLink` anchor, browser middle-click / Ctrl-click cannot use the native “open in new tab/window” behavior. To support that UX, give the row a real `href` (for example via `router.resolve(...)`) or render it as a `RouterLink custom`/anchor while preserving context-menu/delete interactions.

## Session search modal

- The keyboard/search-based session picker is **`SessionSearchModal.vue`**.
- Visibility is driven by the shared composable **`useSessionSearch()`** and its `sessionSearchOpen` ref.
- It renders inside an **`NModal`** and opens recent sessions when shown.
- Choosing an item calls `chatStore.switchSession(item.id, messageId)` and then routes to `hermes.chat` if needed.

## Useful file anchors

- `packages/client/src/components/hermes/chat/ChatPanel.vue`
- `packages/client/src/components/hermes/chat/SessionListItem.vue`
- `packages/client/src/components/hermes/chat/SessionSearchModal.vue`
- `packages/client/src/composables/useSessionSearch.ts`
