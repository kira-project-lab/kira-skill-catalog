# Beta-10 VM acceptance execution notes

Use this reference when executing `kira-assembly/docs/implementation/beta-10-vm-build-and-acceptance-plan.md` or similar Kira beta multi-user VM work.

## Core rule

Do not report beta-10 complete until the acceptance contract is complete. Report each gate as `PASS`, `PARTIAL PASS`, `BLOCKED`, or `PENDING`, and explicitly name remaining gates. Documents, plans, temp-only smoke tests, and partial evidence are subgoals, not completion.

## VM target verification pattern

Do not trust stale inventory names/IPs. First reconcile three sources:

1. `ansible/inventory.generated.ini`
2. current `yc` profile/cloud/folder/instance list
3. SSH config/host key reality

Commands:

```bash
cd /home/werserk/2-kira/kira-ops
sed -n '1,80p' ansible/inventory.generated.ini
yc config list | sed -E 's/(token: ).*/\1***REDACTED***/'
yc resource-manager cloud list --format json
yc resource-manager folder list --cloud-id <cloud-id> --format json
yc compute instance list --folder-id <folder-id> --format json
./bin/kira check vm-beta-readiness
```

If inventory points to one VM but YC access shows a different active VM, stop and document the target mismatch. Do not mutate either VM until the intended beta target is explicit. Treat SSH `REMOTE HOST IDENTIFICATION HAS CHANGED` as a security gate, not a nuisance; verify through YC/trusted channel before changing `known_hosts`.

In the 2026-06-28 beta-10 session, stale generated inventory pointed at `kira-app-01` / `51.250.77.163`, while the current accessible target was `kira-main-ops-01` / `81.26.176.187`. The correct next step was to retarget docs/inventory/evidence to the accessible VM, not provision blindly.

## Read-only VM readiness

Once target is reconciled:

```bash
./bin/kira check vm-beta-readiness
```

The check should prove Ansible ping and read-only VM facts: hostname, OS, `/opt/kira`, `/data/kira/users`, Docker/systemd surfaces. It must not modify VM state.

## If VM cannot fetch GitHub directly

VM-side GitHub SSH/HTTPS may fail because deploy keys/credentials are not present. Do not treat this as a reason to copy a live tree manually. For an acceptance branch, create a git bundle locally and transfer that exact ref:

```bash
cd /home/werserk/2-kira/kira-ops
git bundle create /tmp/kira-ops-beta-10-current.bundle HEAD
scp /tmp/kira-ops-beta-10-current.bundle kira-main-ops:/tmp/kira-ops-beta-10-current.bundle
ssh kira-main-ops
cd /opt/kira/repos/kira-ops-beta-acceptance
git fetch /tmp/kira-ops-beta-10-current.bundle HEAD
git checkout -B beta-10-vm-acceptance-YYYY-MM-DD FETCH_HEAD
git rev-parse HEAD
./bin/kira validate all
```

Record the bundle-backed checkout path and commit in evidence. This preserves Git provenance without requiring live VM GitHub credentials.

## Dummy tenant gate sequence

Run only after VM readiness passes and production fallback health is known.

```bash
cd /opt/kira/repos/kira-ops-beta-acceptance
./bin/kira validate all
sudo ./bin/kira tenant provision-live usr_test_001
scripts/check-beta-tenant-isolation.sh usr_test_001 kira-u-test001
sudo ./bin/kira tenant provision-live usr_test_002
scripts/check-beta-tenant-isolation.sh usr_test_001 kira-u-test001 usr_test_002
scripts/check-beta-tenant-isolation.sh usr_test_002 kira-u-test002 usr_test_001
```

Acceptance evidence must include:

- VM repo path, branch, commit
- `id` output for Linux users
- `stat -c '%a %U:%G %n'` for tenant roots and config files
- negative-read outputs for operator paths and cross-tenant profile denial

## Backup/restore live dummy drill

Temp-only restore smoke is not A11/G9 completion. It is still useful as a VM-side portability check before the live drill. Run it on the VM acceptance checkout and record it as `PARTIAL PASS` only:

