# Dev/prod access and profile drift

Use when `app.dev.kiraproject.ru` has current code but profiles, users, access, model visibility, or UI settings differ from `app.kiraproject.ru`.

## Root cause pattern

Live-dev and prod intentionally run as separate runtime/state contours. Current code deployment does not imply prod-like access data.

Typical split:

```txt
DEV:
HERMES_WEB_UI_HOME=/home/werserk/.hermes-web-ui-dev
HERMES_WEBUI_STATE_DIR=/home/werserk/.hermes-web-ui-dev
HERMES_HOME=/home/werserk/.hermes/profiles/hermes-web-ui-dev
DB=/home/werserk/.hermes-web-ui-dev/hermes-web-ui.db
service=hermes-web-ui-dev.service
ports=8647/8649

PROD:
HERMES_WEB_UI_HOME=/home/werserk/.hermes-web-ui
HERMES_WEBUI_STATE_DIR=/home/werserk/.hermes-web-ui
HERMES_HOME=/home/werserk/.hermes/profiles/kira
DB=/home/werserk/.hermes-web-ui/hermes-web-ui.db
service=hermes-web-ui.service
port=8648
```

If dev has current `origin/dev` but wrong users/profiles, treat it as **configuration/state drift**, not as proof that the feature deployment failed.

## Verification pattern

Compare unit state first:

```bash
systemctl --user show hermes-web-ui-dev.service -p WorkingDirectory -p Environment --no-pager
systemctl --user show hermes-web-ui.service -p WorkingDirectory -p Environment --no-pager
```

Compare safe DB tables without dumping secrets:

```bash
python - <<'PY'
import sqlite3
for label,path in [('dev','/home/werserk/.hermes-web-ui-dev/hermes-web-ui.db'),('prod','/home/werserk/.hermes-web-ui/hermes-web-ui.db')]:
    print('\n==', label)
    con=sqlite3.connect(path); con.row_factory=sqlite3.Row
    for t in ['users','user_profiles']:
        print('table', t)
        for r in con.execute(f"select * from {t}"):
            d=dict(r)
            for k in list(d):
                if any(s in k.lower() for s in ['password','hash','token','secret','key']):
                    d[k]='[REDACTED]'
            print(d)
PY
```

Check config drift:

```bash
ls -la /home/werserk/.hermes-web-ui-dev/config.json /home/werserk/.hermes-web-ui/config.json
```

## Safe repair principle

Do **not** copy the whole prod DB over dev by default: it can overwrite sessions, local QA users, device rows, runtime/browser prefs, WAL state, and dev-only test data.

Preferred repair after explicit approval:

1. stop or quiesce dev if writes are possible;
2. backup `/home/werserk/.hermes-web-ui-dev/hermes-web-ui.db`;
3. sync only the intended access/config surface (`users`, `user_profiles`, safe `config.json`, and any explicitly needed preference tables);
4. decide explicitly whether dev should keep `HERMES_HOME=/home/werserk/.hermes/profiles/hermes-web-ui-dev` or use the same profile root as prod;
5. restart `hermes-web-ui-dev.service`;
6. verify public `/health`, login, visible profiles, and one profile-bound chat smoke test.

Ask before changing access data: users/profiles/passwords/roles are security-sensitive and user-visible.
