# ADR-005 session read/runtime status notes

Session-specific detail from the ADR-005 implementation and verification pass.

## What this session proved

- `running` must be rendered as the primary/active blue tone, not green.
- `streaming` should use the same active tone as `running` when it represents an in-progress runtime state.
- Browser-visible read receipts should be gated on **actual presence**, not just a bare API call.
- The latest relevant message for a read receipt is the most recent non-user item in the session flow (`assistant`, `tool`, or `command`), not the latest message overall.

## Practical gating recipe

When implementing or reviewing read receipts in Hermes Web UI, verify all of these before sending a receipt:

1. the session is the active route/session;
2. the page has focus;
3. `document.visibilityState === 'visible'`;
4. the latest relevant message is currently visible in the viewport;
5. the message has remained visible for a dwell period before issuing the receipt.

## Verification pattern

For this class of change, verify in three layers:

- unit tests for the gating rule and status mapping;
- `npm run build` to catch integration regressions;
- live-dev `/health` plus browser smoke-check to confirm the running host picked up the intended commit and the UI renders the new semantics.

## Session note

This was implemented during the live-dev flow for `hermes.dev.ops.kiraproject.ru` and verified against the running service commit reported by `/health`.
