# Scrollbar and resize-handle mapping for Hermes Web UI

Use this when a request mentions the “slider”, “scroll bar”, or the text-area drag edge in the voice/chat surfaces.

## What is what

- **Page scrollbar**: the main document scroller is typically the app shell container, often `.app-main` in `packages/client/src/App.vue`.
- **Textarea scrollbar**: native scrollbars inside a text area are local to the textarea element itself, e.g. `.input-textarea` in `packages/client/src/components/hermes/chat/ChatInput.vue` or `NInput type="textarea"` controls.
- **Resize handle**: the thin drag zone used to change textarea height is not a scrollbar. In `ChatInput.vue` it is `.resize-handle` and is driven by `startResize(...)`.

## Styling pattern

- Global scrollbar skin lives in `packages/client/src/styles/global.scss`.
- Local overrides are appropriate when only one surface should change.
- For a sharp-corner look, set the thumb radius to `0` and keep the track transparent or neutral.
- Prefer separate treatment for:
  - page scrollbars,
  - textarea scrollbars,
  - resize handles.

## Practical check

Before editing, identify the DOM node you actually want:

1. Is it the page content area? Patch the app shell container.
2. Is it the message/text input itself? Patch the textarea selector.
3. Is it the draggable edge above the input? Patch the resize-handle styles, not scrollbar styles.
