# Upstream 0.6.18 Certification Lessons

Context: the `integration/upstream-0.6.18` branch was certified locally and deployed to live-dev before promotion review.

## Runtime dependency gate

A green build/test suite is not enough when upstream introduces lazy/dynamic imports. In this sync, live-dev initially failed to render a route because `VoiceDialogueControls.vue` dynamically imported `wavesurfer.js` but the root manifest did not declare the dependency.

Reusable pattern:

1. When browser QA shows `Failed to fetch dynamically imported module`, inspect the transitive component chain behind the route, not just the named view file.
2. Search dynamic imports for package names and verify they are declared in root `package.json` and lockfile.
3. Add a focused regression test that asserts dynamically imported runtime packages are declared. This catches production install/runtime failures earlier than Vite's dev-server error.
4. Re-run the focused component test plus full build/browser smoke after adding the dependency.

Do not preserve the transient failure as a rule that Vite/browser QA is broken; the durable rule is to test manifest coverage for dynamic runtime imports.

## Authenticated app-effects gate

After upstream syncs touching routing/auth/app startup, test that authenticated app effects restart after login and after leaving the login route. Health polling, model loading, and similar app-level effects can silently fail if the root effect is skipped while the app begins on the login route.

Reusable pattern:

- Add a focused client regression around the root app/auth transition.
- Verify the effect starts only after authentication and route transition, not before login.
- Browser QA should include login + immediate route render, not only token injection into an already-authenticated app.

## PR-to-dev CI bootstrap caveat

GitHub evaluates `pull_request` workflow configuration from the base branch. If `origin/dev` does not already list `dev` under `pull_request.branches`, adding that change inside the integration PR does not cause checks to appear on that same PR.

When integrating to `dev`:

1. Check whether workflows on the current base branch already trigger for `pull_request` into `dev` before relying on PR checks as a gate.
2. If missing, either land a small CI-bootstrap change into `dev` first, or explicitly state that current promotion depends on local/live-preview certification plus manual approval.
3. Record the caveat in the PR body so review does not wait on checks that GitHub cannot create from the PR's own workflow changes.

## Validation shape that worked

Use a layered gate for broad upstream sync certification:

- focused regression tests for newly discovered contracts;
- `npm run harness:check`;
- full `npm run test`, `npm run test:coverage`, `npm run test:e2e`, `npm run build`;
- `git diff --check`;
- CodeGraph refresh/status as navigation aid, not runtime proof;
- deploy exact integration head to live-dev;
- public `/health` evidence for `webui_version`, `runtime`, `git_branch`, `git_ref`, and `git_commit`;
- browser QA of critical routes with console inspected.

Report the branch as certified locally only after the exact deployed commit matches the tested commit.