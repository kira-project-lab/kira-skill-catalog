# Kira beta-10 VM acceptance

Use when Maxim asks to build, assess, continue, or document beta-10 Kira on VM.

## Core lesson

Do not treat Maxim's home PC / `werserk-tachka` as the live multi-user beta target. It is dev/operator/fallback only. Real beta-10 tenant contours belong on Yandex Cloud VM `kira-main-ops-01` unless Maxim explicitly changes the target.

## Completion reporting

For beta/product goals, never report the goal complete after producing only docs, roadmaps, smoke tests, or one hardening patch. Say exactly which slice passed and list the remaining acceptance gates.

## Acceptance-first workflow

1. Record or check the acceptance contract in `kira-assembly`, normally:
   - `docs/implementation/beta-10-vm-build-and-acceptance-plan.md`
   - `docs/architecture/beta-10-product-boundary.md`
   - `docs/adr/2026-06-27-beta-10-runtime-target-yandex-vm.md`
2. Keep `app.kiraproject.ru` protected as PC fallback; verify with `kira-ops` prod-surface checks before/after risky work.
3. Treat VM host identity as gate G0. If SSH reports `REMOTE HOST IDENTIFICATION HAS CHANGED`, stop and require trusted verification; do not bypass with `StrictHostKeyChecking=no`.
4. Use local `/tmp` tenant smoke tests only as tooling checks, not beta acceptance.
5. Run live tenant provisioning only on `kira-main-ops-01` after VM readiness passes.
6. Store evidence in `kira-ops/docs/evidence/`, not only in chat.

## Minimum beta-10 acceptance gates

- VM identity/access PASS.
- VM baseline inventory PASS.
- Deploy/source model from known Git refs PASS.
- Tenant registry and tool policy validation PASS.
- Real dummy tenant under `kira-main-ops-01:/data/kira/users/usr_test_001` PASS.
- Linux ownership and `0700`/`0600` permissions PASS.
- Negative-read checks against operator profile/secrets/other tenant PASS.
- Authentik/Web UI tenant routing PASS.
- Runtime profile/state/memory separation PASS.
- Runtime dangerous-tool denial PASS.
- Backup/restore drill on VM PASS.
- Disable/re-enable path PASS.
- First real trusted user E2E browser-visible smoke PASS.
- `app.kiraproject.ru` fallback remains healthy.
- Maxim approves cohort expansion.

## G0 target-identity pitfall

Before updating `known_hosts` or provisioning anything, confirm that the intended VM in the acceptance plan, generated inventory, and currently accessible YC project are the same host.

Known failure shape from beta-10 work:

- `ansible/inventory.generated.ini` pointed to `kira-app-01 ansible_host=51.250.77.163` in an old folder.
- Current YC credentials saw cloud `kira` / folder `main` with VM `kira-main-ops-01 public_ip=81.26.176.187`.
- `./bin/kira check vm-beta-readiness` failed with `REMOTE HOST IDENTIFICATION HAS CHANGED` for `51.250.77.163`.

Correct response:

1. Stop before mutation; do not use `StrictHostKeyChecking=no` and do not remove `known_hosts` entries blindly.
2. Capture evidence in `kira-ops/docs/evidence/vm/...`.
3. Ask/decide whether beta-10 target remains the old `kira-app-01` or moves to the accessible `kira-main-ops-01`.
4. Only after the target decision, update docs/inventory and verify the host key through YC console/CLI or another trusted channel.

Resolved beta-10 target from this session:

- Maxim approved retargeting beta-10 to `kira-main-ops-01` / `81.26.176.187`.
- Use Ansible inventory target `kira-main-ops-01 ansible_host=kira-main-ops ansible_user=kira` so the trusted SSH alias and configured identity are used instead of raw IP auth.
- `./bin/kira check vm-beta-readiness` should PASS before mutation. It proved `hostname=kira-main-ops-01`, `whoami=kira`, Docker/systemd surfaces, and `/data/kira/users` on the VM.
- VM evidence paths from the successful pass: `kira-ops/docs/evidence/vm/kira-main-ops-01-g0-g1-readiness-2026-06-28.md`, `kira-ops/docs/evidence/beta-users/usr_test_001-vm-contour-2026-06-28.md`, and `kira-ops/docs/evidence/beta-users/usr_test_001-usr_test_002-cross-tenant-isolation-2026-06-28.md`.

