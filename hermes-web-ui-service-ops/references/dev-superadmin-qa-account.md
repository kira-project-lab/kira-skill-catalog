# Dev superadmin QA account for Hermes Web UI

Use when Kira needs a durable account for browser QA on `https://app.dev.kiraproject.ru`.

## Current Kira dev QA account

- Username: `kira`
- Role: `super_admin`
- Credential file: `/home/werserk/.hermes-web-ui-dev/secrets/kira-superadmin-credentials.env`
- File mode should be `0600`.
- Do not save the password in memory or chat transcripts; read it from the credential file when needed.

Expected env keys:

```bash
HERMES_WEB_UI_DEV_USERNAME=kira
HERMES_WEB_UI_DEV_PASSWORD=<secret>
HERMES_WEB_UI_DEV_ROLE=super_admin
```

## Critical DB path pitfall

Live-dev runs with `NODE_ENV=development`. In this mode the Web UI DB is not the production-like state DB under `HERMES_WEB_UI_HOME`.

For `hermes-web-ui-dev.service`, the active user DB is usually:

```text
/home/werserk/2-kira/hermes-web-ui-dev/packages/server/data/hermes-web-ui.db
```

Not:

```text
/home/werserk/.hermes-web-ui-dev/hermes-web-ui.db
```

Before creating/resetting a dev Web UI user, verify the active service and DB path:

```bash
systemctl --user show hermes-web-ui-dev.service -p MainPID -p WorkingDirectory -p ExecStart -p Environment --no-pager
curl -fsS http://127.0.0.1:8647/health | jq '{status,runtime,git_branch,git_commit,webui_version}'
```

Then inspect the development DB:

```bash
sqlite3 /home/werserk/2-kira/hermes-web-ui-dev/packages/server/data/hermes-web-ui.db \
  "select id, username, role, status from users where username='kira';"
```

## Password hash format

The `users.password_hash` format is:

```text
scrypt:<salt_hex>:<hash_hex>
```

Use Node-compatible scrypt parameters from `users-store.ts`; verify login after updating rather than assuming the row is valid.

## Verification

After creating or rotating the account:

1. Restart live-dev so any cached DB/user state is clean:

```bash
systemctl --user restart hermes-web-ui-dev.service
```

2. Wait for local health:

```bash
for i in {1..60}; do
  curl -fsS http://127.0.0.1:8647/health >/tmp/dev-health.json 2>/dev/null && break
  sleep 1
done
cat /tmp/dev-health.json | jq '{status,runtime,git_branch,git_commit,webui_version}'
```

3. Verify login through the public dev URL. Current login response uses `token` (not always `accessToken`), and `/api/auth/me` nests the user under `user`:

```bash
set -a; . /home/werserk/.hermes-web-ui-dev/secrets/kira-superadmin-credentials.env; set +a
body=$(node -e 'console.log(JSON.stringify({username:process.env.HERMES_WEB_UI_DEV_USERNAME,password:process.env.HERMES_WEB_UI_DEV_PASSWORD}))')
token=$(curl -fsS -X POST https://app.dev.kiraproject.ru/api/auth/login \
  -H 'content-type: application/json' --data "$body" | jq -r '.token // .accessToken')
curl -fsS https://app.dev.kiraproject.ru/api/auth/me \
  -H "Authorization: Bearer $token" | jq '{username:.user.username, role:.user.role, status:.user.status, id:.user.id}'
```

Expected:

```json
{"username":"kira","role":"super_admin","status":"active"}
```

## Browser QA use

Use this account for dev/preview browser QA only. It is intentionally `super_admin` so Kira can access all dev profiles/features during integration testing. Do not copy this account to production unless Maxim explicitly asks.
