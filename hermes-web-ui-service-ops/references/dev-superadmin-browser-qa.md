# Dev Superadmin Browser QA

Use after deploying a Hermes Web UI branch preview or `dev` build to `https://app.dev.kiraproject.ru` when a real browser smoke test is needed.

## Account and secret handling

- Dedicated dev QA account: `kira`, role `super_admin`.
- Read credentials from:

```text
/home/werserk/.hermes-web-ui-dev/secrets/kira-superadmin-credentials.env
```

- File must remain local and `0600`.
- Do **not** print or save the password in memory, reports, screenshots, or logs.
- In live-dev `NODE_ENV=development`, the runtime DB is usually:

```text
/home/werserk/2-kira/hermes-web-ui-dev/packages/server/data/hermes-web-ui.db
```

not the production-like `HERMES_WEB_UI_HOME` DB.

## Token injection pitfall

The browser client expects the bearer token in:

```js
localStorage.setItem('hermes_api_key', token)
```

Do not guess keys such as `auth_token`, `token`, or `hermes_auth_token`; they can leave the browser stuck on the login page even when API login succeeds.

Optional profile hint:

```js
localStorage.setItem('hermes_active_profile_name', 'kira')
```

## Minimal smoke plan

1. `GET /health` and verify:
   - `status=ok`
   - expected `webui_version`
   - expected `runtime`
   - expected `git_branch` / `git_ref`
   - expected `git_commit`
2. `POST /api/auth/login` with the `kira` credentials.
3. `GET /api/auth/me` with the token and verify:
   - `username=kira`
   - `role=super_admin`
   - `status=active`
4. `GET /api/hermes/profiles` and verify at least one usable profile is visible.
5. Browser boot:
   - open the public dev URL;
   - inject `localStorage.hermes_api_key` if using API login;
   - reload;
   - verify the Hermes shell loads and there is no login loop/blank screen.
6. Navigation smoke:
   - `/#/hermes/chat`
   - `/#/hermes/skills`
   - `/#/hermes/settings`
7. Chat non-provider smoke:
   - type a draft in the composer;
   - do not send a real provider request unless the task explicitly requires it.
8. Console gate:
   - collect `pageerror` and console `error` messages;
   - treat missing public assets fetched by UI code as real branch-preview drift, not as harmless noise.

## Useful checks

For static public assets expected by UI code, verify the served URL directly after deploy:

```bash
curl -fsS https://app.dev.kiraproject.ru/skill-recommendations.en.md | head
curl -fsS https://app.dev.kiraproject.ru/skill-recommendations.zh.md | head
```

If Skills page logs `Failed to load skill recommendations: Skill recommendations file was not found`, restore the public markdown files rather than suppressing the error.

## Report shape

Keep the report compact:

```text
QA: <PASS>/<TOTAL> PASS
Runtime: <version>, <branch>, <commit>
Account: kira super_admin verified
Failures:
- <name>: <short cause>
Evidence:
- <report path>
- <screenshot paths if useful>
```
