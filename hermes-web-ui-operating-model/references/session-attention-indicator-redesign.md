# Session attention indicator redesign

Use this note when changing Hermes Web UI session-row attention/status visuals.

## Product direction

Maxim wanted the session status marker to attract more attention while keeping the messenger-like session list clean. The chosen pattern is a **dual indicator**:

1. **Left vertical status rail** on the row for peripheral scanning.
2. **Right-side color dot** in the preview/message row for precise status confirmation.

No text label is shown beside the dot; keep `aria-label` and `title`/tooltip semantics.

## State mapping

| State | Rail | Dot | Halo/ring | Animation | Shape |
|---|---|---|---|---|---|
| read/idle | none | none | none | none | none |
| unread complete | green | green | light halo | none | circle |
| running | blue | blue | pulse halo | yes | circle |
| queued | cyan/blue | cyan/blue | pulse halo | yes | circle |
| needs approval | amber | amber | ring | none | circle |
| needs clarification | amber | amber | ring | none | circle |
| error | red | red | ring | none | diamond |

## Implementation contract

- Keep the current ADR priority semantics: error > needs action > running/queued > unread > read/idle.
- Keep read/idle visually quiet: no rail and no dot.
- Do not animate approval, clarification, error, or unread-complete. Animate only running and queued.
- Treat `queued` as a distinct visual tone when a design needs separate running/queued styling; do not automatically collapse it into `running` if the UI contract distinguishes them.
- Use the component root for row-level state, e.g. `data-attention-tone`, so scoped CSS can style the left rail and subtle row tint without leaking logic into parent views.
- Prefer a pseudo-element for the left rail (`::before`) so the template remains stable and accessible.
- Use `box-shadow`/halo for visual prominence; avoid adding visible text labels unless Maxim asks for denser status copy.

## Testing pattern

Add or update focused raw-SFC contract tests before CSS/template changes:

- status state maps to the expected `data-tone` / `data-attention-tone`;
- read/idle has no dot and no attention attribute;
- left rail selector exists (`.session-item[data-attention-tone]::before`);
- high-signal properties are protected: rail width/position, dot size, halo/ring, pulse keyframes, error diamond transform;
- accessibility attributes remain (`role="status"`, `aria-label`, `title`).

Run the targeted session-list test first, then build. For browser-visible work on dev, push `dev`, restart `hermes-web-ui-dev.service`, and verify local + public `/health` commit.