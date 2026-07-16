# Reusable nav/action button style

Use this when Maxim likes a micro-control style in Hermes Web UI and asks to apply it elsewhere.

## Contract

- Preserve the composer action-button visual language as a reusable style module, not duplicated per component.
- Good current shape:
  - `packages/client/src/styles/action-buttons.scss`
  - mixins: `action-button-shell`, `action-button-content`, `action-button-icon`, `action-button-hover`, `action-button-active`
  - inactive: transparent background, 1px semantic line border, muted text/icon
  - hover: primary text/icon, muted border
  - active: filled `text-primary` background with `surface-root` foreground
  - centered 16px SVG icons, slight square rounding via `$radius-sm`
- When applying this to navigation rows, keep route entries as real anchors. Do not replace `RouteLinkItem` with buttons or divs; middle-click/new-tab behavior depends on `<a href=...>`.
- Style anchor-backed nav rows with the same action-button mixins while preserving `href`, `aria-current`, and `RouterLink` navigation.

## Test pattern

Add/update a source contract that checks:

- the shared SCSS module exists and contains the reusable mixins;
- composer controls consume the shared mixins instead of owning all button CSS inline;
- sidebar/nav items consume the shared mixins;
- `.route-link-item.nav-item` remains anchor-backed, and `RouteLinkItem.vue` still renders a real `<a :href="slotProps?.href || '#'">`.

Focused checks used successfully:

```bash
npm run test -- --run tests/client/design-token-pass.test.ts tests/client/route-link-item.test.ts tests/client/chat-input-draft.test.ts
npm run build
```

## Pitfalls

- Do not sacrifice link semantics for visual consistency. The nav item may look like a button, but it must remain a link when it represents a route.
- Avoid copying the exact composer CSS into sidebar styles. Extract the stable design language first, then consume it from both locations.
- Verify served component CSS, not only local source, because SCSS mixins compile into each component style block.
