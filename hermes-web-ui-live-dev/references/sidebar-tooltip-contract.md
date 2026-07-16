# Sidebar and Composer Tooltip Contract

Use this when Maxim asks for faster text comments/tooltips on Hermes Web UI icon controls or asks for the same tooltip design in the panel/navigation list.

## Durable pattern

- Composer icon buttons in `ChatInput.vue` use Naive UI `NTooltip`; the default popover delay is `100ms`.
- If Maxim asks to make tooltip/comment display "2x faster", set `:delay="50"` (prefer a local constant like `TOOLTIP_DELAY = 50`) instead of changing animation CSS.
- For sidebar route/panel items, prefer the same `NTooltip` implementation over native `title` attributes so the visual design matches composer button tooltips.
- Remove native `title` from the actual trigger element when wrapping it in `NTooltip`; otherwise the browser native tooltip can appear alongside the styled tooltip.
- Preserve accessibility and routing:
  - keep `aria-label` on the real clickable element;
  - keep the real anchor `href` for `RouteLinkItem` so deep links/navigation still work;
  - if wrapping a custom component in `NTooltip`, ensure attrs/classes still land on the real `<a>` (for example `defineOptions({ inheritAttrs: false })` + `v-bind="$attrs"`).

## Verification

In browser, inspect both a nav item and a composer button:

- route link still has `.route-link-item.nav-item` and an `href`;
- native `title` is absent on the trigger;
- `aria-label` remains present;
- after dispatching hover/mouseenter and waiting around `70–90ms`, `.n-tooltip` / `.n-popover` content appears.

## Pitfalls

- Do not rely on `title` if the user asks for the tooltip design used by composer buttons; that is native browser UI, not the themed tooltip.
- Wrapping `RouteLinkItem` with `NTooltip` can swallow parent `class="nav-item"` unless attrs are explicitly forwarded to the inner anchor.
- Do not remove `href` when introducing tooltip wrappers; direct navigation/deep-link behavior is part of the sidebar contract.
