# VM test-access password reset

Use this when Maxim needs temporary browser/login credentials for VM Web UI acceptance across Authentik and Hermes Web UI accounts.

## Principle

Do **not** try to reveal existing passwords. Auth systems should only expose hashes. Generate fresh temporary passwords, set them, verify them, give Maxim the temporary values, and tell him to rotate after testing.

## Scope guard

- Use only for explicit access/testing requests from Maxim.
- Do not enable Telegram or change production `app.kiraproject.ru` as part of this flow.
- Keep the PC fallback and VM gateway state unchanged unless the user separately asks for cutover.
- Never commit generated credentials or password hashes.

## Authentik reset pattern

1. Generate random temporary passwords outside Git, with `umask 077`.
2. Copy the temporary credential JSON into the Authentik server container only for the reset.
3. Use Django ORM to set and verify passwords.

Example pattern:

```bash
OUT=/tmp/kira-test-access-$(date -u +%Y%m%dT%H%M%SZ).json
umask 077
python3 - <<'PY' > "$OUT"
import json, secrets
users=["werserk","sonya","polina"]
alphabet="ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#%+-_"
creds={u:{"authentik":"TmpA-"+"".join(secrets.choice(alphabet) for _ in range(24)),
          "hermes_web_ui":"TmpW-"+"".join(secrets.choice(alphabet) for _ in range(24))} for u in users}
print(json.dumps(creds, ensure_ascii=False, indent=2))
PY

docker cp "$OUT" kira-ops-authentik-server-1:/tmp/kira-test-access.json
cat > /tmp/reset_authentik_passwords.py <<'PY'
import json
from authentik.core.models import User
creds=json.load(open("/tmp/kira-test-access.json"))
for name, vals in creds.items():
    user=User.objects.get(username=name)
    user.set_password(vals["authentik"])
    user.save(update_fields=["password"])
for name, vals in creds.items():
    assert User.objects.get(username=name).check_password(vals["authentik"]), name
print("AUTHENTIK_RESET_AND_VERIFIED:" + ",".join(creds.keys()))
PY

docker exec -i kira-ops-authentik-server-1 /ak-root/.venv/bin/python /manage.py shell < /tmp/reset_authentik_passwords.py

docker exec kira-ops-authentik-server-1 rm -f /tmp/kira-test-access.json
```

## Hermes Web UI reset pattern

Hermes Web UI stores local users in SQLite, but **the public VM route may not use the preview DB**. Before editing, identify the actual upstream for the public host:

- read Caddy route for `app.vm.kiraproject.ru`;
- map its upstream port to the running process/service;
- read that process environment for `HERMES_WEB_UI_HOME` / `HERMES_WEBUI_STATE_DIR`;
- edit the `hermes-web-ui.db` under that state directory, not the similarly named preview DB.

Known VM shape can change during beta routing. In the 2026-06 acceptance session it changed from `usr_test_001`/`28648` to `usr_polina`/`28650`, while both services were still running. Treat the Caddy route as source of truth, not this note.

Observed route examples:

- `http://app.preview.kiraproject.ru` → `172.17.0.1:18648` → `/data/kira/state/hermes-web-ui-preview/hermes-web-ui.db`
- earlier `https://app.vm.kiraproject.ru` → Authentik forward-auth → `172.17.0.1:28648` → `/data/kira/users/usr_test_001/assistants/kira/web-ui-state/hermes-web-ui.db`
- later `https://app.vm.kiraproject.ru/#/` → Authentik forward-auth → `172.17.0.1:28650` → `/data/kira/users/usr_polina/assistants/kira/web-ui-state/hermes-web-ui.db`

Before editing, copy the resolved DB as a local rollback backup.

Current scrypt format:

```text
scrypt:<salt_hex>:<hash_hex>
```

Current hash parameters:

```text
hashlib.scrypt(password, salt=salt.encode(), n=16384, r=8, p=1, dklen=64)
```

Example update/upsert pattern for the public VM Web UI tenant:

