# VM beta tenant note/file access

Use this when a beta tenant passes Authentik/Web UI/runtime/provider checks but G11 note/vault write fails through the Web UI file API.

## Symptom

A tenant user can log in, chat, upload files, and pass negative route checks, but a note/vault smoke such as:

```text
PUT /api/hermes/files/write { path: "obsidian-vault/<marker>.md" }
GET /api/hermes/files/read?path=obsidian-vault/<marker>.md
```

returns `403` for the tenant token.

Known failure shape from the first real-user G11 pass:

```text
path: obsidian-vault/g11-note-<timestamp>.md
PUT /api/hermes/files/write -> 403
GET /api/hermes/files/read -> 403
```

Root cause: the beta Web UI branch had hardened file editor routes behind `requireSuperAdmin`, which was correct for broad file/config access but too broad for tenant-owned note/vault paths.

## Safe fix pattern

Keep dangerous file operations denied by default. Allow non-superadmin tenant users only for explicitly tenant-safe relative prefixes that resolve under their selected profile root:

```text
obsidian-vault/
workspace/
notes/
```

Do not allow arbitrary absolute paths, `..` traversal, `.env`, `auth.json`, `config.yaml`, or operator/profile roots.

Implementation shape in `packages/server/src/routes/hermes/files.ts`:

- add a small `isTenantSafeFilePath(relativePath)` helper;
- keep `requireSuperAdmin` on destructive/broad operations such as delete, rename, copy, and upload unless the product explicitly approves tenant access there;
- remove `requireSuperAdmin` from `read`, `write`, and `mkdir` only after checking `requireTenantFileAccess(ctx, relativePath)`;
- rely on `resolveHermesPath(relativePath, requestedProfile(ctx))` to keep the resolved path under the tenant profile root;
- keep tests proving both sides:
  - tenant admin can `mkdir/read/write` `obsidian-vault/...`;
  - tenant admin still gets `403` for non-whitelisted paths such as `config.yaml`.

## Verification

Focused Web UI checks:

```bash
npm run test -- tests/server/files-routes.test.ts tests/server/dangerous-routes-auth.test.ts
npm run build
```

Deploy only to the beta Web UI checkout unless the task explicitly targets prod.

VM runtime checks after deploy/restart:

```bash
systemctl is-active kira-beta-webui-<uid-with-dashes>.service
curl -sS -o /dev/null -w 'health=%{http_code}\n' http://172.17.0.1:<port>/health
```

Then rerun the browser/API note smoke and record:

```text
mkdirStatus: 200
writeStatus: 200
readStatus: 200
statStatus: 200
absolutePath: /data/kira/users/<uid>/assistants/kira/hermes-root/obsidian-vault/<file>.md
inTenantHermesRoot: true
```

## Pitfalls

- `obsidian-vault/` under the Web UI file API resolves under the tenant Hermes profile root, not `/data/kira/users/<uid>/workspace/obsidian-vault`, unless the profile config maps it differently. Evidence should state the actual `absolutePath` rather than assuming the workspace path.
- A note-fix deploy may leave tenant Web UI state directories owned by a service/runtime group after previous smoke scripts. If the service loops on `EACCES: permission denied, mkdir .../web-ui-state/logs`, reset ownership of tenant runtime roots to the tenant Linux user and recreate `logs` as `0700`.
- Systemd can report `active` before the tenant HTTP listener is ready. Wait for the listener/health response before declaring the route healthy.
- If route-local negative-matrix or auth checks hang, restart only the tenant Web UI service and recheck `/health`; do not touch `app.kiraproject.ru`.

## Reporting

G11 is not full PASS until note/vault behavior either passes or Maxim explicitly removes it from the acceptance contract. If all other G11 checks pass but note write fails, report `PARTIAL PASS` and name this exact blocker.
