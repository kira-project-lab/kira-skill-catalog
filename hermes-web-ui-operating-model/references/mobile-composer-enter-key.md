# Mobile composer Enter key contract

Use when changing Hermes Web UI chat composer keyboard behavior or reconciling mobile/desktop composer parity.

## Contract

- Desktop chat composer: bare `Enter` sends, `Shift+Enter` inserts a newline.
- Mobile chat composer: bare `Enter` is the soft-keyboard newline key and must not send. Let the textarea's native behavior insert a newline.
- Keep slash-command / mention dropdown selection behavior intact: when a command/mention popup is active, `Enter` may still choose the active item because the user is interacting with the popup, not inserting text.

## Implementation pattern

- Distinguish **mobile input device** from **narrow viewport**. A half-width desktop window must still submit on bare `Enter`; a real mobile/touch-soft-keyboard device must insert a newline.
- Use or add a shared helper such as `isMobileInputDevice()` in `@/composables/useMobileLayout`:
  - check mobile user agents (`Android|iPhone|iPad|iPod|Mobile`), and
  - fall back to touch/coarse-pointer signals when UA is not enough.
- In `ChatInput.vue`, after `if (e.key !== 'Enter' || e.shiftKey) return`, return early for `isImeEnter(e) || isMobileInputDevice()` before `preventDefault()` / `handleComposerAction()`.
- In `GroupChatInput.vue`, apply the same device-mobile guard before `preventDefault()` / `handleSend()`.
- Do not use viewport width alone (`isMobileViewport()`) for this behavior unless the user explicitly asks for width-based behavior; it regresses narrow desktop windows.
- Do not add a separate mobile send shortcut unless the UX explicitly asks for it; the visible Send button remains the mobile send path.

## Tests

Add/keep focused jsdom tests for both surfaces:

- Desktop-narrow case: stub a desktop UA with a small viewport width (for example 600px) and assert bare `Enter` submits / triggers send.
- Mobile-device case: stub an iPhone/Android UA or coarse-pointer/touch capability and assert bare `Enter` does not submit and the textarea can keep the native newline.
- Include both ordinary `ChatInput.vue` and `GroupChatInput.vue` when both expose the same text-entry behavior.
- Run the focused tests first and watch them fail before production code changes when fixing this class of bug.

## Verification

- `npm run test -- tests/client/chat-input-draft.test.ts tests/client/group-chat-input-mentions.test.ts`
- `npm run build`
- For live-dev, push `dev`, restart `hermes-web-ui-dev.service`, verify public `/health` reports the pushed commit, and check served source contains the mobile guard.