```bash
cd /opt/kira/repos/kira-ops-beta-acceptance
./bin/kira smoke beta-restore usr_test_001
```

Portability pitfall: use `python3 -m json.tool`, not bare `python`, in VM smoke scripts; the beta VM may not have a `python` shim even though Python 3 is installed.

A11/G9 needs VM live dummy tenant state. A safe pattern is:

1. seed harmless files under the dummy tenant profile/state/workspace/uploads/exports;
2. write backup to `/data/kira/users/<uid>/backups/<timestamp>`;
3. write `manifest.json`, tarballs, `checksums.sha256`;
4. verify checksums;
5. restore into a clean non-active path such as `/data/kira/restore-drills/<uid>-<timestamp>`;
6. verify required restored files and private permissions;
7. do not restore over active tenant state.

Use root for archive operations when tenant-owned private directories are `0700`; otherwise non-root `cd` into backup paths can fail with permission denied. Preserve final ownership as the tenant user and mode `0700` dirs / `0600` files.

## Disable/re-enable drill status

A tenant-state marker drill is useful but only a partial A12 pass until Auth/Web UI runtime exists.

Pattern:

```bash
sudo ./bin/kira tenant access status usr_test_001
sudo ./bin/kira tenant access disable usr_test_001 beta-disable-drill
sudo stat -c '%a %U:%G %n' /data/kira/users/usr_test_001/.disabled
sudo ./bin/kira tenant access enable usr_test_001 beta-disable-drill
scripts/check-beta-tenant-isolation.sh usr_test_001 kira-u-test001 usr_test_002
```

Report this as `PARTIAL PASS`: marker/private data preservation/re-enable are proven; Authentik/Web UI session revocation and per-user runtime stop remain pending.

## Loopback-only Web UI tenant runtime gate

For A7/A8 before public Authentik/Caddy routing exists, a useful intermediate gate is a loopback-only Web UI runtime for one dummy tenant. This proves that the tenant can run a separate Web UI process under its Linux user and that non-superadmin API calls are denied, without touching `app.kiraproject.ru`.

### Tenant bridge/runtime pitfalls

When the tenant Web UI can authenticate but chat fails, separate three layers before changing policy:

1. **Authentik forward-auth**: browser reaches `app.vm.kiraproject.ru` and the Authentik application allows the user.
2. **Web UI JWT auth**: `/api/auth/login` returns a tenant token; client requests should use `Authorization: Bearer <tenant-token>` and `X-Hermes-Profile: default` where appropriate.
3. **Hermes Agent bridge/provider**: chat run reaches the bridge and then a configured model provider.

Known durable beta-10 pattern:

- Authentik `Permission denied` after login can mean the user is not in the group bound to the Authentik application (for example `kira-users`). Fix the user/application binding; do not bypass Authentik or loosen the app policy.
- Authentik forward-auth does **not** automatically establish the Web UI's JWT session. For smoke tests, log in through Authentik, then establish the Web UI tenant session with `/api/auth/login` using the tenant's own Web UI credentials stored under the tenant `acceptance-secrets`; never print those values.
- A tenant Web UI unit needs an explicit `HERMES_AGENT_ROOT` pointing at the VM Hermes Agent checkout (for example `/opt/kira/services/hermes-agent`) if the tenant runtime cannot read the default discovery path. Otherwise the bridge can exit with a `PermissionError` while looking for `/home/kira/run_agent.py`.
- Do not let multiple tenant units share the default global bridge endpoint `ipc:///tmp/hermes-agent-bridge.sock`. Give each tenant a private endpoint under its Web UI state root, e.g. `ipc:///data/kira/users/<uid>/assistants/kira/web-ui-state/agent-bridge.sock`.
- `HERMES_AGENT_BRIDGE_BASE_HOME` should point at the tenant Hermes root so worker/profile subprocesses stay inside the tenant namespace.
- A successful bridge start is not full runtime success. If chat returns `No inference provider configured`, G7/G8 remain blocked until a tenant-scoped provider key/model is configured; do not copy Maxim/operator `.env` or broad profile secrets into beta tenants without explicit approval.

