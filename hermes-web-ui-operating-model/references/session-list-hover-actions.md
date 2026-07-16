# Session list hover actions

Use when changing session-list row affordances in Hermes Web UI.

## Current Kira preference

- Do not show a hover-only `...` / ellipsis widget on session rows.
- Keep rows visually clean: title/time on the first line, preview/status on the second line, no hidden action button appearing on hover.
- Keep context actions accessible through the existing context menu path: right-click on desktop and long-press on touch.

## Implementation notes

- Remove the DOM, props, emits, and CSS together; do not only hide the button with CSS.
- In `SessionListItem.vue`, avoid `session-item-actions`, `actionsMenu`, and `open-actions` for row hover menus.
- In `ChatPanel.vue`, avoid passing `actions-menu`, listening to `@open-actions`, or maintaining a separate `handleActionMenu` path for the ellipsis.
- Keep `@contextmenu="handleContextMenu($event, s.id)"` and long-press behavior so actions remain reachable without visual row chrome.

## Tests / verification

- Update source-contract tests to assert `session-item-actions`, `actions-menu`, `open-actions`, and `handleActionMenu` are absent.
- Run the session row focused test and build.
- For live-dev, verify served `SessionListItem.vue` and `ChatPanel.vue` no longer contain the removed selectors/props/events.
