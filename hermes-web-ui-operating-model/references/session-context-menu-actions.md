# Session context-menu action design

Use this when changing the right-click / long-press menu for chat session rows.

## Contract

- Keep row hover affordances quiet; actions live in the context menu, not hidden `...` row controls.
- Preferred session-row context menu order:
  1. `Open in new tab`
  2. `Rename`
  3. divider
  4. `Set workspace`
  5. `Set model`
  6. `Export` → `Full export (json)` / `Compressed export (txt)`
  7. divider
  8. `Copy session` → `ID` / `Link`
  9. `Delete`
- Do not reintroduce `Pin/Unpin` into this menu unless explicitly requested; it competes with the simpler session action model.
- Give every textual option a left icon. For Naive UI `NDropdown`, use the option `icon` renderer and a shared icon wrapper class so nested menu items inherit the same geometry.
- Destructive action styling: `Delete` text/icon should use the semantic error token (`--status-error`), not a generic muted/action color.
- Menu labels and non-destructive icons should read brighter than muted metadata; use `--text-primary` for option label/prefix/suffix text and custom icon wrappers unless a destructive token overrides it.
- Hover lightening should be immediate for this sharp ops UI. Set context-menu option hover/text transitions to `none` / `0s` rather than relying on default fade transitions, and do not let icon color darken/shift on hover.
- The `Pin` option should use a clearly upright diagonal pushpin glyph, not a vertical/upside-down pin shape.

## Implementation notes

- `packages/client/src/components/hermes/chat/ChatPanel.vue` owns the session context-menu options and handler.
- For style rules inside a scoped Vue SFC, use `:global(.session-context-menu ...)` because Naive UI dropdown content is rendered outside the local component subtree.
- Naive UI dropdown styles can beat weak overrides. For instant hover and danger colors, include the real menu root class in selectors and use sufficient specificity, for example `:global(.session-context-menu.n-dropdown-menu .n-dropdown-option .n-dropdown-option-body::before) { transition: none !important; }` and `:global(.session-context-menu.n-dropdown-menu .session-context-menu-delete .n-dropdown-option-body__label) { color: var(--status-error) !important; }`.
- Prevent icon hover darkening by styling the custom icon wrapper directly, not only the Naive UI prefix: `:global(.session-context-menu.n-dropdown-menu .n-dropdown-option .session-context-menu-icon) { color: var(--text-primary) !important; transition: color 0s !important; }`.
- Make the destructive color cover both text and the custom icon wrapper: include `.session-context-menu-delete .session-context-menu-icon`, not only Naive UI label/prefix/suffix classes. Keep the destructive rule after the generic icon rule and use `!important`, otherwise a stable non-destructive icon override can accidentally turn Delete back to primary text color.
- Add/keep a source contract that checks the menu order, dividers, nested export/copy options, icon renderer calls, delete class, brighter text token, error token for text and icon, stable `--text-primary` non-destructive icon color, upright pin path, and `transition: none !important` / `0s` transitions.
- When verifying served source in Vite dev mode, remember the SFC script and style may be served separately; check the style URL (`?vue&type=style...`) for CSS rules if they do not appear in the transformed script response.
- Browser QA should inspect computed styles after opening the menu: dispatch a real right-click sequence (`pointerdown` + `mousedown` + `contextmenu` with `button: 2`) on `a.session-item`, then assert `getComputedStyle(optionBody, '::before').transition === 'none'`, delete icon color equals delete label color, and the Pin SVG path is the intended upright glyph.
