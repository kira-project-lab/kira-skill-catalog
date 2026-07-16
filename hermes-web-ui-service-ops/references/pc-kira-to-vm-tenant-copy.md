# PC Kira → VM tenant copy

Use when Maxim asks to copy the current PC Kira state/profile into the VM `app.vm.kiraproject.ru` contour.

## Principle

Do not assume the public VM route points at the generic preview service or the tenant you last touched. First identify the **actual Caddy upstream**, then map that port to the running process environment and state paths.

This is a point-in-time copy, not production cutover. Keep `app.kiraproject.ru` and the PC gateway untouched unless Maxim separately approves cutover.

## Preflight: find the real target

On `kira-main-ops-01`:

```bash
sudo grep -n 'app.vm.kiraproject.ru' -A3 /opt/kira/compose/ops/caddy/Caddyfile
sudo ss -ltnp | grep -E '2864|2865|18648'
for pid in $(pgrep -f 'dist/server/index.js'); do
  echo "PID=$pid"
  sudo sh -c "tr '\0' '\n' < /proc/$pid/environ" |
    grep -E '^(PORT|HERMES_WEB_UI_HOME|HERMES_WEBUI_STATE_DIR|HOME|HERMES_HOME)='
done
```

If Caddy says `app.vm.kiraproject.ru -> 172.17.0.1:<port>`, the target is the process whose `PORT=<port>`. Use its `HERMES_WEB_UI_HOME` and `HERMES_HOME`, not a guessed `/data/kira/state/hermes-web-ui-preview` path.

Pitfall from 2026-06: `app.vm.kiraproject.ru` pointed to `172.17.0.1:28650`, whose state was `usr_polina`, while earlier fixes had been applied to `usr_test_001` / `28648`. Browser login then failed or showed the wrong Kira.

## Local snapshot source

PC production baseline is usually:

```text
Web UI state: /home/werserk/.hermes-web-ui
Hermes profile: /home/werserk/.hermes/profiles/kira
Canonical profile source: /home/werserk/2-kira/kira-hermes-profile/profile
```

Use SQLite backup API for live DBs:

```python
import sqlite3
for src, dst in [
    ('/home/werserk/.hermes-web-ui/hermes-web-ui.db', '<snap>/web-ui-state/hermes-web-ui.db'),
    ('/home/werserk/.hermes/profiles/kira/state.db', '<snap>/hermes-root/state.db'),
]:
    s = sqlite3.connect(src)
    d = sqlite3.connect(dst)
    s.backup(d)
    d.close(); s.close()
```

Then `rsync` surrounding state/profile files into the snapshot, excluding live SQLite sidecars and rebuildable heavy caches.

Recommended exclusions:

```text
hermes-web-ui.db, hermes-web-ui.db-*, hermes.db, server.pid, server.log, logs/
state.db, state.db-*
cache/, audio_cache/, browser-profiles/
home/.cache/, home/.npm/, home/.config/google-chrome/, home/.config/chromium/, home/.local/share/Trash/
```

Also consider excluding `home/go/pkg/mod/`: Go module caches contain read-only files and can make local cleanup noisy unless you `chmod -R u+rwX` before removing the staging tree.

## VM apply workflow

1. Copy snapshot to VM staging, e.g. `/tmp/kira-vm-copy-<UTC>`.
2. Stop only the target tenant service, not PC prod and not unrelated VM tenants.
3. Move current target `web-ui-state` and `hermes-root` into rollback:

```bash
ROLL=/data/kira/rollback/app-vm-copy-$(date -u +%Y%m%dT%H%M%SZ)
sudo mkdir -p "$ROLL"
sudo systemctl stop <target-service>.service
sudo mv "$TARGET/web-ui-state" "$ROLL/web-ui-state.before"
sudo mv "$TARGET/hermes-root" "$ROLL/hermes-root.before"
```

4. Copy snapshot into the target paths:

```bash
sudo mkdir -p "$TARGET/web-ui-state" "$TARGET/hermes-root"
sudo rsync -a --delete "$STAGE/web-ui-state/" "$TARGET/web-ui-state/"
sudo rsync -a --delete "$STAGE/hermes-root/" "$TARGET/hermes-root/"
sudo chown -R <tenant-linux-user>:<tenant-linux-user> "$TARGET/web-ui-state" "$TARGET/hermes-root"
sudo chmod 700 "$TARGET" "$TARGET/web-ui-state" "$TARGET/hermes-root"
sudo rm -f "$TARGET"/web-ui-state/hermes-web-ui.db-{shm,wal} "$TARGET"/hermes-root/state.db-{shm,wal}
```

5. After copying PC DB, re-apply the temporary Web UI password/account expected for browser acceptance, because the copied PC DB may overwrite the VM test credential. Use the Web UI scrypt format from `vm-test-access-password-reset.md`.
6. Start the target tenant service and wait for `/health`.
7. Remove remote staging after verification to recover disk.

## Verification

Verify each layer separately:

```bash
curl -fsS -m 30 http://172.17.0.1:<port>/health
```

Then login via API with the Web UI credentials and check current state:

```text
POST /api/auth/login -> 200
GET /api/auth/me -> expected user/role
GET /api/hermes/profiles -> includes default/profile expected by UI
GET /api/hermes/sessions?limit=5 -> recent PC sessions/titles
```

Finally run browser QA through the public URL:

```text
https://app.vm.kiraproject.ru/#/
```

The browser must pass both gates:

1. Authentik login;
2. Hermes Web UI login.

A successful final screen should show the real PC session list. Example proof shape: titles such as `Материалы хакатон-практики Альфа-Банка`, `Доведение Киры до beta-10`, `Статус развёртывания Киры на VM`.

## Performance and disk notes

- A large copied `state.db` can make the first `/health` and first session-list call slow. Wait and recheck before diagnosing failure.
- Clean staging with permission repair if needed:

```bash
chmod -R u+rwX /tmp/kira-vm-copy-<UTC> 2>/dev/null || true
rm -rf /tmp/kira-vm-copy-<UTC>
```

- Check disk before and after; this copy can consume ~10 GiB plus rollback while staged.
- If rollback is tiny after `mv`, that usually means the prior tenant was minimal; still report the rollback path.

## Report status

Report only after live verification:

- target upstream and tenant path used;
- DB session count;
- browser-visible proof that current sessions appear;
- rollback path;
- disk state.

Do not claim “current Kira copied” from a successful rsync alone.
