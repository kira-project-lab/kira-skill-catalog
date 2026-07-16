# Chat mobile parity and desktop context-menu action routing

Use this when adjusting Hermes Web UI chat controls that differ between desktop and mobile, or when moving header-only chat actions into the session context menu.

## Mobile composer Enter contract

- On desktop, bare `Enter` may submit; `Shift+Enter` inserts a newline.
- On a real mobile input device, bare `Enter` is the soft-keyboard return/newline key and must not submit. Let the native textarea behavior run by returning before `preventDefault()` / submit.
- Do **not** key this behavior to narrow viewport width alone: a half-width desktop window is still desktop input and should submit on bare `Enter`.
- Apply the same rule to the ordinary chat composer and group chat composer when both expose the same text-entry behavior.
- Implementation pattern: import/use a device/input-capability helper such as `isMobileInputDevice()` inside the keydown handler and include it in the early-return guard after IME checks. The helper should combine mobile UA checks with touch/coarse-pointer fallback.
- Test first with both cases: narrow desktop viewport should submit; mobile UA/touch input should not submit.

## Chat header action placement

- If Maxim asks to add a quick action "next to the `...`" in the top-right chat header, treat the kebab/options button as the anchor and place the new control immediately before it in the same `.header-actions` / mobile actions group.
- For New Chat parity, reuse the existing new-chat handler/drawer behavior rather than creating a second session-creation path. Keep the button square/compact, with tooltip/`aria-label`, and preserve the options button immediately to its right.
- Add the header action in both desktop and mobile header action groups when the request is phrased as a general top-right chat affordance, unless Maxim explicitly limits it to desktop.
- If a chat header action is specifically desktop-oriented, do not hide it with CSS only. Prefer not rendering the toolbar on mobile, e.g. `v-if="!isMobile"` on `.chat-header-toolbar`, so the control is absent from mobile accessibility/navigation too.
- Keep mobile-native controls (hamburger/session drawer buttons) separate from desktop toolbar actions.
- Protect this with a source/component contract that the toolbar is gated by `!isMobile` and no ungated `.chat-header-toolbar` remains, and for top-right quick actions assert order: new/control button before options/kebab.

## Routing outline through the session context menu

- `ChatPanel.vue` owns session context-menu options and handlers. To move a header-only action into the right-click menu:
  1. Add a typed icon name/path to `SessionMenuIconName` / `sessionMenuIconPaths`.
  2. Add a `DropdownOption` entry to `contextMenuOptions`, e.g. `{ label: t("chat.outlineTitle"), key: "outline", icon: sessionMenuIcon("outline") }`.
  3. Handle the key in `handleContextMenuSelect`, e.g. `toggleInspector("outline")`.
  4. If a header button should invoke the same menu, add a helper that sets `contextSessionId` to `chatStore.activeSessionId`, positions `contextMenuX/Y` from the clicked button rect, and sets `showContextMenu = true`.
- Avoid duplicating action behavior between header and context menu. The header button should open the menu; the menu item should own the action.
- Source-contract tests are useful here because Naive UI dropdown content is teleported and hard to inspect in shallow component tests.

## Mobile active-session options menu

- The mobile chat header needs a distinct top-right active-session options button, not a reused outline/list icon. Prefer an inline SVG vertical ellipsis / kebab (`circle` dots, `fill="currentColor"`) for “more/options”.
- When opening the active-session context menu from that right-edge mobile button, align the dropdown under the button’s right edge: use a mobile-only placement such as `bottom-end` and set the manual `x` coordinate from `button.getBoundingClientRect().right`; keep desktop `bottom-start` / `rect.left` behavior.
- If Naive UI submenu items must flip left on mobile because there is no right-side space, make the direction explicit in the row itself. For mobile submenu rows such as Tags, Export, and Copy, render a left cue (`‹ Label`) and hide the default right-facing submenu suffix for those rows. Do not move the options button left just to make submenus open right; it conflates navigation controls with current-session actions.
- Protect this with source contracts that assert: mobile `contextMenuPlacement`, `rect.right` positioning, the mobile menu class, mobile submenu cue classes, and the absence/hiding of the misleading right chevron on mobile submenu rows.

## Verification

- If desktop chat header actions are gated behind `v-if="!isMobile"`, keep a separate mobile-native options affordance for the active session in the chat header. Do not assume hiding the desktop toolbar is sufficient; mobile still needs access to rename/tags/outline/copy/delete session actions.
- Place the mobile options affordance on the right side of `.chat-header`, separate from the left mobile menu/session drawer controls, e.g. `.chat-header-mobile-actions` with `margin-left: auto`.
- The mobile options button should call the same `openActiveSessionContextMenu` helper as the desktop outline/menu button. Do not wire it directly to `toggleInspector('outline')`; the menu item owns the outline action.
- Use a distinct **vertical ellipsis / kebab** SVG for this mobile options button, not the outline/list icon. A list/hamburger-like icon reads too similarly to the left session/menu controls. A durable source contract should assert `.chat-header-options-button`, `pane-toolbar-button-icon--kebab`, three vertical `<circle>` nodes, and absence of the old `M3 12h18` / `M3 6h18` / `M3 18h18` outline paths inside the mobile options block.
- Add a user-facing `chat.sessionOptions` i18n key in every locale file for the button `aria-label` and `title`.

## Verification

- Run the focused client contract/component tests first.
- Run `npm run build` for Vue/TS regressions.
- For live-dev changes, restart `hermes-web-ui-dev.service`, verify local/public `/health` reports the pushed commit, and verify served Vite source contains the expected menu key/helper/gating.