## VM dummy-tenant provisioning pattern

After G0/G1 pass, put the accepted `kira-ops` ref onto the VM in a separate checkout such as `/opt/kira/repos/kira-ops-beta-acceptance`. If GitHub deploy keys are unavailable on the VM, a local `git bundle` transferred via `scp` is acceptable for a controlled acceptance checkout; record the commit hash in evidence.

Then run from the VM checkout:

```bash
./bin/kira validate all
sudo ./bin/kira tenant provision-live usr_test_001
scripts/check-beta-tenant-isolation.sh usr_test_001 kira-u-test001
```

Important implementation pitfall: Ubuntu on `kira-main-ops-01` has `/usr/sbin/nologin`, not `/usr/bin/nologin`; live tenant provisioning should create system users with `/usr/sbin/nologin`. Verify with `getent passwd <linux_user>`.

For full A6, create a second dummy tenant such as `usr_test_002` and run negative-read checks both ways:

```bash
scripts/check-beta-tenant-isolation.sh usr_test_001 kira-u-test001 usr_test_002
scripts/check-beta-tenant-isolation.sh usr_test_002 kira-u-test002 usr_test_001
```

A6 is only PASS when both tenants can read their own root and cannot read operator profile/secrets or the other tenant's profile.

## Useful commands

```bash
cd /home/werserk/2-kira/kira-ops
./bin/kira check prod-surface
./bin/kira check vm-beta-readiness
./bin/kira validate all
./bin/kira smoke beta-all usr_test_001

yc config list
yc resource-manager cloud list --format json
yc resource-manager folder list --cloud-id <cloud-id> --format json
yc compute instance list --folder-id <folder-id> --format json
```

Live VM tenant provisioning, only after VM identity/access is trusted:

```bash
cd /opt/kira/repos/kira-ops-beta-acceptance
sudo ./bin/kira tenant provision-live usr_test_001
scripts/check-beta-tenant-isolation.sh usr_test_001 kira-u-test001
scripts/check-beta-tenant-isolation.sh usr_test_001 kira-u-test001 usr_test_002
```

## A7/A8 Web UI/Auth gate pattern

After tenant filesystem/isolation gates pass, do **not** assume Web UI/Auth is ready. Run/read the VM Web UI/Auth readiness probe from the operator machine, not from the VM, because the acceptance script uses local Ansible:

```bash
cd /home/werserk/2-kira/kira-ops
./bin/kira check vm-webui-auth-readiness
```

When public routing starts working, keep the proof split into layers:

1. Authentik application access — user belongs to the group bound to the application, e.g. `kira-users` for `kira-vm-web-ui`; `Permission denied` after Authentik login is usually an app-policy/group issue, not a Caddy route issue.
2. Web UI tenant API mapping — `/api/auth/login` and `/api/auth/me` prove the Web UI JWT maps to the tenant username and only allowed profile(s), typically `default` for dummy tenants.
3. Representative admin/danger route denial — e.g. `/api/auth/users`, `POST /api/hermes/profiles`, and `/api/hermes/config` should return `403` for the tenant token.
4. Chat/runtime smoke — a user prompt reaches Hermes Agent bridge and receives a model response.
5. Tool-loop denial — forbidden terminal/filesystem/deploy/arbitrary MCP attempts are denied by the running assistant.

Do not collapse these into one `browser works` claim. Authentik can pass while Web UI JWT is absent; bridge can pass while provider/model configuration is absent.

Known A7/A8 blocker shape from beta-10 work:

```text
authentik_status=present
caddy_status=present
docker_webui=missing
caddy_webui_routes=missing
BLOCKED: no Hermes Web UI beta runtime or route is visible on the VM
```

Interpretation:

- Authentik and Caddy existing on `kira-main-ops-01` are necessary but not sufficient.
- A7 cannot pass until a VM Hermes Web UI beta runtime and Caddy/Auth route exist.
- A8 cannot pass until there is a VM Web UI API surface for direct cross-tenant/profile denial tests.
- Record the blocker in `kira-ops/docs/evidence/vm/...` and update the acceptance plan; do not keep provisioning lower layers and call beta readiness complete.

Implementation pitfall: `./bin/kira check vm-webui-auth-readiness` is an **operator-side read-only probe**. If you sync `kira-ops` to the VM, do not run this Ansible-based check inside the VM unless Ansible is installed/configured there; use direct SSH/manual checks or run the probe from the home/operator checkout.

