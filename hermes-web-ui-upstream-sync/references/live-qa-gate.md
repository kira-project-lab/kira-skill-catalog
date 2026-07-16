# Upstream sync live QA gate

Use this reference near the end of a Hermes Web UI upstream sync, after local `harness:check`, `test`, `test:coverage`, `test:e2e`, and `build` pass.

## Purpose

Local tests prove the integration branch is coherent; live-dev QA proves the deployed preview is usable with real auth, real profile state, served assets, and browser console behavior.

## Dev account

Use the dedicated dev QA account:

- username: `kira`
- role: `super_admin`
- credential file: `/home/werserk/.hermes-web-ui-dev/secrets/kira-superadmin-credentials.env`

Do not print the password. For detailed credential handling and browser-token injection, see `hermes-web-ui-service-ops/references/dev-superadmin-browser-qa.md`.

## Minimum gate

1. Deploy branch preview, e.g. `bash scripts/deploy-dev-branch.sh preview/upstream-<version>`.
2. Verify public health:

```bash
curl -fsS https://app.dev.kiraproject.ru/health | jq '{status,webui_version,runtime,git_branch,git_commit}'
```

3. Login as `kira` via API or browser UI.
4. Confirm `/api/auth/me` returns `kira`, `super_admin`, `active`.
5. Confirm `/api/hermes/profiles` is accessible.
6. Browser-smoke these routes:
   - `/#/hermes/chat`
   - `/#/hermes/skills`
   - `/#/hermes/settings`
7. Type a chat draft without sending a provider request.
8. Capture screenshots and console/page errors.

## What counts as a blocker

- Login loop / blank shell.
- `/api/auth/me` fails or returns the wrong user/role.
- Chat route cannot render session list/composer.
- Skills/settings routes blank or throw page errors.
- Uncaught browser page errors.
- Console errors from required assets or required data loaders.

## What can be a non-blocking follow-up

- Optional content missing with a graceful UI fallback, if the feature is not required for sync acceptance. Still record it. Example: missing `skill-recommendations.<locale>.md` on Skills can be a console-cleanliness issue; fix by adding the static file or making the loader quiet on 404.

## Report shape

```text
Live QA: PASS / FAIL / BLOCKED
Branch: <branch>
Commit: <sha>
Version: <version>
Account: kira super_admin verified
Routes: chat <pass/fail>, skills <pass/fail>, settings <pass/fail>
Console: <clean/errors>
Screenshots/report: <paths>
Merge recommendation: <merge / hold>
```