```bash
DB=/data/kira/users/usr_test_001/assistants/kira/web-ui-state/hermes-web-ui.db
cp -a "$DB" "$DB.before-test-password-reset-$(date -u +%Y%m%dT%H%M%SZ)"

python3 - <<'PY' "$OUT" "$DB"
import json, sqlite3, time, secrets, hashlib, sys
creds=json.load(open(sys.argv[1]))
DB=sys.argv[2]

def hash_password(password):
    salt=secrets.token_hex(16)
    h=hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1, dklen=64).hex()
    return f"scrypt:{salt}:{h}"

con=sqlite3.connect(DB)
now=int(time.time()*1000)
for name, vals in creds.items():
    row=con.execute("select id from users where username=?", (name,)).fetchone()
    if row:
        con.execute(
            "update users set password_hash=?, updated_at=?, status='active' where username=?",
            (hash_password(vals["hermes_web_ui"]), now, name),
        )
    else:
        con.execute(
            "insert into users (username, password_hash, role, status, created_at, updated_at) values (?, ?, 'super_admin', 'active', ?, ?)",
            (name, hash_password(vals["hermes_web_ui"]), now, now),
        )
con.commit()
for name, vals in creds.items():
    ph=con.execute("select password_hash from users where username=?", (name,)).fetchone()[0]
    scheme,salt,expected=ph.split(":")
    actual=hashlib.scrypt(vals["hermes_web_ui"].encode(), salt=salt.encode(), n=16384, r=8, p=1, dklen=len(bytes.fromhex(expected))).hex()
    assert scheme == "scrypt" and actual == expected, name
print("WEBUI_RESET_AND_VERIFIED:" + ",".join(creds.keys()))
PY

systemctl restart kira-beta-webui-usr-test-001.service
```

Pitfall: updating `/data/kira/state/hermes-web-ui-preview/hermes-web-ui.db` can verify locally on `127.0.0.1:18648` while `https://app.vm.kiraproject.ru/` still rejects the password because Caddy sends that public host to the beta tenant on port `28648`.

## Browser acceptance after reset

For `app.vm.kiraproject.ru`, acceptance has two credential gates:

1. Authentik at `auth.kiraproject.ru` using the Authentik password.
2. Hermes Web UI login using the Web UI local account password.

Verify both, in a browser, until the Hermes Web UI shell opens. A successful API login against the wrong local port is not enough.

## Report format

Use the same reset principle for the Werserk ops Authentik at `https://auth.ops.werserk.com/`, but target the Werserk VM and container names:

```text
ssh target: werserk-main-ops-01
container: werserk-ops-authentik-server-1
username: werserk
public URL: https://auth.ops.werserk.com/
```

Keep generated credential JSON and reset scripts in `/tmp`, copy them into the container only for the reset, run `/ak-root/.venv/bin/python /manage.py shell`, verify with `check_password`, then remove temporary files from both the host and container.

## Browser acceptance gate

If Maxim sets the acceptance criterion as “you independently authenticate through web,” do not stop at database/ORM password verification. Complete a real browser login:

1. Open the public Authentik URL.
2. Enter username and the newly generated temporary password.
3. Submit the flow.
4. Verify the post-login Authentik Application Dashboard or another authenticated-only page is visible.
5. Report only the concise result and visible authenticated evidence, not command transcripts or hashes.

For `auth.ops.werserk.com`, expected successful evidence is the Authentik **Application Dashboard** with Werserk applications such as Grafana, Prometheus, Loki, Registry, Kuma, Pi Home Admin, or Codex LB.

## Browser acceptance after reset

When Maxim's acceptance criterion is browser login, do not stop at ORM `check_password()` or a route `302`. Complete the web flow yourself:

1. Open the exact public Authentik host.
2. Enter username.
3. Enter the newly generated temporary password.
4. Verify that the page reaches the Authentik Application Dashboard or the requested protected application.
5. Report the visible dashboard/application names as evidence.

If the browser says `Invalid password` after a prior reset, treat the password as stale or mismatched for that Authentik instance. Generate and set a fresh password on the correct VM/container, then retry the browser flow. Do not keep retyping the same failed password.

## Host/container mapping pitfalls

Keep the Kira and Werserk Authentik instances separate:

- Kira VM: `https://auth.kiraproject.ru/`, SSH `kira-main-ops-01`, container `kira-ops-authentik-server-1`.
- Werserk ops VM: `https://auth.ops.werserk.com/`, SSH `werserk-main-ops-01`, container `werserk-ops-authentik-server-1`.

Use the public hostname from the user's request to select the target. Do not reuse a temporary password from another Authentik instance unless browser acceptance on that exact host already passed.

## Report format

Keep the final response compact:

- Say old passwords were not revealed; temporary passwords were reset and verified.
- Provide the exact Authentik URL and username.
- Provide credentials grouped by account.
- Include browser acceptance evidence when performed: dashboard reached, visible app names/count.
- Ask Maxim to rotate after testing.

Do not include command transcripts or hashes unless Maxim asks for audit details.

