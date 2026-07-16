# Obsidian-like workspace shell for Hermes Web UI

Use when Maxim compares Hermes Web UI to Obsidian, asks for docked panes/toolbars/workspace redesign, or wants a UI ADR/spec for agent workspace IA.

## Core product model

Do not copy Obsidian's file-tree domain. Transfer the workspace mechanics:

```text
AppShell
  ActivityRail
  DockPane(left: Sessions)
  WorkspacePane(center: Active session / agent work surface)
  DockPane(right: Inspector, optional)
  StatusBar(bottom)
```

Every pane should follow:

```text
PaneHeader
PaneToolbar
PaneBody
PaneFooter
```

## Design judgment

Hermes should read as an **agent workspace**, not a chat page or dashboard. The semantic difference is:

- app navigation becomes a compact activity rail;
- sessions become a docked pane with toolbar actions;
- the active chat becomes the central workspace pane;
- drawer/outline/files/tools become right docked inspector modes;
- runtime state belongs in the workspace header/status bar and detailed Run inspector;
- large action cards like `Search` / `New Chat` should become pane-toolbar controls.

## Four-phase ADR shape

When asked to document this direction, create a repo ADR with these phase boundaries:

1. **Workspace shell and left dock** — activity rail, Sessions dock, pane toolbar, chat workspace header, docked composer.
2. **Right docked inspector** — replace temporary drawer behavior with docked Outline / Files / Run / Tools modes, collapsible and resizable.
3. **Agent run surface and status system** — make Stop availability, running state, row state, previews, approvals/clarifies, and terminal output one truthful projection of server/runtime state.
4. **Tabs, splits, persisted layout** — optional active workspace tabs/splits, persisted as Web UI layout state rather than Hermes Agent runtime state.

## Component inventory to include

- `packages/client/src/components/layout/AppSidebar.vue`
- `packages/client/src/components/hermes/chat/ChatPanel.vue`
- `packages/client/src/components/hermes/chat/SessionListItem.vue`
- `packages/client/src/components/hermes/chat/ChatInput.vue`
- `packages/client/src/components/hermes/chat/SessionSearchModal.vue`
- `packages/client/src/components/hermes/chat/DrawerPanel.vue`
- `packages/client/src/components/hermes/chat/OutlinePanel.vue`
- `packages/client/src/components/hermes/chat/FilesPanel.vue`
- `packages/client/src/components/hermes/chat/TerminalPanel.vue`
- `packages/client/src/components/hermes/chat/ConversationMonitorPane.vue`
- `packages/client/src/components/hermes/chat/MessageList.vue`
- `packages/client/src/components/hermes/chat/VirtualMessageList.vue`
- `packages/client/src/components/hermes/chat/MessageItem.vue`
- `packages/client/src/components/hermes/chat/MarkdownRenderer.vue`
- `packages/client/src/stores/hermes/app.ts`
- `packages/client/src/stores/hermes/chat.ts`
- `packages/client/src/services/hermes-api.ts`
- server session/runtime/socket controllers and services that expose row/run state
- `packages/client/src/styles/variables.scss`
- locale files under `packages/client/src/i18n/`
- focused client source-contract tests and e2e layout tests

## Implementation pass checklist

When Maxim asks to fully implement an Obsidian-like workspace ADR, treat it as a visible shell migration, not a color/layout polish pass:

1. Add a focused source-contract test first and watch it fail. Assert the ADR status, activity rail selector/token, session dock pane/header/toolbar, workspace pane header/body/footer/statusbar, docked inspector modes, and absence of launcher-card/overlay-drawer selectors.
2. Convert the app sidebar to a true activity rail by using a semantic token such as `$activity-rail-width` and an explicit `activity-rail` class/ARIA label; keep expanded mode available only if the existing product still needs it.
3. Replace session launcher cards with a `Sessions` dock pane header and compact toolbar buttons. Preserve search/new-chat behavior, tooltips, accessible labels, modal focus handoff, session resize, pinned order, unread/runtime row state, and context menu behavior.
4. Wrap the chat center as a `WorkspacePane`: `pane-header` for the active session, `pane-body` for messages, `pane-footer` for a docked composer, and a quiet bottom status bar for connection/profile/model/run basics.
5. Convert durable desktop drawer content into a right `inspector-dock`. Use modes such as `outline`, `files`, `terminal`, and `run`; header buttons toggle the selected mode. On mobile, overlay presentation is acceptable only as the responsive form of the same dock contract.
6. Simplify `DrawerPanel` from a body-level Teleport/overlay into a docked content component when it is mounted inside the inspector. Remove `drawer-overlay` and fixed-position panel CSS for the desktop dock path.
7. Update stale tests that explicitly expected the old launcher cards or `showDrawer = true`; they should now protect pane toolbar and inspector toggles instead.
8. Add any new user-facing strings, such as a `Run` inspector label, to every locale file.
9. Verify with the focused ADR test, nearby session/design-token tests, `npm run build`, `git diff --check`, live-dev `/health`, and served-source checks for the new selectors and removed overlay selectors.


## Non-goals / pitfalls

- Do not implement split panes first; stabilize the pane contract first.
- Do not add toolbar icon noise without the pane model.
- Do not keep durable context panels as floating overlays on desktop.
- Do not move runtime truth into browser-local layout state.
- Do not rely on color alone for status; keep semantic priority, text/icon/tooltip/ARIA labels.
- Treat mobile overlay/stack as a responsive presentation of the same dock contract, not a separate IA.

## Documentation routing

This is repo-level operational UI architecture. Put the canonical decision in `docs/adr/ADR-0NN — <title>.md` and update `docs/adr/README.md` plus `docs/adr/Index.md`. Keep broader strategy in Obsidian only as context/link, not as a duplicate ADR.
