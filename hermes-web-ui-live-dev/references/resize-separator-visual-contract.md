# Resize separator visual contract

Use when Maxim reports that sidebar/session-pane separators look split, partial-height, duplicated, or visually inconsistent.

## Contract

Hermes Web UI has two adjacent vertical resize separators in the chat surface:

- `AppSidebar.vue` / `.sidebar-resize-handle` — navigation sidebar resize handle.
- `ChatPanel.vue` / `.session-list-resize-handle` — session list resize handle.

They should read as the same control class:

- full panel height: `top: 0; bottom: 0;`
- hit target: `width: 8px; right: -4px;`
- no visible border on the button itself: `border: 0; border-radius: 0; background: transparent;`
- high enough overlay: `z-index: 6;`
- visible line only via `::after`:
  - `position: absolute; top: 0; right: 3px; width: 1px; height: 100%;`
  - default transparent, hover/focus/resizing uses `$accent-primary`
- focus outline should match the nav sidebar handle when present.

## Pitfall

Do not start `.session-list-resize-handle` at `$header-height`. That creates a partial-height handle and leaves the session header boundary looking like a separate small divider. Maxim wants one continuous full-height separator, not a header segment plus a lower resize handle.

## Browser verification

Check both geometry and hit target, not just source:

```js
(() => {
  const el = document.querySelector('.session-list-resize-handle')
  const r = el.getBoundingClientRect()
  return {
    top: r.top,
    bottom: r.bottom,
    height: r.height,
    width: r.width,
    zIndex: getComputedStyle(el).zIndex,
    hits: [0, 30, 60, 300, Math.max(0, Math.floor(r.bottom - 1))].map(y => ({
      y,
      className: String(document.elementFromPoint(Math.floor(r.left), y)?.className || ''),
      title: document.elementFromPoint(Math.floor(r.left), y)?.getAttribute?.('title'),
    })),
  }
})()
```

Expected: height equals the owning pane height, `top` is `0`, and hit-tests at the top/header/body all return `session-list-resize-handle`.