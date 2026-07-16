# Icon button visual contract

Use this when Maxim reports sidebar/nav/header icon buttons looking outlined, too large, or inconsistent.

## Root-cause pattern

- A visible "outline" around `.route-link-item.nav-item` may actually be `border` from `packages/client/src/styles/action-buttons.scss`, not CSS `outline`.
- Browser `getComputedStyle(el).outline` can show a color/width even when `outline-style: none`; check `outlineStyle`, `border`, and `boxShadow` separately.
- Naive UI buttons can add internal visual frames via `.n-button__state-border`, `.n-button__border`, and `.n-button__ripple`; hide these for custom icon buttons.
- Theme buttons can drift if they hand-roll styles instead of using the shared action-button mixins.

## Preferred contract

- Shared icon shell: `action-button-shell` should remove frames: `border: none`, `outline: none`, `box-shadow: none`.
- Hover state: light neutral fill via `$state-hover-bg`, not an outline/border.
- Header/panel action buttons should be compact equal squares that frame only the SVG, e.g. `24px × 24px` with rounded corners.
- Theme/style toggle buttons should use the same shared shell/hover mixins as other icon buttons.

## Verification

In browser, verify representative elements:

```js
for (const selector of [
  '.route-link-item.nav-item[href="#/hermes/memory"]',
  'button.nav-item',
  '.theme-switch',
  '.header-action-button',
]) {
  const el = document.querySelector(selector)
  const cs = getComputedStyle(el)
  const r = el.getBoundingClientRect()
  console.log(selector, {
    width: r.width,
    height: r.height,
    border: cs.border,
    outlineStyle: cs.outlineStyle,
    boxShadow: cs.boxShadow,
    background: cs.backgroundColor,
    borderRadius: cs.borderRadius,
  })
}
```

Expected: `outlineStyle: "none"`, `boxShadow: "none"`, no visible border; panel/theme buttons square and consistent.