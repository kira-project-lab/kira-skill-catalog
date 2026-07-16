# VM beta tenant provider + bridge smoke notes

Use this reference when a beta tenant reaches the VM Web UI but chat/runtime does not complete.

## Gate separation

Do not collapse these into one “login works” claim:

1. Public route/Auth: `app.vm.kiraproject.ru` reaches Authentik and returns to the Web UI route.
2. Web UI tenant session: `/api/auth/me` with the Web UI JWT maps to the tenant username.
3. Profile visibility: `/api/hermes/profiles` shows only the tenant-scoped profile, usually `default`.
4. Bridge readiness: tenant Web UI can reach its own Hermes Agent bridge socket.
5. Provider/model readiness: tenant Hermes profile has a scoped inference provider key and model.
6. Tool-loop policy denial: tenant runtime refuses/denies forbidden terminal/filesystem/deploy/operator-profile access.

A browser may show the chat page while `/api/auth/me` is still `401`; Authentik forward-auth is not the same as Web UI JWT login.

## Tenant bridge hardening

For per-tenant VM Web UI services, avoid the global default bridge endpoint:

```ini
Environment=HERMES_AGENT_ROOT=/opt/kira/services/hermes-agent
Environment=HERMES_AGENT_BRIDGE_BASE_HOME=/data/kira/users/<uid>/assistants/kira/hermes-root
Environment=HERMES_AGENT_BRIDGE_ENDPOINT=ipc:///data/kira/users/<uid>/assistants/kira/web-ui-state/agent-bridge.sock
ReadOnlyPaths=/opt/kira/repos/hermes-web-ui-beta /opt/kira/services/hermes-agent
```

Why:

- without `HERMES_AGENT_ROOT`, the bridge can discover an unreadable/default root such as `/home/kira/run_agent.py` and exit with `PermissionError`;
- without a tenant-scoped `HERMES_AGENT_BRIDGE_ENDPOINT`, multiple tenant services can collide on `/tmp/hermes-agent-bridge.sock`.

Manual bridge probe pattern on the VM:

```bash
sudo -u <linux_user> env \
  HERMES_HOME=/data/kira/users/<uid>/assistants/kira/hermes-root \
  HERMES_AGENT_ROOT=/opt/kira/services/hermes-agent \
  HERMES_AGENT_BRIDGE_BASE_HOME=/data/kira/users/<uid>/assistants/kira/hermes-root \
  timeout 3 /usr/bin/python3 \
  /opt/kira/repos/hermes-web-ui-beta/dist/server/agent-bridge/python/hermes_bridge.py \
  --endpoint ipc:///tmp/hermes-agent-bridge-manual-smoke.sock \
  --hermes-home /data/kira/users/<uid>/assistants/kira/hermes-root \
  --agent-root /opt/kira/services/hermes-agent
```

Expected ready line:

```json
{"event":"ready","mode":"broker"}
```

## Provider key provisioning pattern

Use a tenant-scoped provider key for beta users/dummy tenants. Do not copy Maxim/operator `.env` or broad profile secrets.

OpenRouter key creation requires a **management key**; a normal inference key returns `401 Invalid management key` on `POST /api/v1/keys`.

API payload for a low-limit beta key:

```json
{
  "name": "kira-beta-<uid>-YYYYMMDD",
  "limit": 2,
  "limit_reset": "monthly",
  "include_byok_in_limit": true
}
```

Store the plaintext key immediately; OpenRouter returns it only once. Prefer Yandex Lockbox with entries:

```text
OPENROUTER_API_KEY=<secret>
OPENROUTER_KEY_NAME=kira-beta-<uid>-YYYYMMDD
```

`yc lockbox secret create --payload -` expects the payload to be a JSON array of entries, not an object wrapper:

```json
[
  {"key":"OPENROUTER_API_KEY","text_value":"..."},
  {"key":"OPENROUTER_KEY_NAME","text_value":"kira-beta-<uid>-YYYYMMDD"}
]
```

Install into the tenant Hermes root only:

```text
/data/kira/users/<uid>/assistants/kira/hermes-root/.env        mode 0600 owner <linux_user>
/data/kira/users/<uid>/assistants/kira/hermes-root/config.yaml mode 0600 owner <linux_user>
```

Minimal tenant config used for dummy smoke:

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

## Evidence hygiene

- Never write `sk-or-v1` plaintext into repo evidence.
- Save only key name, limit, reset policy, hash, and Lockbox secret name.
- If key creation succeeds but secret storage fails, delete the orphaned provider key before retrying or explicitly record it as revoked/deleted.
- After provider setup, prove both browser smoke and session API messages: the session should contain the user prompt and an assistant response, not just the echoed prompt in the input UI.
