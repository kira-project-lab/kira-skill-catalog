# Account-scoped UI preferences

Use this when a Hermes Web UI setting must follow the signed-in user across devices and differ between users.

## Pattern

- Treat the server preference as the source of truth; use `localStorage` only as a fallback, legacy cache, or offline optimistic cache.
- Scope persistence by authenticated `user_id`, not by profile, browser, or device.
- Prefer a small keyed preferences table over one-off local-only state:
  - `user_id`
  - `preference_key`
  - JSON payload/value
  - timestamps
  - index on `user_id`
- Version preference payloads (`version: 1`) so future migrations can distinguish shape changes from invalid data.
- Keep normalization in both client and server layers: invalid/missing payloads should converge to the product default rather than leaking raw JSON into UI state.
- Register routes in the protected Hermes route chain; preferences should not be readable or writable without an authenticated user.

## Client implementation shape

- Put API wrappers under `packages/client/src/api/hermes/<preference>.ts` using the existing `request(...)` helper style.
- Keep pure default/normalization helpers in `packages/client/src/data/...` so tests can lock the contract without mounting the UI.
- Expose composable methods such as `load()` and `save()`; call `load()` from the relevant mounted surfaces so multiple entrypoints converge on the account state.
- Preserve fallback behavior for legacy `localStorage` users, but do not describe local storage as the sync source.

## Server implementation shape

- Add a storage layer under `packages/server/src/db/hermes/...-store.ts` rather than putting JSON/SQL logic directly in the controller.
- Add protected controller + route modules under `packages/server/src/controllers/hermes/` and `packages/server/src/routes/hermes/`.
- Register the schema in `packages/server/src/db/hermes/schemas.ts` through the existing `syncTable(...)` path.
- Add the route module to `packages/server/src/routes/index.ts` before proxy/catch-all routes.

## Test contract

Use TDD for behavior/contract changes:

- Server tests should prove:
  - default preference for a new user;
  - per-user isolation/persistence;
  - auth guard.
- Client tests should prove:
  - product default visible/hidden set;
  - invalid/partial payload normalization;
  - `load()` uses server state;
  - `save()`/bulk/reset operations write through the API;
  - fallback/local cache behavior stays non-authoritative.

## Example: Activity Rail visibility

The activity rail visibility setting uses this pattern:

- API: `GET/PUT /api/hermes/user-preferences/activity-rail`
- Server key: `activityRail`
- Client fallback key: `hermes.layout.activityRail.v1`
- Default visible set: `chat`, `search`, `memory`, `channels`, `settings`
- Required/non-hideable items: `chat`, `settings`

## Pitfalls

- Do not leave a user-facing preference in browser-only `localStorage` when the requirement says sync between devices or separate users.
- Do not scope UI preferences to a Hermes profile unless the product requirement is explicitly profile-specific.
- Do not finalize with only a local build if Maxim expects the live-dev site to reflect the change; compare `/health` `git_commit` to the pushed commit and restart/update the dev service if needed.
