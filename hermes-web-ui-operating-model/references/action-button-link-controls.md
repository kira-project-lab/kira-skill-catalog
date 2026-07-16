# Reusable action-button/link controls

Use when applying the compact composer-control visual language outside the chat composer, especially to sidebar/activity-rail navigation.

## Contract

- Keep the visual language reusable, not copied into each component:
  - put shared SCSS in `packages/client/src/styles/action-buttons.scss`;
  - expose mixins such as `action-button-shell`, `action-button-content`, `action-button-icon`, `action-button-hover`, `action-button-active`.
- Preserve the liked composer geometry:
  - compact outlined gray inactive state;
  - filled light/white active state;
  - centered 16px SVG icons;
  - slightly rounded square/rectangular shape.
- For navigation items, keep route entries as real anchors via `RouteLinkItem` / `<a href=...>` so middle-click and open-in-new-tab still work.
- Add short explanatory hints to every action-styled nav item:
  - `title` and `aria-label` should both be present;
  - text should be laconic, normally 1–4 words;
  - use existing sidebar labels where they are already short.
- If `RouteLinkItem` receives new hint props, pass them through to the rendered anchor without changing its `href` or `@click="slotProps?.navigate"` behavior.

## Test pattern

- Source contract: assert reusable SCSS file exists and components import/use the mixins.
- Route contract: `RouteLinkItem` renders a real `a` with `href`, `title`, and `aria-label`.
- Sidebar contract: all `.nav-item` nodes have a short `title` and matching `aria-label`; all `a.route-link-item.nav-item` nodes retain `href`.
- Build after SCSS mixin changes; scoped SFC style compilation can pass source tests but fail in `vue-tsc`/Vite.

## Semantic action states for composer controls

When a compact action button represents a semantic runtime/queue state, let that semantic state choose the accent instead of reusing the generic primary/accent active color.

- `append` / `queue` send state should visually match queued-message affordances: use `var(--accent-info)` for the active queue send button background and border, not `var(--accent-primary)` or neutral gray.
- Keep normal send/default states in the generic composer action-button language; only the stateful queued/append mode gets the info accent.
- The queued/append send control still means “send this message”; keep the same upward send arrow as the normal send button. Do not switch it to a right-arrow/forward glyph just because the message will be queued.
- Add a focused source/style contract near the composer tests that asserts the queued class (`.composer-action-button--queue:not(:disabled)`) uses `background: var(--accent-info) !important;` and `border-color: var(--accent-info) !important;`, that the queued icon reuses the normal send/up-arrow paths/classes, and that old right-arrow paths are absent.
- For browser-visible polish, verify both the source contract and the served Vite bundle/source after live-dev restart; CSS regressions can pass component behavior tests.

## Chat header controls

When applying the composer/send-button visual language to `ChatPanel.vue` header controls:

- Use the shared `@/styles/action-buttons` mixins instead of Naive UI `quaternary size="small" circle` defaults.
- Prefer a compact square button (`@include actionButtons.action-button-shell(28px)`) with slight rounding over circular 28px buttons.
- Render the SVG directly in the `NButton` body with a stable class such as `.header-action-icon`; avoid the `#icon` slot when visual centering matters because it adds `.n-button__icon` / `.n-icon-slot` wrappers.
- Give every header action short `title` and `aria-label` values; invisible icon-only controls must remain self-describing.
- For panel/inspector toggles, project state into an active class (for example `.header-action-button--active`) and use `action-button-active`; stateless actions such as “copy session id” stay outlined/inactive.
- Preserve existing behavior: session pane toggle still flips `showSessions`; inspector buttons still call `toggleInspector('<mode>')`; drawer/files launcher remains inside `.header-actions`, not as a floating overlay.
- Add/update source contracts that `ChatPanel.vue` imports the shared action-button module, uses `.header-action-button`, uses the active class, uses direct icon classes, and keeps the drawer action inside the header actions block.

## Pitfalls

- Do not replace route links with buttons just to get button styling; that breaks middle-click/new-tab behavior.
- Do not rely on visible text alone when collapsed/icon-rail mode hides labels; `title`/`aria-label` must carry the short explanation.
- Avoid one-off class copies of composer styles; future polish should happen in the shared mixins.
- Do not leave Naive UI `circle`/`#icon` slot defaults on controls Maxim asked to match the composer/send style; they visually regress to round gray dots with wrapper-induced icon centering issues.
