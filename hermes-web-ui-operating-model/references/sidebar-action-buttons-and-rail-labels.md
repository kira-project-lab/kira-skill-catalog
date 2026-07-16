# Sidebar action buttons and rail labels

Use when changing Hermes Web UI activity-rail/sidebar navigation buttons.

## Reusable action-button styling

- Keep the composer-style action button language reusable in `packages/client/src/styles/action-buttons.scss`.
- Prefer shared SCSS mixins over copying button CSS:
  - `action-button-shell`
  - `action-button-content`
  - `action-button-icon`
  - `action-button-hover`
  - `action-button-active`
- Composer controls and sidebar nav items should consume the same shared mixins so compact outlined inactive state, filled light active state, centered 16px SVGs, and slight square rounding stay consistent.

## Sidebar nav links

- Sidebar route items must remain real anchors through `RouteLinkItem` / `<a href=...>` so middle-click and “open in new tab” browser behavior works.
- If adding tooltips or accessibility labels, extend `RouteLinkItem` props (`title`, `ariaLabel`) rather than replacing it with a button.
- Every action-styled nav item should have a short 1–4 word `title` and matching `aria-label`.

## Group labels

- Do not render visual `.nav-group-label` headers or `.nav-group-arrow` chevrons in the activity rail unless Maxim explicitly asks to restore collapsible group headers.
- If group headers are removed, also remove the folding plumbing and stale CSS:
  - `usePersistentRecord('hermes.sidebar.collapsedGroups')`
  - `groupLabel`
  - `toggleGroup`
  - `isGroupCollapsed`
  - `v-show="!isGroupCollapsed(...)"`
  - `.nav-group-label` / `.nav-group-arrow` styles
- Keep `.nav-group`, `.nav-group-items`, `.nav-panel-separator`, and all route/button items intact.

## Tests / verification

Focused contracts should assert:
- sidebar route items still render as anchors with `href`;
- `.nav-item` entries have short `title` + `aria-label`;
- `AppSidebar.vue` source does not contain `.nav-group-label`, `.nav-group-arrow`, or folding helpers after removal;
- `npm run build` passes;
- live-dev served source lacks removed selectors and reports the target commit in `/health`.
