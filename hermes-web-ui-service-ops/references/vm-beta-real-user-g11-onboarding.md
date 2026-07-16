# VM beta real-user G11 onboarding pattern

Use this when moving from dummy tenant beta-10 evidence to the first real trusted beta user on `kira-main-ops-01`.

## Key distinction

A real beta user can have a public/Auth identity that differs from the tenant UID.

Example shape from the first G11 attempt:

```text
Authentik username: polina
Tenant UID: usr_polina
Linux user: kira-u-polina
Web UI tenant user: usr_polina
```

Do not assume `uid == Authentik username`. Tenant helpers should resolve the auth username from `inventory/tenants.yaml`:

```yaml
auth:
  web_account: polina
  authentik_user_ref: polina
runtime:
  linux_user: kira-u-polina
```

Public-access helpers must toggle Authentik group membership for `authentik_user_ref`, but mirror Web UI status and VM `.disabled` markers for the tenant UID.

## G11 sequence

1. Verify prod fallback first:

   ```bash
   ./bin/kira check prod-surface
   ```

2. Add a tenant registry entry for the real user with non-secret metadata only.
3. Commit/push and sync the VM acceptance checkout from a Git ref or bundle. Do not leave VM-only edits.
4. Provision the live contour:

   ```bash
   sudo ./bin/kira tenant provision-live <uid>
   ```

5. Install a tenant Web UI runtime on a dedicated port:

   ```bash
   sudo ./scripts/install-beta-webui-runtime.sh <uid> <port>
   sudo ./scripts/smoke-beta-webui-auth.sh <uid> <port> 172.17.0.1
   sudo KIRA_SMOKE_OUTPUT_JSON=/tmp/<uid>-negative-matrix.json \
     ./bin/kira smoke beta-negative-matrix <uid> <port> 172.17.0.1
   ```

6. For a real public-route G11 attempt, switch `app.vm.kiraproject.ru` to the real tenant upstream, validate Caddy, reload, and verify prod fallback again. Record the route switch in evidence.
7. Enable public access through the helper:

   ```bash
   ./scripts/beta-user-public-access.py enable <uid> --reason g11-real-beta-user-smoke
   ```

8. Run browser/API smoke and the full browser-visible E2E scenario.

## Provider-key gate

G11 is not PASS until the real tenant has its own capped inference provider key/config.

- Do not copy a dummy tenant key into a real user tenant.
- Do not copy Maxim/operator keys.
- If an OpenRouter management key is available, use it only to create a new limited user/model key; do not install or persist the management key in tenant roots, repo evidence, memory, or docs.
- Store the generated tenant key immediately in a scoped Lockbox secret such as `kira-beta-openrouter-<uid>` with entries `OPENROUTER_API_KEY` and `OPENROUTER_KEY_NAME`.
- Install only that tenant-scoped key into `/data/kira/users/<uid>/assistants/kira/hermes-root/.env` and config into `config.yaml`, both `0600 <tenant-user>:<tenant-user>`.
- If no OpenRouter management key or approved tenant-scoped provider secret is available, stop at `PARTIAL / BLOCKED` and record exactly which lower layers passed.

Evidence should say the blocker is `missing separate capped provider key/config`, not a generic chat failure.

Evidence should say the blocker is `missing separate capped provider key/config`, not a generic chat failure.

After provider provisioning, rerun the lower G11 smokes instead of assuming the prior route/auth pass still proves runtime:

```bash
# route-local health after restart
curl -sS -o /dev/null -w '%{http_code}\n' http://172.17.0.1:<port>/health

# browser/API mapping through public route
NODE_PATH=<webui-node-modules> node /tmp/beta_app_vm_browser_api_smoke_generic.js <uid>

# provider-backed chat and policy checks
NODE_PATH=<webui-node-modules> node /tmp/beta_app_vm_chat_smoke_generic.js <uid>
NODE_PATH=<webui-node-modules> node /tmp/beta_app_vm_negative_smoke.js <uid>
NODE_PATH=<webui-node-modules> node /tmp/beta_app_vm_memory_smoke.js <uid>
NODE_PATH=<webui-node-modules> node /tmp/beta_app_vm_upload_smoke.js <uid>

# backup/restore and active session revocation
sudo ./bin/kira smoke beta-live-restore <uid>
./scripts/beta-user-public-access.py disable <uid> --reason g11-active-session-revocation
./scripts/beta-user-public-access.py enable <uid> --reason g11-active-session-reenable
```

## Evidence status wording

For a partial G11 attempt, split the layers:

- PASS: tenant registry entry;
- PASS: live VM root and Linux user;
- PASS: Web UI runtime health;
- PASS: Authentik account maps to public beta route;
- PASS: Web UI JWT maps to tenant UID and allowed profile(s);
- PASS: negative matrix denies restricted API/tooling routes;
- BLOCKED: chat/memory/upload/note E2E until provider key/config exists;
- PARTIAL PASS: chat/provider/upload/negative/restore/revocation pass but note/vault write fails;
- PASS: first real user completes chat/provider, in-chat recall, upload, tenant-safe note/vault write, negative matrix, live restore, and disable/re-enable with old-token denial.

Do not call beta-10 complete while G11 chat/memory/upload/note and disable/re-enable are blocked. After G11 passes, G12 cohort expansion still needs an approved user list and routing model.
- PASS: live backup/restore drill completes;
- PASS: disable/re-enable rejects an already-issued token;
- BLOCKED: any remaining user-facing feature that is still part of the G11 contract, such as note/vault write returning `403`.

Do not call beta-10 complete while a required G11 feature remains blocked. If note/vault write is blocked through `/api/hermes/files/write`, report it as a specific product/API blocker, not as provider failure.

## Temp credentials hygiene

If a temporary Authentik password is needed for automated browser smoke, keep it outside the repo, e.g. `/tmp/authentik-<uid>.env` with `0600`, and report only that it was set. Never commit or paste it into evidence.

After smoke, rotate the temporary password again and store handoff credentials in a scoped Lockbox secret instead of leaving the operator `/tmp` file as the only copy. Use a tenant-specific secret name such as `kira-beta-authentik-<uid>-temp` with non-code evidence that the rotation happened; do not record the plaintext value in docs.
