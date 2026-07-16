# New Chat Option Availability

This note captures when the Hermes Web UI new-chat surface does and does not expose model/provider controls.

## What the UI does today

- **Desktop New Chat drawer** (`ChatPanel.vue`) opens a drawer with `profile`, `provider`, `model`, and `workspace` fields when the chosen agent/runtime uses provider-backed models.
- **Mobile New Chat** (`ChatSessionDrawerPane.vue`) and **`Cmd/Ctrl+N`** (`useKeyboard.ts`) go directly to `chatStore.startDraftChat()` and route to `hermes.chat`; they do **not** open the full model picker UI.
- **Global coding-agent mode** intentionally hides `provider` and `model` fields. That is expected behavior, not a broken selector.

## Diagnosis order when a user says “I can’t choose model/options”

1. Identify the entrypoint they used: desktop drawer, mobile action, or keyboard shortcut. If they attached a screenshot, inspect whether labels are present but controls are absent.
2. Check whether the new chat is in **Hermes** vs **coding-agent** mode, and whether coding-agent mode is **global**.
3. If the desktop drawer shows only labels such as `Agent`, `Profiles`, `Provider`, or `Models` but no controls, first verify `ChatPanel.vue` imports every Naive UI component it uses in the template. A missing `NSelect` import can make all select controls vanish while imported adjacent controls such as `FolderPicker`/`NInput` still render.
4. If the select controls render but are empty/disabled, confirm the profile has selectable model groups loaded from the app store.
5. Verify the relevant source paths rather than assuming the picker is broken:
   - `packages/client/src/components/hermes/chat/ChatPanel.vue`
   - `packages/client/src/components/layout/mobile/ChatSessionDrawerPane.vue`
   - `packages/client/src/composables/useKeyboard.ts`
   - `packages/client/src/composables/model-selection.ts`

## Regression contract for vanished select controls

When fixing a missing-control issue in the desktop New Chat drawer, add or update a focused raw-source test (for example `tests/client/chat-draft-session-flow.test.ts`) that asserts both:

```ts
expect(chatPanelSource).toMatch(/import \{[\s\S]*\bNSelect\b[\s\S]*\} from "naive-ui"/)
expect(chatPanelSource).toContain('<NSelect')
```

This protects the actual failure mode: template usage of a component without the corresponding import.
## Fast mental model

- **Draft creation** does not always imply **model selection UI**.
- **Provider/model fields** are only part of the desktop drawer flow and only when the runtime expects them.
- If the user chose a global coding agent, the absence of provider/model fields is the intended UX.
