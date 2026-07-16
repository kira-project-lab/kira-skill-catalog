# Chat session sidebar anatomy and border alignment

Use this reference when debugging visual issues around the Chat left session pane, main chat header, and the divider between them.

## Key elements

In `packages/client/src/components/hermes/chat/ChatPanel.vue`:

- Session dock/sidebar container: `.session-dock`
- Session sidebar header: `.pane-header.session-pane-header`
- Session list body: `.pane-body.session-items`
- Sidebar resize separator: `.session-list-resize-handle`
- Main chat header: `.pane-header.chat-header`
- Main chat body: `.pane-body.chat-content-wrapper`

The session header and chat header intentionally share `.pane-header` and should have the same height from `$header-height`.

## Pitfall: 1–2px border mismatch at the divider

If Maxim reports that the horizontal line under the left session header and the horizontal line under the main chat header are off by a couple of pixels, do not start by changing header height.

First inspect the real DOM geometry:

```js
(() => {
  const q = s => document.querySelector(s)
  const data = el => {
    if (!el) return null
    const r = el.getBoundingClientRect()
    const cs = getComputedStyle(el)
    return {
      top: r.top,
      bottom: r.bottom,
      height: r.height,
      padding: cs.padding,
      borderTop: cs.borderTopWidth,
      borderBottom: cs.borderBottomWidth,
      boxSizing: cs.boxSizing,
    }
  }
  return {
    sessionHeader: data(q('.session-pane-header')),
    chatHeader: data(q('.chat-header')),
    resizeHandle: data(q('.session-list-resize-handle')),
  }
})()
```

Observed root cause pattern: both headers can be exactly aligned (`top: 0`, `bottom: 60`, `height: 60`) while the mismatch is caused by `.session-list-resize-handle`:

- it is absolutely positioned inside `.session-dock`;
- `top: 0; bottom: 0; right: -4px; width: 8px; z-index: 2;`
- its pseudo-line (`::after`) overlays the T-junction between the header bottom borders and the vertical separator.

Quick browser proof: temporarily hide `.session-list-resize-handle`; if the visual step disappears, the problem is the overlay/resizer junction, not header height.

```js
const style = document.createElement('style')
style.textContent = '.session-list-resize-handle{display:none!important}'
document.head.appendChild(style)
```

## Fix direction

Prefer fixing the separator/resizer geometry over changing header height:

- align the resizer line with the real panel border;
- avoid drawing the full-height overlay across the header border junction;
- or start the active/pseudo line below the header border if that matches the intended visual design.

Known-good fix for the chat/session-pane T-junction: keep `.pane-header` shared at `$header-height`, but start `.session-list-resize-handle` below the header:

```scss
.session-list-resize-handle {
  position: absolute;
  top: $header-height;
  right: -4px;
  bottom: 0;
}
```

Verification after the fix:

- `.session-pane-header.getBoundingClientRect().bottom === .chat-header.getBoundingClientRect().bottom`;
- `getComputedStyle(.session-list-resize-handle).top === "60px"` when `$header-height` is `60px`;
- browser visual check shows no 1–2px step at the left session pane / main chat boundary.

Keep the shared `.pane-header` height contract intact unless DOM measurements prove the headers themselves differ.
