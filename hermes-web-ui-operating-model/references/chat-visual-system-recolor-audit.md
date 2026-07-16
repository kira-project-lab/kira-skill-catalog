# Chat visual-system recolor audit

Use when Maxim asks to recolor, simplify, standardize, or rationalize the Hermes Web UI chat surface.

## Scope to inventory first

For a standard chat screen with most capabilities visible, inspect these surfaces before proposing token changes:

1. App/root shell: body/root background, global scrollbars, selection.
2. App sidebar logo section: logo block, collapse button, resize handle.
3. App sidebar navigation: group labels, nav idle/hover/active, badges, profile/model selectors, footer, connection status, version/theme/language controls.
4. Session list: panel background, resize handle, launcher row, search/new buttons, group labels, session row idle/hover/active, title/time/preview, author badges, action menu, status rail/dot/warning states.
5. Chat center: chat root, header, header action buttons, workspace/source badges, message bubbles, system/command/error messages, command status chips, attachments, thinking blocks, tool lines/details, markdown inline/block elements, queue float panel.
6. Composer: input area, input wrapper, textarea, slash-command dropdown, context bar, attachments, trace/speech toggles.
7. Approval/clarify bars: container, icon block, command snippet, actions separator.
8. Outline panel: panel, header, user question block, heading rows, empty state.
9. Drawer/tools: overlay, drawer panel, tabs, close button, terminal/files sidebars, terminal session rows, shell badge, xterm/file frames.

## Output shape Maxim expects

Provide a numbered inventory in this compact form:

```md
1. <element name>
Цвет: <actual token/literal and resolved value when known>
Доп. декор: <border/outline/shadow/radius/glow/gradient/scrollbar/etc.>
Проблема/решение: <only if relevant>
```

Keep the inventory evidence-based. Separate what is verified in code/browser from judgment.

## Recolor diagnosis checklist

Look specifically for these failure patterns:

- Too many near-identical dark surfaces (e.g. `#1a1a1a`, `#202020`, `#252525`, `#262626`, `#2a2a2a`, `#333333`, `#393939`).
- Accent token is effectively white/gray, causing hover/active/focus/code/badge states to look like random gray haze instead of state.
- Components use local `rgba(255,255,255,...)`, `rgba(0,0,0,...)`, `color-mix(...)`, or hardcoded semantic colors instead of shared tokens.
- Permanent structural panes use shadows when borders would be cleaner.
- Similar controls use different radii (`0`, `2`, `3`, `4`, `6`, `8`, `10`, `12`, `14`, `16`, `999`, `50%`).
- Status dots/rails use multiple shapes, halos, and independent palettes that are louder than their information value.
- Naive UI controls visually diverge from custom Hermes controls.

## Recommended simplification model

Do not start by manually recoloring individual components. First propose a token layer and component primitives.

Suggested dark surface stack:

```scss
--surface-root: #0f1113;
--surface-sidebar: #15181b;
--surface-panel: #1b1f23;
--surface-raised: #22272c;
--surface-hover: #283038;

--line-subtle: #252b31;
--line-default: #343b43;
--line-strong: #4a535d;

--text-primary: #eef2f4;
--text-secondary: #aeb7bf;
--text-muted: #737d86;
```

Prefer a non-white accent for selected/focus/action states, e.g. cold steel:

```scss
--accent-primary: #7aa2c7;
--accent-soft: rgba(122, 162, 199, 0.14);
--accent-line: rgba(122, 162, 199, 0.32);
```

State tokens:

```scss
--state-hover-bg: rgba(255,255,255,.045);
--state-active-bg: rgba(122,162,199,.14);
--state-active-line: #7aa2c7;
--state-focus-ring: rgba(122,162,199,.42);
```

Geometry tokens:

```scss
--radius-none: 0;
--radius-sm: 4px;
--radius-md: 6px;
--radius-lg: 8px;
```

Status tokens:

```scss
--status-running: #7aa2c7;
--status-waiting: #d6a75c;
--status-success: #7fc29b;
--status-error: #d97878;
--status-unread: #eef2f4;
```

## Recolor implementation order

1. Add/adjust semantic tokens in `packages/client/src/styles/variables.scss`.
2. Replace hardcoded gray/white/black alpha in chat surface components with semantic tokens.
3. Standardize shared primitives before per-component polish: `panel`, `row`, `button`, `badge`, `event-block`, `status-dot`, `resize-handle`, `scrollbar`.
4. Remove shadows from permanent panes; reserve one `--shadow-popover` for true popovers/floating panels.
5. Make hover, active, and focus visually distinct: hover = weak surface tint, active = tint plus accent rail/line, focus = ring/outline only.
6. Browser-review the full chat screen with app sidebar, session list, chat, outline, drawer/tools, approval/clarify, and composer visible.

## Pitfalls

- Do not let `--accent-primary` remain near-white if the goal is recolor clarity; it turns every state into another gray.
- Do not solve by adding more grays. Reduce surface count first.
- Do not preserve component-local decorative exceptions unless they carry a real semantic role.
- Do not change data/status semantics while doing recolor; visual tokens only unless Maxim asks for behavior changes.