Pattern:

1. Put the intended Web UI source on the VM from a known Git ref or bundle, e.g. `/opt/kira/repos/hermes-web-ui-beta`, then run `npm ci --ignore-scripts` and `npm run build`.
2. Create tenant-scoped roots under `/data/kira/users/<uid>/assistants/kira/`:
   - `web-ui-state`
   - `hermes-root` with `active_profile=default`
   - workspace/upload/export roots
3. Create a root-owned systemd service that runs as the tenant Linux user with loopback bind and tenant-only write paths:

```ini
User=kira-u-test001
Group=kira-u-test001
WorkingDirectory=/opt/kira/repos/hermes-web-ui-beta
Environment=NODE_ENV=production
Environment=PORT=28648
Environment=BIND_HOST=127.0.0.1
Environment=PROFILE=default
Environment=HERMES_HOME=/data/kira/users/usr_test_001/assistants/kira/hermes-root
Environment=HERMES_WEB_UI_HOME=/data/kira/users/usr_test_001/assistants/kira/web-ui-state
Environment=HERMES_WEBUI_STATE_DIR=/data/kira/users/usr_test_001/assistants/kira/web-ui-state
Environment=HERMES_AGENT_ROOT=/opt/kira/services/hermes-agent
Environment=HERMES_AGENT_BRIDGE_BASE_HOME=/data/kira/users/usr_test_001/assistants/kira/hermes-root
Environment=HERMES_AGENT_BRIDGE_ENDPOINT=ipc:///data/kira/users/usr_test_001/assistants/kira/web-ui-state/agent-bridge.sock
Environment=UPLOAD_DIR=/data/kira/users/usr_test_001/uploads
Environment=WORKSPACE_BASE=/data/kira/users/usr_test_001/workspace
Environment=HERMES_WEB_UI_DISABLE_GATEWAY_AUTOSTART=1
Environment=HERMES_WEB_UI_DISABLE_MCP_AUTOINJECT=1
Environment=HERMES_LAN_DISCOVERY_ENABLED=false
ExecStart=/usr/local/bin/node /opt/kira/repos/hermes-web-ui-beta/dist/server/index.js
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/data/kira/users/usr_test_001
ReadOnlyPaths=/opt/kira/repos/hermes-web-ui-beta
```

Use a port that is not already occupied. In the 2026-06-28 run, `18648` was misleading because another listener already owned it; switching to `127.0.0.1:28648` isolated the beta runtime. Always verify with `ss -ltnp` and `systemctl status`, not just a successful curl.

Auth bootstrap pitfall: when `/api/auth/status` says `hasUsers:false`, the first login must use the built-in bootstrap credentials `admin` / `123456`; logging in with an arbitrary desired admin name returns `401`. Immediately change the admin password to a generated value, then create the dummy tenant Web UI account mapped only to `default`. Store generated dummy credentials only on the VM under the tenant root, e.g. `/data/kira/users/<uid>/acceptance-secrets/webui-auth.env` with `0700` directory and `0600` file, never in chat/evidence.

Minimum A7/A8 loopback checks:

```text
GET  /api/auth/status                  -> 200
POST /api/auth/login admin bootstrap   -> 200
POST /api/auth/change-password admin   -> 200
POST /api/auth/users usr_test_001      -> 201
POST /api/auth/login usr_test_001      -> 200
GET  /api/auth/me as usr_test_001      -> 200, username=usr_test_001
GET  /api/hermes/profiles              -> 200, profiles=[default]
POST /api/hermes/profiles              -> 403 for tenant user
GET  /api/auth/users                   -> 403 for tenant user
```

Report this as **PARTIAL PASS** for A7/A8 until public Authentik/Caddy routing and browser-visible login are proven. A loopback runtime proves tenant-local Web UI/auth/API denial; it does not prove public beta routing, Authentik mapping, cross-tenant routed API denial, chat/memory separation, or runtime tool-policy enforcement.

