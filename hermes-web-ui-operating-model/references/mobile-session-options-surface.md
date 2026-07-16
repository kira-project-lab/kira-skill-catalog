# Mobile session options surface

Use when Hermes Web UI exposes chat/session actions from a mobile header `⋮` button.

## Lesson

Do not adapt the desktop session `NDropdown` with cascading `children` submenus for mobile. It creates fragile UX and code:

- Mobile viewports do not have enough width for reliable side-opening submenus.
- Naive UI nested dropdown placement is controlled inside `DropdownOption`; root dropdown `placement` only affects the top-level menu.
- Popper/follower may flip submenus left when there is no right-side space, while the built-in suffix chevron can still imply right-opening behavior.
- Adding a left chevron inside the label is a symptom fix: it can coexist with Naive UI's built-in right chevron and produce contradictory cues.
- CSS targeting can be brittle because option `props.class` may land on the option body, not an outer container.

## Recommended mobile design

Keep desktop and mobile surfaces separate:

- Desktop: keep the existing context `NDropdown` with grouped actions and submenus.
- Mobile: the `⋮` button should open a dedicated action surface, preferably a right-side session options drawer in Hermes' workspace language, or a bottom/action sheet if a more native mobile pattern is desired.

Research/heuristic grounding:

- Popular mobile UI systems avoid cascading menus for nested actions because they depend on hover/side-opening spatial memory that phones do not have.
- Material-style guidance maps overflow actions to menus for short flat lists, and to modal bottom sheets / full-height sheets when the action set is longer, grouped, or needs nested choices.
- iOS-style interaction uses action sheets / sheets for contextual actions and drill-down navigation for secondary sets; avoid exposing submenus that open sideways from an overflow item.
- In Hermes Web UI, a right drawer is acceptable over a bottom sheet because the app already uses left/right workspace panels and the chat header has an obvious top-right anchor. Use a bottom/action sheet only if the action set becomes very short and non-hierarchical.

For Hermes specifically, prefer a **right-side mobile options drawer with drill-down**:

```text
Session options      ×
Open in new tab
Rename
Outline
Tags              ›
Workspace
Model
Export            ›
Copy              ›
Delete
```

Nested actions become internal views, not floating submenus:

```text
‹ Session options
Export
Full JSON
Compressed TXT
```

## Implementation shape

- Preserve desktop `NDropdown` behind `v-if="!isMobile"` or equivalent.
- Add mobile drawer state:
  - `showMobileSessionOptions`
  - `mobileSessionOptionsView: 'main' | 'tags' | 'export' | 'copy'`
- The mobile `⋮` handler sets `contextSessionId` to the active session and opens the drawer, not the dropdown.
- Main drawer rows are flat actions; rows that navigate to a subview use a right chevron.
- Subviews have a back affordance and reuse existing handlers (`toggle tag`, `export`, `copy`) without duplicating business logic.
- Destructive actions remain separated at the bottom and styled with the existing danger language.

## Visual style contract

Do not make the mobile drawer look like a generic stack of rounded action buttons. In Maxim's Hermes Web UI, this reads as foreign to the app style. Match the activity-rail/sidebar nav-row language instead:

- reuse `@include actionButtons.workspace-icon-label-row` for drawer rows when available;
- keep rows flat/transparent by default, with no per-row `border: 1px solid ...` boxes;
- avoid large independent corner rounding such as `border-radius: 8px` on every action row unless it matches the shared nav token (`$workspace-icon-row-radius` / a local `$sidebar-nav-button-radius` alias);
- use tight vertical rhythm like nav groups (`gap: 2px`), not card-button spacing;
- use the shared hover/active mixins (`action-button-hover`) instead of bespoke border hover states;
- put drill-down chevrons in a suffix grid column, matching list/navigation rows rather than floating submenu arrows.

If the drawer still feels visually wrong after the interaction model is fixed, check row chrome first: boxed borders and excessive rounding are usually the mismatch.

## Verification

Add source/UI contracts before implementation:

- Mobile `⋮` opens the mobile drawer, not `NDropdown`.
- Desktop context menu remains `NDropdown` and keeps existing order/actions.
- No mobile-specific cascade/dropdown hacks remain (`sessionSubmenuLabel`, mobile submenu chevron injection, `session-context-menu-submenu-left`).
- Drawer contains main view and drill-down view state.
- `Tags`, `Export`, and `Copy` do not render as floating dropdown children on mobile.

Run focused client tests and build, then restart live-dev and verify served source/health for the pushed commit.
