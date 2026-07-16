# Resizable layout panels pattern

Use this when Maxim asks to let Hermes Web UI users narrow/widen side panels or change composer/input panel height with bounded controls.

## Scope pattern

Treat resizing as a small layout feature set, not a redesign:

- left app navigation/sidebar width;
- chat session list width;
- chat composer/input panel height.

Split work when multiple panels are involved:

```text
Parent coordination issue
├─ UX contract: defaults, min/max, persistence, mobile behavior, accessibility
├─ Implement left navigation/sidebar width
├─ Implement chat session list width
├─ Implement composer/input panel height
└─ Integrated QA gate
```

## Contract first

Before implementation, require exact values and behavior:

- default width/height;
- minimum and maximum bounds;
- whether values persist per browser/profile/user;
- clamping behavior for invalid persisted values and viewport changes;
- reset behavior;
- desktop vs mobile/narrow viewport behavior;
- interaction with existing collapse/expand controls;
- resize handle visual style and hit target;
- keyboard/accessibility path or explicit approved fallback.

Do not let implementers invent different limits per panel independently.

## Implementation guardrails
## Implementation guardrails

- Preserve the existing visual system: compact, sharp/straight edges; avoid unrelated redesign.
- Prefer CSS custom properties or a single local state/persistence path over scattered hard-coded sizes.
- Clamp persisted values before applying them.
- Keep collapsed icon-rail behavior separate from expanded sidebar resizing unless the contract explicitly says otherwise.
- Treat the composer panel height as different from native textarea resize/autogrow; Maxim asked about the containing input section, not only the textarea element.
- For the chat composer specifically, a good default contract is: textarea opens as one row (`rows="1"`), auto-grows from its content until `50vh` / `window.innerHeight * 0.5`, then keeps the textarea scrollable; manual section resize should use the same clamp and still apply height to the textarea as the actual growing element.
- If adjusting composer chrome, keep padding optical and symmetric when requested: for the rounded input shell, `padding: 10px;` aligned left/right spacing with the bottom edge better than `10px 12px`.
- Add locale strings for visible tooltips, labels, and ARIA text.

## Collapse/default-state guardrails

Panel size persistence and collapse-state persistence are separate contracts. Do not persist a collapse/expand choice just because panel width persists.

- Ask/decide explicitly whether a panel should restore its last collapse state after reload.
- For Maxim's main Hermes app navigation (`Hermes Studio`, Chat/History/Jobs), the preferred reload default is collapsed, independent of any prior expanded state.
- The chat session-list section is a separate surface; keep it expanded by default unless the task asks to persist or collapse it.
- Regression-test stale persisted values such as `hermes_sidebar_collapsed = '0'` so old browser state cannot override the intended reload default.

## Scroll containment interaction

Resizable panels can reintroduce page-scroll/flex bugs. Pair with `references/chat-scroll-containment.md` when the chat surface is involved.

Verify:

- internal session list scroll still owns session scrolling;
- message list remains visible and scrollable at max composer height;
- outer app/page scroll does not move the chat surface;
- non-chat routes that need page scroll still scroll normally.

## Likely Hermes Web UI paths

- `packages/client/src/App.vue` — top-level layout and `AppSidebar` placement.
- `packages/client/src/components/layout/AppSidebar.vue` — left navigation/sidebar.
- `packages/client/src/styles/variables.scss` — current sidebar width variables.
- `packages/client/src/components/hermes/chat/ChatPanel.vue` — session list and chat flex chain.
- `packages/client/src/components/hermes/chat/ChatInput.vue` — composer/input surface.
- Existing persistence composables/stores — persisted panel size state.

## Acceptance criteria to include

- Resize works only within contract bounds.
- Size persists across route changes and reloads.
- Invalid persisted values are clamped.
- Collapse/expand behavior still works.
- Mobile/narrow viewport behavior follows the contract.
- Keyboard/accessibility requirements are satisfied.
- No unrelated route/sidebar/composer redesign is included.
- Browser evidence covers resize, persistence, viewport clamp, and scroll containment.
