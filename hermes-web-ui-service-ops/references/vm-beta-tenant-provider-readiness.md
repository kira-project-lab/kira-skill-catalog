# VM beta tenant provider readiness

Use this when a VM beta tenant can log into the routed Web UI but chat/runtime smokes fail before a model response.

## Gate separation

Keep these checks separate in evidence:

1. Public Authentik route reaches the tenant surface.
2. Web UI JWT/session maps to the tenant user and allowed profile(s).
3. Agent bridge starts and uses a tenant-scoped endpoint.
4. Tenant Hermes profile has a provider/model/API key.
5. Tool-loop policy denial is proven with a working runtime.

A browser reaching `/#/hermes/chat` is not a runtime pass. A saved user prompt is not a model-response pass.

## Common failure sequence

### Authentik permission denied

If Authentik shows `Permission denied` after login, inspect application/policy bindings. In the beta VM case, `usr_test_001` had only `kira-ops` but the `kira-vm-web-ui` application binding allowed `kira-users`; adding the user to the existing `kira-users` group fixed the routed app permission without changing the application/provider policy objects.

### Web UI still returns 401

Authentik forward-auth and Web UI JWT are separate. A Playwright/browser smoke may need to establish a Web UI tenant token with `/api/auth/login` and then set `localStorage.hermes_api_key` plus `localStorage.hermes_active_profile_name` before API checks. Verify `/api/auth/me` returns the tenant username before claiming Web UI tenant mapping.

### Agent bridge ENOENT / wrong root

If chat shows `Agent Bridge is not reachable: connect ENOENT configured endpoint`, inspect the tenant service logs and run the bridge manually as the tenant user. In the VM beta runtime, the bridge tried `/home/kira/run_agent.py` and failed with permission denied. The tenant unit needed:

```ini
Environment=HERMES_AGENT_ROOT=/opt/kira/services/hermes-agent
Environment=HERMES_AGENT_BRIDGE_BASE_HOME=/data/kira/users/<uid>/assistants/kira/hermes-root
Environment=HERMES_AGENT_BRIDGE_ENDPOINT=ipc:///data/kira/users/<uid>/assistants/kira/web-ui-state/agent-bridge.sock
ReadOnlyPaths=/opt/kira/repos/hermes-web-ui-beta /opt/kira/services/hermes-agent
```

Do not use the global default `/tmp/hermes-agent-bridge.sock` for multiple tenant runtimes; each tenant Web UI service should have a private bridge endpoint under its own writable state root.

### No inference provider configured

If the routed chat reaches the bridge but shows:

```text
No inference provider configured. Run ‘hermes model’ to choose a provider and model, or set an API key (OPENROUTER_API_KEY, OPENAI_API_KEY, etc.) in ~/.hermes/.env.
```

then the next missing gate is provider/model readiness, not Web UI auth.

Use a tenant-scoped provider key, not Maxim/operator `.env` or a broad copied profile. Preferred pattern:

- separate beta-test OpenRouter/OpenAI key;
- low spend cap, e.g. `$2`; 
- stored in a scoped secret or tenant `.env` with `0600` permissions;
- minimal `config.yaml` model/provider entry for the tenant profile;
- no copy of `auth.json`, operator profile secrets, SSH keys, or broad `.env`.

OpenRouter key creation note: `POST https://openrouter.ai/api/v1/keys` requires a **management key**. A normal inference `OPENROUTER_API_KEY` can return `401 Invalid management key`; do not treat that as OpenRouter being down. If browser login is needed, stop at the login/2FA/payment boundary and ask the user to authenticate or provide a scoped management key.

## Evidence wording

Use `PARTIAL PASS` or `BLOCKED` precisely:

- `PARTIAL PASS`: Authentik route, Web UI tenant token, profile visibility, and representative admin-route denial passed.
- `BLOCKED`: tenant chat reaches bridge but no provider/model key exists.
- Do not claim G7/G8 pass until a real model response and tool-loop denial are proven under the tenant profile.
