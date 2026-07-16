# Paperclip entrypoint readiness pattern

Use when implementing a Hermes Web UI entrypoint for an external execution backend such as Paperclip.

## Pattern

1. Keep production checkout untouched unless explicitly deploying; use a dedicated feature worktree/branch.
2. Add server-side BFF endpoint first:
   - protected `/api/hermes/...` route;
   - no direct browser access to backend secrets/tokens;
   - argument arrays for launcher/CLI subprocesses;
   - real external sends require explicit `allowSend`; default to dry-run.
3. Add client helper second:
   - use `request()` so auth and `X-Hermes-Profile` are attached consistently;
   - expose dry-run notification options explicitly;
   - validate required ids before issuing requests.
4. Add visible UI entrypoint third:
   - router route;
   - sidebar item;
   - compact status panel with project id, status, counts, digest;
   - no real notification button by default.
5. Add i18n keys to every locale touched by sidebar/navigation.
6. Verify with focused tests and build:
   - server controller/service tests;
   - client API/view tests;
   - i18n coverage test;
   - `npm run build` before reporting ready.
7. Record readiness evidence in the owning backend checklist when this UI is part of a cross-repo certification.

## Pitfalls

- A server endpoint alone is not a user-facing entrypoint; checklist closure requires a visible route or action in the UI.
- Notification dry-run flags must be boolean-tested to avoid accidental real sends.
- Do not route Paperclip code fixes through Paperclip agents; Kira/Hermes owns Paperclip implementation, Paperclip agents validate behavior only.