## VM Web UI preview checkout prerequisite for A7/A8

When A0-A6 pass but A7/A8 are pending, first inspect whether a VM Web UI runtime/checkout exists. On `kira-main-ops-01`, the useful existing checkout was `/opt/kira/services/hermes-web-ui-preview`.

If the checkout's `.git` metadata is root-owned, fix the metadata ownership only, not the whole runtime blindly:

```bash
sudo chown -R kira:kira /opt/kira/services/hermes-web-ui-preview/.git
```

If the VM cannot fetch the private GitHub repo because deploy keys are unavailable, transfer the accepted Web UI dev ref as a local bundle from the operator machine:

```bash
git -C /home/werserk/2-kira/hermes-web-ui-dev bundle create /tmp/hermes-web-ui-dev-<sha>.bundle dev
scp /tmp/hermes-web-ui-dev-<sha>.bundle kira-main-ops:/tmp/
ssh kira-main-ops
cd /opt/kira/services/hermes-web-ui-preview
git fetch /tmp/hermes-web-ui-dev-<sha>.bundle dev
git checkout -B beta-10-webui-preview FETCH_HEAD
```

Then verify the hardening contract on the VM before starting or routing anything publicly:

```bash
npm run test -- tests/server/profile-routes-auth.test.ts
```

This is only an A7/A8 prerequisite. It proves the VM checkout has profile lifecycle route hardening; it does **not** prove Authentik/Web UI tenant mapping, direct API cross-tenant denial, runtime memory separation, or tool-policy enforcement. Record it as prerequisite evidence (example: `kira-ops/docs/evidence/vm/kira-main-ops-01-webui-preview-checkout-2026-06-28.md`) and keep `app.kiraproject.ru` protected with `./bin/kira check prod-surface`.

## Backup/restore and disable gates

A11 and A12 are separate from Web UI/Auth:

- A11 can PASS for live dummy tenant state when a VM backup creates `manifest.json`, component archives, `checksums.sha256`, restores into a clean drill path such as `/data/kira/restore-drills/<uid>-<timestamp>`, and verifies private permissions.
- A12 can only be PARTIAL PASS if it writes/clears a tenant `.disabled` marker but Authentik/Web UI session revocation is not yet implemented. Do not call disable complete until browser/API access is actually denied for the disabled user.

Evidence examples from this workflow:

- `kira-ops/docs/evidence/beta-users/usr_test_001-vm-backup-restore-2026-06-28.md`
- `kira-ops/docs/evidence/beta-users/usr_test_001-disable-reenable-2026-06-28.md`

## Two-tenant loopback Web UI state separation pattern

When A7/A8 need progress but public Authentik routing is not ready, a useful intermediate gate is two **loopback-only** Web UI runtimes on the VM, one per dummy tenant. This is not final beta readiness, but it gives concrete proof that Web UI auth/state roots are separated.

Pattern from beta-10 work:

```text
usr_test_001 -> kira-beta-webui-usr-test-001.service -> 127.0.0.1:28648
usr_test_002 -> kira-beta-webui-usr-test-002.service -> 127.0.0.1:28649
```

Each service should run as its tenant Linux user with tenant-scoped roots:

```text
User=kira-u-test00N
BIND_HOST=127.0.0.1
HERMES_HOME=/data/kira/users/<uid>/assistants/kira/hermes-root
HERMES_WEB_UI_HOME=/data/kira/users/<uid>/assistants/kira/web-ui-state
HERMES_WEBUI_STATE_DIR=/data/kira/users/<uid>/assistants/kira/web-ui-state
UPLOAD_DIR=/data/kira/users/<uid>/uploads
WORKSPACE_BASE=/data/kira/users/<uid>/workspace
HERMES_WEB_UI_DISABLE_GATEWAY_AUTOSTART=1
HERMES_WEB_UI_DISABLE_MCP_AUTOINJECT=1
HERMES_LAN_DISCOVERY_ENABLED=false
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/data/kira/users/<uid>
ReadOnlyPaths=/opt/kira/repos/hermes-web-ui-beta
```

Use helper scripts in `kira-ops` if present:

```bash
sudo ./scripts/install-beta-webui-runtime.sh usr_test_002 28649
sudo ./scripts/smoke-beta-webui-auth.sh usr_test_002 28649
```

