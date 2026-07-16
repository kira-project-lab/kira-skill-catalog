# Kira beta user contour smoke checks

Use this when moving from product docs toward a working beta/user-contour implementation while protecting `app.kiraproject.ru`.

## Pattern

When the target product requires isolated users but production must not be touched, make the next step executable in `kira-ops` first:

1. Keep `app.kiraproject.ru` read-only for the task; verify `/health` before/after if relevant.
2. Put tenant registry and provisioning logic in `kira-ops`, not in the production Web UI checkout.
3. Prefer temp-root smoke checks before touching `/data/kira/users`:
   - provision a dummy tenant under `mktemp` via a `--base-dir` override;
   - check required assistant/profile/web-ui-state/agentmemory/workspace/uploads/exports/backups directories;
   - assert private paths are mode `0700`;
   - assert the command did not plan `/data/kira/users`, `/home/werserk`, or `/opt/kira` during smoke tests.
4. Add a single operator entrypoint for repeatability, for example:
   - `./bin/kira smoke beta-tenant <uid>`
   - `./bin/kira smoke beta-restore <uid>`
   - `./bin/kira smoke beta-all <uid>`
5. Run syntax/validation gates after wiring the entrypoint:
   - `bash -n bin/kira scripts/*.sh` for changed shell scripts;
   - `python -m py_compile scripts/platform.py` for Python ops logic;
   - `./bin/kira validate all`;
   - the new smoke command itself.
6. Report the actual status precisely: this proves a temp-contour smoke path, not live beta readiness.

## Completion language

Do not say the final product goal is complete after docs, registry scaffolding, or temp smoke checks. Say: `сделан следующий проверяемый шаг`; list what remains, usually real dummy tenant provisioning, Linux user ownership, negative-read checks, service wiring, backup/restore drill, and browser/Web UI tenant routing.

## Promotion gate

Only move from temp smoke to real dummy tenant after explicit scope is clear. Real `/data/kira/users/<uid>` provisioning, Linux user creation, systemd/service changes, Authentik bindings, or public routing are live operational changes and need the appropriate approval/safety gate.

## Live dummy tenant bootstrap pattern

When approval is given to create a real disabled dummy tenant, first run a privilege preflight instead of assuming the agent shell can do it:

```bash
sudo -n true && echo sudo_nopasswd=YES || echo sudo_nopasswd=NO
for p in /data /data/kira /data/kira/users /data/kira/users/<uid>; do
  if [ -e "$p" ]; then stat -c '%A %a %U:%G %n' "$p"; else echo "MISSING $p"; fi
done
```

If `sudo -n true` requires a password and `/data` is not writable, do not fake progress. Implement or verify a root-required command path, record the blocked attempt, and report that the live contour is not created. A good live bootstrap command should:

1. validate the tenant registry and resolve `runtime.linux_user` from `inventory/tenants.yaml`;
2. require root and exit with a clear non-zero code when not root;
3. create `/data`, `/data/kira`, `/data/kira/users` with traversable parent permissions;
4. create or reuse the tenant Linux user;
5. provision `/data/kira/users/<uid>` from the same registry-backed path as the temp smoke;
6. set tenant directories to `0700`, files to `0600`, and chown the contour to the tenant user;
7. seed a minimal profile config only if needed for negative-read targets;
8. run `scripts/check-beta-tenant-isolation.sh <uid> <linux_user>`.

Record evidence separately for live attempts, including whether `/data/kira/users/<uid>` actually exists afterward. Do not claim live negative-read checks passed unless the root-required command really ran and the check script passed.
