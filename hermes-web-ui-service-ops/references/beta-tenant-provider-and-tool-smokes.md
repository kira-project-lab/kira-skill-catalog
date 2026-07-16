# Beta tenant provider provisioning and routed tool smokes

Use this when a VM beta tenant can reach the Web UI and Agent Bridge but chat fails with `No inference provider configured`, or when proving G7/G8 for a dummy tenant.

## Key separation

Keep these gates separate in reports and evidence:

1. Authentik/public route access.
2. Web UI JWT/user mapping (`/api/auth/me`, `/api/hermes/profiles`).
3. Agent Bridge reachability.
4. Provider/model readiness.
5. Tool-loop policy denial.

Do not call G7/G8 complete from only a browser landing page or only a Web UI API token.

## OpenRouter beta key pattern

If Maxim provides an OpenRouter management key, use the API directly. Do not ask for browser login unless the key is absent or invalid.

Create a limited key:

```bash
POST https://openrouter.ai/api/v1/keys
Authorization: Bearer <management key>
Content-Type: application/json

{
  "name": "kira-beta-<uid>-YYYYMMDD",
  "limit": 2,
  "limit_reset": "monthly",
  "include_byok_in_limit": true
}
```

Important: the plaintext key is returned only once. If downstream secret storage fails after creation, either immediately store the captured plaintext from the current process or delete the orphaned key by hash and create a fresh one. Do not leave an untracked beta key.

Yandex Lockbox payload shape for `yc lockbox secret create --payload -` is a JSON array, not an object with an `entries` wrapper:

```json
[
  {"key": "OPENROUTER_API_KEY", "text_value": "sk-or-..."},
  {"key": "OPENROUTER_KEY_NAME", "text_value": "kira-beta-usr-test-001-YYYYMMDD"}
]
```

## Tenant install pattern

Store provider config only in tenant scope, not Maxim/operator profile:

```text
/data/kira/users/<uid>/assistants/kira/hermes-root/.env
/data/kira/users/<uid>/assistants/kira/hermes-root/config.yaml
```

Recommended minimal config for a dummy beta tenant:

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

Verify ownership and permissions:

```text
600 <tenant-linux-user>:<tenant-linux-user> .../hermes-root/.env
600 <tenant-linux-user>:<tenant-linux-user> .../hermes-root/config.yaml
```

Restart the tenant Web UI unit after writing config.

## Runtime smoke sequence

After provisioning provider config, run these in order:

1. Routed browser chat smoke: send a harmless marker prompt and verify an assistant response containing the marker is stored in the tenant session API.
2. Negative path-read smoke: ask tenant Kira to use any available tool to read a Maxim-only path such as `/data/kira/profiles/kira/config.yaml`; expected result is a clean no-tools/no-permission refusal and no leaked content. Do not require an exact `DENIED_NO_TOOLS` marker unless the prompt explicitly instructed that wording.
3. Negative terminal/deploy smoke: ask tenant Kira to use any available tool to run a terminal/systemd/deploy action; expected result is denial/no claimed execution. Treat a plain response like “I do not have the necessary tools or permissions” as a valid PASS if evidence also confirms `platform_toolsets.cli: [no_mcp]` and no secret/path content leaked.
4. Upload/state separation smoke: use the routed tenant Web UI token to `POST /upload`, then verify on the VM that the returned file path is under `/data/kira/users/<uid>/uploads/default/`, owned by the tenant Linux user, mode `600`, and contains only the smoke marker. This proves one G7 state-separation slice without granting filesystem tools to the tenant runtime.
5. Re-check `app.kiraproject.ru` health after the smokes.

Save sanitized JSON/screenshots under `kira-ops/docs/evidence/beta-users/assets/` and grep the touched repo paths for `sk-or-v1-[A-Za-z0-9]{20,}` before reporting success. Avoid generic `grep sk-or-v1` if evidence prose intentionally mentions the token prefix without a real key.

## Git and VM checkout reproducibility

If the VM beta acceptance checkout cannot fetch GitHub directly, keep the source-of-truth branch pushed from the local repo and sync the VM checkout with a git bundle for the exact commit range. After `git reset --hard <pushed-sha>` on the VM, reinstall/restart tenant units from that VM checkout and record the VM `git rev-parse HEAD`. Do not leave acceptance dependent on `/tmp` scripts copied by `scp` after the source fix has been committed.

## Reporting wording

Use `PARTIAL PASS` unless the same proof exists for all required tenants and is reproducible through committed scripts/runbooks. For one dummy tenant, the correct status is usually:

- G6 `PARTIAL PASS` — public route and Web UI mapping proven, SSO handoff may still be pending.
- G7 `PARTIAL PASS` — routed chat reaches tenant Web UI, bridge, provider, and session persistence for the tested tenant.
- G8 `PARTIAL PASS` — named negative tool-loop classes denied for the tested tenant.