## After G11 passes: acceptance-document sync and G12 boundary

When the first real trusted beta user passes G11, the next safe step is not automatic cohort rollout. First reconcile the governing docs and ops evidence:

1. Update `kira-assembly/docs/implementation/beta-10-vm-build-and-acceptance-plan.md` so A7-A13 reflect the real G11 evidence and G12 remains explicitly not started.
2. Update `kira-ops/docs/evidence/beta-users/beta-10-vm-acceptance-status-YYYY-MM-DD.md` so it does not still describe G11 as pending or dummy-only.
3. Commit and push both repos on their active acceptance branches.
4. Keep `app.kiraproject.ru` guarded with `./bin/kira check prod-surface` before and after any VM-facing change.
5. Sync the VM acceptance checkout only from a pushed Git ref or bundle. If the sync requires `git reset --hard` or another consent-gated VM mutation and Hermes blocks it, stop and ask for explicit approval for that exact sync; do not work around the gate with manual file copying.

G12 stays blocked until Maxim provides or approves:

- ordered users 2-10 with stable UID, Authentik username, display name, and handoff/contact channel;
- per-user provider budget or approval to create the same capped tenant key shape used for `usr_polina`;
- routing model for `app.vm.kiraproject.ru`: one active routed tenant at a time, per-user host/path routing, or another multi-tenant route layer;
- confirmation that the VM beta route should expand while `app.kiraproject.ru` remains fallback.

Report this as `G11 PASS; G12 blocked on user list/routing`, not as full beta-10 completion.

## Production fallback guard

Before and after VM mutation:

```bash
cd /home/werserk/2-kira/kira-ops
./bin/kira check prod-surface
```

Do not cut over `app.kiraproject.ru`, enable duplicate Telegram gateway processing, or disable PC fallback unless Maxim explicitly approves.

## G11-to-G12 handoff pattern

After the first real trusted beta user reaches G11 `PASS`, do not stop at chat summary or leave stale acceptance docs saying G11 is pending. Do this handoff before attempting users 2–10:

1. Update the canonical acceptance contract in `kira-assembly` so the checklist reflects the real G11 evidence and names G12 as the remaining gate.
2. Update the `kira-ops` beta status snapshot so it says G11 passed for the real tenant and that G12 needs an approved ordered user list plus routing decision.
3. Commit/push both repos, then sync the VM acceptance checkout from the pushed `kira-ops` ref by Git bundle if the VM cannot fetch GitHub directly.
4. Add or refresh a G12 cohort runbook before live onboarding. It should require: ordered users 2–10, stable UIDs, Authentik usernames, handoff channels, per-user provider caps, and a routing choice.
5. Treat the routing choice as a blocking product/ops decision: single active routed tenant is acceptable only for sequential smoke; concurrent users need a multi-user routing layer and tests.
6. Re-run `./bin/kira validate all` locally and on the VM checkout, then `./bin/kira check prod-surface`. Report exact refs and `app.kiraproject.ru` `200 / 200 / 401` guard output.

Do not call beta-10 complete after G11. Say: `G11 PASS; G12 NOT STARTED/BLOCKED on approved users and routing decision` unless every approved cohort user has per-user evidence.

## Evidence discipline

Create evidence files under `kira-ops/docs/evidence/`, not only chat summaries. For beta-10 gates, prefer:

```text
docs/evidence/vm/<vm>-g0-g1-readiness-YYYY-MM-DD.md
docs/evidence/beta-users/<uid>-vm-contour-YYYY-MM-DD.md
docs/evidence/beta-users/<uid>-<otheruid>-cross-tenant-isolation-YYYY-MM-DD.md
docs/evidence/beta-users/<uid>-vm-backup-restore-YYYY-MM-DD.md
docs/evidence/beta-users/<uid>-disable-reenable-YYYY-MM-DD.md
```

Every evidence doc should state target host, command(s), Git ref, PASS/PARTIAL/BLOCKED, production impact, and remaining gates.
