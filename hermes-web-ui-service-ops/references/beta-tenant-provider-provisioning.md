# Beta tenant provider provisioning

Use this when a VM beta tenant Web UI reaches Authentik, Web UI JWT, and Agent Bridge, but chat/runtime fails with provider/model configuration errors.

## Gate separation

Report these as separate gates, not one generic “login/chat works” claim:

1. Public route and Authentik authorization.
2. Web UI tenant JWT/API mapping (`/api/auth/me`, visible profiles, admin route denial).
3. Agent Bridge reachability.
4. Provider/model readiness.
5. Tool-loop policy denial.

A browser can reach `#/hermes/chat` while `/api/auth/me` is still `401`. A message can reach the bridge while the tenant profile still fails with `No inference provider configured`.

## OpenRouter key pattern

If Maxim supplies an OpenRouter **management key**, use the OpenRouter API directly. Do not ask for browser login after the management key is available.

Create a limited tenant key:

```bash
POST https://openrouter.ai/api/v1/keys
Authorization: Bearer <management-key>
Content-Type: application/json

{
  "name": "kira-beta-<uid>-<date>",
  "limit": 2,
  "limit_reset": "monthly",
  "include_byok_in_limit": true
}
```

The response includes plaintext `key` only once. Store it immediately in a scoped secret, then remove any temp copy.

Durable secret shape:

```text
Lockbox secret: kira-beta-openrouter-<uid>
entries:
  OPENROUTER_API_KEY
  OPENROUTER_KEY_NAME
```

If a key is created but secret persistence fails, delete the orphaned key before creating the stored replacement.

## Tenant-scoped install pattern

Install the key only into the tenant Hermes root, not Maxim/operator profile roots:

```text
/data/kira/users/<uid>/assistants/kira/hermes-root/.env
/data/kira/users/<uid>/assistants/kira/hermes-root/config.yaml
```

If the management key is provided in chat, do **not** store it in memory, evidence, repo files, or Lockbox unless Maxim explicitly asks. Use it in an ephemeral prompt/input path to create the limited tenant key, then persist only the resulting tenant key in the tenant-scoped Lockbox secret. A safe pattern is a temporary script using `getpass.getpass()` or stdin in a PTY, with the management key omitted from stdout.

After creating the tenant key, immediately:

1. write a temporary `0600` Lockbox payload containing only `OPENROUTER_API_KEY` and `OPENROUTER_KEY_NAME`;
2. create or add a version to `kira-beta-openrouter-<uid>`;
3. verify `GET /api/v1/key` with the tenant key and save only non-secret metadata;
4. install `.env` and `config.yaml` into the tenant Hermes root as `0600 <tenant-linux-user>:<tenant-linux-user>`;
5. delete local and VM temp payload/config files;
6. restart only `kira-beta-webui-<uid-with-dashes>.service` and wait for the route-local `/health` to return `200` before browser smokes.

Minimal config used for dummy beta tenant smoke:

```yaml
profile: default
model:
  default: google/gemini-3-flash-preview
  provider: openrouter
providers: {}
fallback_providers: []
platform_toolsets:
  cli:
    - no_mcp
```

Required permissions:

```text
600 <tenant-linux-user>:<tenant-linux-user> .env
600 <tenant-linux-user>:<tenant-linux-user> config.yaml
```

Restart only the tenant Web UI service, then run routed chat smoke and session-message inspection.

## Secret hygiene checks

Before reporting success:

- Do not print the OpenRouter key value in stdout/evidence.
- Save only key name/hash/limit/remaining budget.
- Scan touched repo paths for actual key patterns, not for harmless literal examples:

```bash
grep -R -E "sk-or-v1-[A-Za-z0-9]{20,}" docs/evidence/beta-users scripts
```

## Reporting wording

If provider provisioning passes for a dummy tenant, say `G7 partial pass for <uid>` unless every later beta gate is also done. Name remaining gates explicitly: tool-loop negative matrix, active-session revocation, real beta user end-to-end smoke, and cohort expansion.
