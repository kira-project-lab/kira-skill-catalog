# Telegram-like session tag assignment

Use this reference when implementing or reviewing session tag assignment UX in Hermes Web UI.

## Product contract

- The fast path is a Telegram-like context submenu, not a modal:
  - session right-click menu item: `Tags…` / `Теги…` with child options.
  - child tag rows are membership toggles: `✓` means assigned; clicking again removes the tag from that session.
  - keep the menu open after toggle so multiple tags can be changed in one pass.
- Creation and management are separate jobs:
  - `+ New tag…` opens a lightweight create dialog.
  - primary button copy should communicate the contextual side effect: `Create and add`.
  - `Manage tags…` opens a separate management modal for edit/recolor/delete.
- Destructive reusable-tag deletion must never be in the fast assignment path. Keep it behind `Manage tags…` plus confirmation that the tag is removed from sessions but sessions are not deleted.

## Implementation pattern

- Build the parent context menu `Tags…` option with `children: tagAssignmentMenuOptions.value`.
- Render tag rows with a custom label renderer, e.g. `renderSessionTagMenuItem(tag)`, so the row can show:
  - checkmark column;
  - color dot using the limited tag palette;
  - label.
- Do not show visible `Assigned` / `Not assigned` text in the submenu; the checkmark carries the visual state, while `aria-checked` carries the accessibility state.
- Handle child keys separately from normal context-menu actions:
  - `tag-toggle:<id>` toggles assignment and immediately restores/keeps `showContextMenu.value = true`.
  - `create-tag` closes the menu and opens `showCreateSessionTagModal`.
  - `manage-tags` closes the menu and opens `showManageSessionTagsModal`.
- Keep reusable tag operations in the existing session-browser prefs store helpers:
  - `assignBadgeToSession()` / `removeBadgeFromSession()` for membership;
  - `createBadgeForSession()` for create-and-add;
  - `updateBadgeDefinition()` / `deleteBadgeDefinition()` for management.

## Tests and contracts

Add/keep focused source contracts in `tests/client/session-list-item.test.ts` that assert:

- `Tags…` uses `children: tagAssignmentMenuOptions.value`.
- `tag-toggle:` dispatch exists and calls assignment toggle logic.
- the old assignment modal fast path is absent (`showSessionTagModal.value = true` should not be the path for `add-badge`).
- create and manage use separate modal states (`showCreateSessionTagModal`, `showManageSessionTagsModal`).
- user-facing strings such as `createAndAddTag`, `editTag`, and `noTagsYetShort` exist in all locale files.

## Browser QA checklist

On live-dev, verify with a real context menu:

1. Right-click a session row.
2. Open `Tags…`.
3. Confirm existing tags show only the checkmark as the visible assignment indicator; `Assigned` / `Not assigned` text should not be visible.
4. Confirm accessibility state is still preserved via `aria-checked` / menuitemcheckbox semantics.
5. Toggle at least two tags in the same open menu; the menu should remain open and row chips should update.
5. Use `+ New tag…`; create a temporary QA tag; confirm it is immediately assigned.
8. In `Manage tags…`, confirm the edit action is labeled `Edit`, not `Rename`, because it edits both label and color.
9. Trigger delete confirmation for the QA tag and verify copy says sessions are not deleted.
10. Delete the QA tag and restore any pre-existing tag assignments modified during QA.

## Pitfalls

- Naive UI dropdowns may close on selection by default. For membership toggles, explicitly keep/reopen the controlled context menu after `tag-toggle:<id>`.
- Do not reintroduce a large `Tags for this session` assignment modal as the primary flow; it is slower and mixes assignment with global tag management.
- Avoid using dropdown `type: "divider"` source-contract checks too broadly: nested tag submenus also contain dividers. Contract tests should look for specific divider keys such as `session-context-divider-primary` when checking parent menu order.
