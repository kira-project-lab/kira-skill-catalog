# Beta admin route hardening

Use when moving Hermes Web UI toward a multi-user / beta-user contour without breaking `app.kiraproject.ru`.

## Lesson

Plans and architecture docs are only artifacts. Do not report the product goal as complete until a working, verified product contour exists. For long-running product goals, report concrete implementation steps as partial progress and name the remaining gates.

## Safe next-step pattern

1. Work in `/home/werserk/2-kira/hermes-web-ui-dev`, not production `/home/werserk/2-kira/hermes-web-ui`.
2. Re-check git status for prod and dev checkouts before edits.
3. Find routes that mutate profile/runtime/server state and gate them with `requireSuperAdmin`.
4. Preserve read/list/status routes that are already user/profile scoped.
5. Add a source-contract test for route middleware so authorization regressions are visible without needing live credentials.
6. Run the focused test and `npm run build`.
7. Verify production public health (`https://app.kiraproject.ru/` and `/health`) after local/dev changes; this confirms the protected prod surface is still alive, not that the change is deployed.

## Concrete example from the first hardening step

`packages/server/src/routes/hermes/profiles.ts` should require `requireSuperAdmin` for profile lifecycle/runtime control:

- `POST /api/hermes/profiles` create profile
- `POST /api/hermes/profiles/:name/restart` restart profile runtime
- `POST /api/hermes/profiles/:name/gateway/restart` restart gateway
- `DELETE /api/hermes/profiles/:name` delete profile
- `POST /api/hermes/profiles/:name/rename` rename profile
- `POST /api/hermes/profiles/:name/export` export profile
- `POST /api/hermes/profiles/import` import profile

Keep profile reads and per-profile metadata/status user-scoped unless the product policy changes.

## Reporting contract

Say: “Implemented one hardening step: …; goal remains incomplete.”

Do not say: “Goal reached/completed” after creating plans, docs, or a single hardening patch.
