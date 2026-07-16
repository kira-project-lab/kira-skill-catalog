# Workspace header separator alignment

Use when Maxim asks for the left activity rail, session pane, and main chat pane to feel like one continuous workspace shell.

## Goal

The bottom borders / horizontal separators of the three top zones should land on one shared y-coordinate:

1. activity rail top utility area;
2. session pane toolbar/header;
3. main chat header.

## Implementation pattern

- Use the shared `$header-height` token from `packages/client/src/styles/variables.scss` as the single source of truth.
- In `ChatPanel.vue`, make `.pane-header` use both:
  - `height: $header-height;`
  - `min-height: $header-height;`
- Avoid vertical padding that changes the effective height of `.chat-header`; use horizontal padding only, e.g. `padding: 0 20px;`.
- For `AppSidebar.vue` / activity rail, add a top separator at the same y-coordinate with a pseudo-element:
  - `.sidebar::before { top: $header-height; height: 1px; background: $line-default; }`
- Offset the rail navigation below the top zone, e.g. `padding-top: calc(#{$header-height} + 8px);`.
- Center any top utility/collapse button inside the shared header band, e.g. `top: calc((#{$header-height} - 28px) / 2);`.

## Test contract

Add/keep a source-level UI contract that asserts:

- `$header-height` is the shared token;
- `ChatPanel.vue` uses `height` and `min-height` from that token for pane headers;
- `.chat-header` has no vertical padding;
- `AppSidebar.vue` renders the pseudo separator at `$header-height`;
- rail content starts below the shared top band;
- the collapse button is centered within the band.

## Pitfalls

- Do not tune the three sections independently with visually similar pixel values; it will drift later.
- Do not leave `.chat-header { padding: 21px 20px; }` or similar vertical padding after introducing a shared height; padding plus height makes the separator appear misaligned.
- Do not fake the activity rail header by only adding top padding; the visible separator must be drawn at the same y-coordinate as the pane header borders.