Then verify cross-runtime auth denial without printing secrets:

```text
usr_test_001 own runtime port 28648 status 200
usr_test_002 own runtime port 28649 status 200
usr_test_001 into tenant2 runtime port 28649 status 401
usr_test_002 into tenant1 runtime port 28648 status 401
```

Acceptance interpretation:

- A7: PARTIAL PASS only. Loopback user-to-runtime mapping works; Authentik/public route remains pending.
- A8: PARTIAL PASS only. Admin/profile lifecycle denial and cross-runtime credential denial work; public routed API matrix remains pending.
- A9: PARTIAL PASS only for Web UI auth/state roots. Actual chat/session/memory separation remains pending.

Evidence example: `kira-ops/docs/evidence/beta-users/usr_test_001-usr_test_002-vm-webui-state-separation-2026-06-28.md`.

## Web UI auth smoke pitfalls

- On a fresh isolated Web UI state DB, `/api/auth/status` reports `hasUsers=false`; the first login must use the built-in bootstrap password `123456`, then immediately change the admin password to a generated tenant-owned value. Do not assume a generated admin password will work before bootstrap.
- `/api/auth/me` may return the user object directly rather than under `{ user: ... }`; smoke probes should accept both shapes.
- User profile bindings may not appear in `/api/auth/me`; verify profile access with `/api/hermes/profiles` instead.
- Store generated smoke credentials only under tenant-owned `acceptance-secrets` with `0700` directory and `0600` file permissions. Never paste them into chat or docs.
- If older smoke evidence used different key names (`beta_username`/`beta_password` vs `TENANT_USER`/`TENANT_PASSWORD`), cross-runtime probes should normalize both formats rather than copying secrets around.

## A10 dangerous-route denial pattern

When proving beta dangerous-tool denial, separate two layers clearly:

1. **Web UI/API dangerous route denial** — routes that would install/launch coding agents, mutate config/credentials/models, manage MCP servers/tools, or refresh provider/model catalogs must require `requireSuperAdmin`. A beta tenant token should receive `403`.
2. **Hermes Agent tool-loop denial** — actual assistant tool execution denial for terminal/filesystem/arbitrary MCP/deploy attempts. Web UI route denial is only a PARTIAL PASS for A10 until this is also proven.

Useful hardening targets in Hermes Web UI:

```text
packages/server/src/routes/coding-agents.ts -> codingAgentRoutes.use(requireSuperAdmin)
packages/server/src/routes/hermes/config.ts -> config/credentials routes requireSuperAdmin
packages/server/src/routes/hermes/mcp.ts -> mcpRoutes.use(requireSuperAdmin)
packages/server/src/routes/hermes/models.ts -> provider/model mutation routes requireSuperAdmin; keep available-models readable if needed
```

Add/keep a source contract test such as `tests/server/dangerous-routes-auth.test.ts` that asserts the route files keep the super-admin guard. Run with the profile route contract test:

```bash
npm run test -- tests/server/dangerous-routes-auth.test.ts tests/server/profile-routes-auth.test.ts
npm run build
```

On the VM, after deploying the hardened Web UI ref to `/opt/kira/repos/hermes-web-ui-beta` and restarting the loopback tenant services, run a tenant-token denial smoke that attempts at least:

```text
GET /api/hermes/config
PUT /api/hermes/config
PUT /api/hermes/config/credentials
POST /api/coding-agents/claude-code/install
POST /api/coding-agents/claude-code/runs
GET /api/hermes/mcp/tools
POST /api/hermes/mcp/reload
POST /api/hermes/provider-models
PUT /api/hermes/config/model
PUT /api/hermes/model-alias
PUT /api/hermes/custom-model
```

Expected result: every dangerous route returns `403` for the beta tenant token. Record as A10 **PARTIAL PASS** evidence, not full A10, because Hermes Agent tool-loop denial remains pending. Example evidence path: `kira-ops/docs/evidence/beta-users/usr_test_002-vm-webui-dangerous-route-denial-2026-06-28.md`.

Pitfall: if a tenant's `acceptance-secrets/webui-auth.env` is incomplete or from an old format, do not overwrite it silently against an existing Web UI auth database. Fail closed with a clear message and reset the tenant runtime deliberately if credentials are lost. This avoids creating new secrets that no longer match the existing auth DB.
