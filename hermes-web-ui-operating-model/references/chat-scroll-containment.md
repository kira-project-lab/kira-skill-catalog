# Chat scroll containment pattern

Use this when Hermes Web UI chat/session surfaces can be scrolled out of view, wheel/trackpad events seem to move the whole page instead of the intended pane, or a chat route has nested scroll containers.

## Symptom

- A user can “over-scroll” downward/upward until the session list or full chat surface disappears.
- The session list and message list may each have their own scrollbars, but the outer app/page also scrolls.
- The bug is more visible with trackpads or strong wheel momentum because events bubble from the internal scroll area to the page-level scroll container.

## Root-cause pattern

Look for this chain:

```text
.app-main overflow-y: auto
  └─ route view height: 100vh / calc(100 * var(--vh))
      └─ chat panel with internal scroll panes
```

When the route view is sized as another viewport inside an already scrollable app main, the outer `.app-main` can become a competing scroll container. In flex layouts, missing `min-height: 0` on intermediate parents can also prevent internal `overflow-y: auto` panes from owning the scroll.

## Fix pattern

Keep chat routes viewport-locked and put scrolling only in intentional internal panes:

```scss
.chat-view {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.app-main {
  min-width: 0;
  min-height: 0;
}
```

For chat-specific pages, prefer route-specific outer containment rather than globally removing page scroll from pages that need it.

Add or verify `min-height: 0` through the flex chain, especially:

```scss
.chat-panel,
.chat-main,
.chat-content-wrapper,
.chat-main-content,
.session-list,
.session-items {
  min-height: 0;
}
```

Keep `overflow-y: auto` only on panes that should scroll, such as the session items list and message list.

## Verification

- Open a long session list and a long chat.
- Use strong wheel/trackpad scroll at the bottom/top of each internal pane.
- The app/page must not move; only the intended pane should scroll.
- Confirm non-chat routes still retain normal page scrolling if they need it.
- Prefer browser evidence or an e2e assertion that the route/page scroll position remains fixed while internal panes scroll.

## Pitfalls

- Do not fix this by globally disabling all `.app-main` scrolling unless you confirm every route can provide its own scroll behavior.
- Do not rely on `height: 100vh` inside a parent that already owns viewport height; it often creates a second scrollable viewport.
- Do not diagnose from CSS alone when possible: identify which element's `scrollTop` changes during reproduction.
