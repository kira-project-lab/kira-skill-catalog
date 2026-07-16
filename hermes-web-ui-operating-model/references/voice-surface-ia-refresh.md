# Voice surface IA refresh

## Durable pattern

When the voice panel starts reading as an admin console instead of a product surface, split it into two explicit user intents:

- `Speak` — the minimal composer for getting output now.
- `Voices` — the manager/editor for inspecting and changing voice definitions.

Keep the surface visually similar, but reduce header clutter and move technical/runtime detail behind disclosure.

## Contract used in the refreshed surface

- Header shows status-first runtime metadata only.
- Technical/runtime details are secondary and collapsed by default.
- `Speak` uses a compact composer and should not expose lifecycle management controls.
- `Voices` owns the catalog, details panel, and lifecycle actions.
- The selected voice detail card should make the current record obvious with explicit fields such as:
  - id
  - status
  - mode
  - language
  - model
  - revision
  - last updated
  - reference text
  - description
  - notes
- Group actions by intent instead of placing all buttons in one row:
  - routine / normal operations
  - lifecycle operations
  - danger zone

## Important behavior rules

- Preview can work for draft or inactive voices when the operation is read-only or non-publishing.
- Generation should require an active voice.
- The catalog should not duplicate preset IDs; dedupe at catalog construction time, not only in the UI.
- When the picker depends on voice status, refresh the composer picker after catalog mutations so Speak stays in sync with Voices.

## Verification pattern

- Update UI asset tests to assert the new surface names and critical detail-panel fields.
- Update scenario tests so they activate a voice when the scenario is about generation success, and only leave it inactive when the scenario is explicitly about inactive handling.
- Verify the live panel in browser after the change; do not trust static markup alone.
