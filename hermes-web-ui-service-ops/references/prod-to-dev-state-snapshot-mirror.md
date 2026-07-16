# Prod → dev state snapshot mirror

Use when `app.dev.kiraproject.ru` should show the same chats, statuses, read state, and profiles as production without making dev live-read or write production state.

## Principle

Do **not** point dev at prod's live DB/profile. Use a one-way snapshot copy:

- prod stays running;
- stop only `hermes-web-ui-dev.service` before mutating dev files;
- keep distinct bridge endpoints (`prod.sock` and `dev.sock`);
- back up dev first;
- copy prod state into dev from a consistent snapshot;
- restore/keep a dev QA login if needed;
- restart only dev and verify prod was unaffected.

This avoids concurrent writes, read-receipt drift, and bridge registry/socket confusion.

## Preflight evidence

```bash
systemctl --user show hermes-web-ui.service hermes-web-ui-dev.service \
  -p Id -p ActiveState -p MainPID -p WorkingDirectory -p Environment --no-pager

curl -fsS http://127.0.0.1:8648/health | jq '{runtime,git_branch,git_ref,git_commit,agent_bridge}'
curl -fsS http://127.0.0.1:8647/health | jq '{runtime,git_branch,git_ref,git_commit,agent_bridge}'
stat -Lc 'path=%n inode=%i mode=%A mtime=%y' /tmp/hermes-agent-bridge*.sock 2>/dev/null || true
```

Expected topology:

```text
PROD HERMES_WEB_UI_HOME=/home/werserk/.hermes-web-ui
PROD HERMES_HOME=/home/werserk/.hermes/profiles/kira
PROD bridge=ipc:///tmp/hermes-agent-bridge-prod.sock

DEV HERMES_WEB_UI_HOME=/home/werserk/.hermes-web-ui-dev
DEV HERMES_HOME=/home/werserk/.hermes/profiles/hermes-web-ui-dev
DEV bridge=ipc:///tmp/hermes-agent-bridge-dev.sock
```

## Safe snapshot workflow

Reusable helper: `references/scripts/prod_to_dev_state_snapshot_mirror.py` implements this flow, including SQLite backups, dev-only stop/start, dev QA login preservation, and optional `--reset-password` in both live-dev auth DB locations. Review constants before running.

1. Create an archive directory under:

```text
/home/werserk/9-archive/hermes-web-ui-dev-prod-state-mirror/<UTC-stamp>/
```

2. Before stopping dev, preserve dev QA access rows from dev Web UI DB (`users`, `user_profiles`) for the configured dev credential username, usually from:

```text
/home/werserk/.hermes-web-ui-dev/secrets/kira-superadmin-credentials.env
```

Important live-dev pitfall: `hermes-web-ui-dev.service` runs with `NODE_ENV=development`, so the active auth DB may be the package-local dev DB, not only `HERMES_WEB_UI_HOME`:

```text
/home/werserk/2-kira/hermes-web-ui-dev/packages/server/data/hermes-web-ui.db
```

Before declaring dev login preserved, inspect/reset the credential user in both likely DBs:

```text
/home/werserk/.hermes-web-ui-dev/hermes-web-ui.db
/home/werserk/2-kira/hermes-web-ui-dev/packages/server/data/hermes-web-ui.db
```

Then verify `/api/auth/login` against both local `http://127.0.0.1:8647` and public `https://app.dev.kiraproject.ru`. Do not print passwords in logs; if rotating, write the local credential file with `0600` and report the new password only to Maxim.

3. Snapshot prod SQLite DBs with SQLite's backup API, not raw copy while live:

- `/home/werserk/.hermes-web-ui/hermes-web-ui.db`
- `/home/werserk/.hermes/profiles/kira/state.db`

4. Back up current dev state:

- `/home/werserk/.hermes-web-ui-dev/hermes-web-ui.db`
- `/home/werserk/.hermes/profiles/hermes-web-ui-dev/state.db`
- `/home/werserk/.hermes/profiles/hermes-web-ui-dev/sessions/`
- `/home/werserk/.hermes/profiles/hermes-web-ui-dev/config.yaml`

5. Stop only dev:

```bash
systemctl --user stop hermes-web-ui-dev.service
```

6. Replace dev state from prod snapshots:

- copy prod Web UI DB snapshot to `/home/werserk/.hermes-web-ui-dev/hermes-web-ui.db`;
- reinsert preserved dev QA user/profile rows if needed;
- copy prod Hermes `state.db` to `/home/werserk/.hermes/profiles/hermes-web-ui-dev/state.db`;
- rsync prod `sessions/` into dev profile `sessions/` with `--delete`;
- copy prod `config.yaml` into dev profile if the goal is prod-like profiles/provider config.

7. Fix ownership to the running user if necessary.

8. Start dev:

```bash
systemctl --user start hermes-web-ui-dev.service
```

## Verification

```bash
systemctl --user is-active hermes-web-ui.service hermes-web-ui-dev.service
curl -fsS http://127.0.0.1:8648/health | jq '{runtime,git_branch,git_ref,git_commit,agent_bridge}'
curl -fsS http://127.0.0.1:8647/health | jq '{runtime,git_branch,git_ref,git_commit,agent_bridge}'
stat -Lc 'path=%n inode=%i mode=%A mtime=%y' /tmp/hermes-agent-bridge*.sock 2>/dev/null || true
journalctl --user -u hermes-web-ui.service --since '10 min ago' --no-pager | grep -E 'unknown run|agent-bridge.*error' || true
journalctl --user -u hermes-web-ui-dev.service --since '10 min ago' --no-pager | grep -E 'unknown run|agent-bridge.*error' || true
```

Then verify dev auth/profile/session APIs without printing secrets:

- dev QA login succeeds;
- `/api/auth/me` returns expected active admin/super-admin;
- `/api/hermes/profiles` includes prod-like profiles;
- `/api/hermes/sessions?limit=5` returns prod-like sessions with `row_state`.

For browser QA, use the existing dev superadmin browser flow and check Chat / Skills / Settings / Paperclip plus console errors.

## Expected drift

A small message-count difference between prod and dev after mirror is normal if prod keeps running during the snapshot window. The snapshot is point-in-time, not live replication.

## Rollback

Stop dev, restore the archived dev DB/profile files from the backup directory, start dev, and rerun the same health/auth/session checks. Prod does not need rollback because it was never stopped or mutated.
