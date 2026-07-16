# Session row status dot — ADR-006 implementation notes

Use this when implementing or reviewing Hermes Web UI chat/session-list row status indicators after ADR-006.

## Contract

Session rows may render exactly one compact status dot, derived from server-authoritative `session.rowState` / `row_state`.

Placement:
- first line: session title + time;
- second line: message preview on the left, one dot on the right edge;
- dot is not an active/current-session marker, pin marker, profile marker, or message-role marker.

Visual quiet state:
- complete/read (`primary: 'idle'` and `read: 'read'`, or equivalent no-attention state) should render no dot unless layout stability explicitly requires a neutral placeholder.

## Priority mapping

Map the highest-priority user-relevant state only:

1. `needs_approval` or `needs_clarification` → waiting/amber.
2. `error` → error/red.
3. `running` or `queued` → running/blue-cyan.
4. `unread` or `read === 'unread' && attention === 'has_new_agent_output'` → unread-complete/green-mint.
5. complete/read/no-attention → no dot.

Use semantic component tokens, not raw colors in logic:

```css
--session-status-waiting: var(--warning, #f59e0b);
--session-status-error: var(--danger, #ef4444);
--session-status-running: var(--info, #38bdf8);
--session-status-unread-complete: var(--success, #34d399);
--session-status-neutral: rgba(var(--text-primary-rgb), 0.24);
```

## Accessibility

Every rendered dot must expose a human-readable `aria-label` and/or `title`, preferably using `row_state.aria_label_key` with existing `rowStatus.*Aria` i18n keys.

Color alone is not enough for assistive tech. The visual UI stays a single dot; the accessible tree gets the status label.

## Tests to add first

For `SessionListItem` or equivalent row component, add RED tests for:
- `needs_approval` + unread → waiting tone;
- `needs_clarification` + read → waiting tone;
- `error` → error tone;
- `running` → running tone;
- `queued` → running tone;
- `unread` → unread-complete tone;
- complete/read → no dot;
- dot is in the second-line preview row;
- dot has `aria-label` / `title`;
- realtime `session.row_state.changed` updates the row via the existing row-state sync path.

## Pitfalls

- Do not resurrect the old fork-era multi-status/title-row status component just to satisfy ADR-006. ADR-006 wants one collapsed dot on the preview row.
- Do not derive the dot from `active`, selected state, pinned state, profile, or local route state.
- Do not bypass `row_state` with ad-hoc client-only `streaming`/`waiting` props unless the server row-state path is unavailable and the ADR is explicitly updated.
- If a prior instruction said “do not return the status dot,” re-check current ADRs: ADR-006 supersedes that for the single server-authoritative preview-row dot.
