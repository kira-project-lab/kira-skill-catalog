# New Chat creation flow

## Current implementation

`New Chat` is not a server-side dialog creation API flow. In the client store, `chatStore.newChat()` creates a local session object, inserts it into the sessions list, and immediately switches to it.

### Desktop

- Entry point: `ChatPanel.vue` session-pane toolbar button.
- UX: opens a modal first.
- Modal collects:
  - profile
  - provider
  - model
- Confirm path:
  - `chatStore.newChat({ profile, provider, model })`
  - `router.push({ name: 'hermes.session', params: { sessionId } })`
  - close modal
  - focus composer

### Mobile drawer

- Entry point: `ChatSessionDrawerPane.vue`.
- UX: direct create, no modal.
- Flow:
  - `chatStore.newChat()`
  - close mobile overlays
  - navigate to the new session

### Keyboard shortcut

- `Cmd/Ctrl+N` invokes `chatStore.newChat()` directly.
- It does not open the desktop modal.

## Important UX contract

- Desktop is the only path that asks for model/profile/provider before the session is opened.
- Mobile and keyboard are instant-create shortcuts.
- The visible title begins as the generic new-chat label until the session receives a real title.

## Pitfalls

- Do not describe this as a server-created dialog object; the primary UX is client-created session state.
- Do not assume all entry points share the modal flow; they intentionally do not.
- If you change the modal flow, keep the composer-focus behavior after navigation.
