# Session card tags and avatar pattern

Use when changing the Hermes chat session-list card layout, identity metadata, filtering, or user-defined labels/tags.

Note: older code paths may still use `badge` internally. User-facing copy, menus, and docs for this UX should say `tag` unless Maxim explicitly asks to preserve the old wording.

## Contract

- Keep the session card readable as three distinct rows:
  1. pinned state + title + time;
  2. message preview only, without author/runtime prefixes;
  3. user custom tags only.
- Use a left avatar column as the stable identity anchor for the full card height.
  - Hermes sessions should use the selected/profile avatar when available, rendered as a rounded-square avatar rather than a circular one.
  - Coding/runtime sessions may use runtime-specific avatar treatment when that is the clearer identity.
  - Put the identity label under the avatar: profile name for Hermes sessions, `codex` / `claude` for coding-agent sessions.
  - Do not render a separate `Hermes` runtime label in session rows.
- Custom session tags are account/profile preferences, not browser-local decoration.
  - Store tag definitions and session assignments through the session-browser-prefs API/store path, even if the existing implementation still names those fields `badge` internally.
  - Keep assignments per session; keep definitions reusable at the profile/account level.
  - The add-tag flow must support both creating a new tag and assigning an existing tag definition to another session.
  - Editing/deleting tags should operate on the reusable definition and propagate through assignments; deletion should clean assignments rather than leaving orphaned tag ids.
- Restrict custom tag colors to the agreed named palette (`gray`, `blue`, `violet`, `green`, `yellow`, `orange`, `red`, `pink`). Do not allow arbitrary hex/freeform colors in the first-pass UX; it breaks the neutral visual system and makes QA harder.
- Session-list filters belong in the toolbar between Search and New Chat. Provide filters for both profile/runtime identity and tag, and keep them as projections over the same session records rather than duplicating session state.

## Implementation checklist

- Update the Vue card/sidebar component and the session browser prefs client store/API together; do not add UI-only tag state.
- Add/extend server controller, route, and persistence normalization for tag definitions and assignments.
- Add focused client tests for layout order, rounded-square avatar rendering, avatar identity label, preview-without-author-prefix, custom tag row contents, context-menu create/remove/assign-existing/edit/delete tag behavior, toolbar filter ordering, profile/runtime filtering, tag filtering, and palette enforcement.
- Add server/store tests for persisted tag prefs, reusable definition update/delete, and normalization.
- Custom tags are added from the session row right-click/context menu, not via an inline `+` button in the row.
- After commit/push to `origin/dev`, restart `hermes-web-ui-dev.service` and verify `/health` reports the pushed commit before calling the dev deploy done.

## Pitfalls

- Do not place profile/runtime in the title row; it makes the first line noisy and competes with the session title.
- Do not put the message author prefix back into the preview row when the card already has profile/runtime identity metadata.
- Do not expose the legacy `badge` term in user-facing UI for this surface after the rename; keep it only as an internal compatibility name when needed.
- Do not report the request as completed until focused tests are green, build/browser QA are complete, the commit is pushed to `origin/dev`, the dev service is restarted, and `/health` shows the pushed commit.
- Do not treat successful unit tests as enough for this surface: card spacing, avatar anchoring, popover/filter behavior, and persisted tag display need browser QA on `#/hermes/chat`.
