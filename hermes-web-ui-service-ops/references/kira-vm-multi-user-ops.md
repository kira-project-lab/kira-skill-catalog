# Kira VM multi-user Web UI and gateway ops

Use this when extending the YC VM Kira contour for multiple users/friends while the PC contour remains the fallback.

## Durable pattern

- Treat the VM contour as a reproducible deployment, not a pile of live hotfixes.
- Put operational scripts/templates/runbooks/evidence in `kira-project-lab/kira-ops` first, then deploy to `/opt/kira/ops-repo` and `/opt/kira/ops` on `kira-yc`.
- Put Hermes Agent gateway/runtime code changes in `kira-project-lab/kira-hermes-agent` first, then apply/update the VM service checkout.
- Do not move `app.kiraproject.ru` or disable PC services until Maxim explicitly verifies the VM contour and asks for cutover.

## Minimal multi-user layout

Do not model "Kira for Sonya/Polina" as assistants named `sonya` or `polina`. Product-wise, the assistant remains **Kira** for every user; the user/account is the tenant namespace that owns a Kira instance.

For small bootstrap deployments, a flat profile map may exist temporarily, but the target shape is:

```text
assistant/template: kira              # brand/persona/product definition
account/tenant: <user_id or username> # human owner namespace
instance: <tenant>/assistants/kira     # that user's Kira
```

Recommended durable filesystem shape:

```text
/data/kira/users/<user_id>/assistants/kira/profile
/data/kira/users/<user_id>/assistants/kira/workspace
/data/kira/users/<user_id>/assistants/kira/memory
/data/kira/users/<user_id>/{.ssh,git,obsidian}
/data/kira/shared/{skills-readonly,public-memory,shared-docs}
```

If current tooling still requires flat Hermes profile IDs, use them as compatibility aliases only; do not let the UI/persona imply the assistant is named after the user. The UI label should stay `Кира`, with an owner/context subtitle if needed (`для Sonya`, `workspace Sonya`).

Friend Kira instances can read shared skills/docs, but should not get Maxim's profile, secrets, Obsidian vault, infra SSH keys, deploy scripts, or YC admin credentials.

## Web UI account -> Kira instance mapping

The Web UI account layer, human tenant namespace, Kira assistant definition, and Hermes runtime profile are separate. Do not present technical profile IDs as assistant names.

Target conceptual mapping:

```text
werserk -> users/<maxim_id>/assistants/kira
sonya   -> users/<sonya_id>/assistants/kira
polina  -> users/<polina_id>/assistants/kira
```

Current compatibility mapping script may still map accounts to flat Hermes profile IDs while the runtime catches up:

```bash
/opt/kira/ops/scripts/apply-webui-profile-map.py \
  /data/kira/state/hermes-web-ui-preview/hermes-web-ui.db \
  werserk=<maxim_kira_profile_alias> sonya=<sonya_kira_profile_alias> polina=<polina_kira_profile_alias>
```

Expected product baseline:

```text
assistant display name: Кира
owner/account: werserk | sonya | polina
runtime namespace: distinct per owner
```

Avoid a visible state where `sonya` or `polina` looks like the assistant/persona name; they are owners/tenants only.

## Authentik account naming

For Maxim, use `werserk` as the human-facing Authentik username. Do not present the account as `admin`/`akadmin` even if it has superuser privileges or originated from an Authentik bootstrap admin account. Keep role/privilege as a separate field from the account name.

Friend Authentik usernames should match their Web UI/profile names when practical (`sonya`, `polina`, etc.) so SSO, Web UI users, and Hermes profile mappings stay legible.

## One Telegram bot -> many Kira instances

Preferred target is one Telegram bot branded as Kira, with routing by Telegram user ID to the user's own Kira namespace:

```yaml
platforms:
  telegram:
    extra:
      profile_routes:
        users:
          "<maxim_tg_id>": users/<maxim_id>/assistants/kira
          "<sonya_tg_id>": users/<sonya_id>/assistants/kira
          "<polina_tg_id>": users/<polina_id>/assistants/kira
```

If the current gateway only accepts flat Hermes profile IDs, route to compatibility aliases but keep the product language as "Кира" for everyone.

Gateway implementation rule: keep a single parent bot connection and route each message to a target profile subprocess with the target `HERMES_HOME`. Do **not** switch global process profile state in-process for concurrent users.

The systemd unit needs:

```ini
Environment="HERMES_GATEWAY_PROFILE_ROOTS=/data/kira/profiles"
```

Never enable the VM gateway for the same bot while the PC gateway is active, unless Maxim explicitly requests cutover; duplicate bot processors can create double replies or state races.

## Friend preview profile hardening

For friends in preview, avoid copying Maxim's full profile just to make chat work.

- Visible identity stays `profile_display_name: Кира`; compatibility profile IDs such as `sonya`/`polina` are not assistant names.
- If separate Codex OAuth credentials are not ready, configure a preview provider explicitly (for example OpenRouter) and copy only the provider key required for that preview profile. Do not copy `auth.json` or broad `.env` secrets from Maxim's profile.
- Restrict preview friend profiles with `platform_toolsets.cli: [no_mcp]` unless their task explicitly needs tools. Validate the effective tool surface through the bridge/runtime, not just by reading config; expected preview baseline is `tool_count: 0`.
- Run a negative privacy smoke after tool restriction: prompt the friend profile to read Maxim-only paths such as `/data/kira/profiles/kira/config.yaml` and `/data/kira/users/werserk/assistants/kira`. A clean refusal/denial is acceptable; a no-content provider error is not a privacy pass, only evidence that the read path was not successfully exercised.
- Treat any successful read of Maxim's config/profile by a friend profile as a release blocker until tool/runtime or OS isolation is tightened and re-tested.

## Validation checklist

- `systemctl --user list-timers` includes backup, restore-smoke, and health timers.
- `check-kira-vm-health.sh` passes Web UI, agentmemory, Paperclip, Codex proxy, assistant-instance registry/layout, Web UI mapping, and latest backup checks.
- `backup-kira-vm.sh` excludes large disposable caches (`home/.cache`, npm cache/npx, HuggingFace cache) so backups are bounded.
- Do not trust `PASS backup latest-vm present` or restore-smoke alone as disaster-recovery proof. Inspect the actual `latest-vm` archive list and manifest: for a full beta DR claim it should include service artifacts, UID tenant users, shared data, service state, and Authentik coverage when SSO restore is in scope (`services.tgz`, `users.tgz`, `shared.tgz`, `state.tgz`, `authentik.tgz` or an explicit documented replacement). If the script supports these archives but the latest backup predates the support, create a fresh backup before claiming readiness.
- `restore-kira-vm-smoke.sh` passes against `latest-vm`. If cleanup fails on extracted read-only shared skills, fix the script to `chmod -R u+rwX "$work"` before `rm -rf`; do not count the timer as production-ready until restore-smoke passes after that fix.
- Compare source-of-truth repo and runtime checkout separately. A clean `/opt/kira/repos/kira-ops` on `origin/main` plus a dirty `/opt/kira/ops` runtime tree can be functionally OK, but it is a reproducibility gap until deployment state explains the runtime copy. Report it as source/runtime drift, not service failure.
- If a GitHub deploy runs a VM-side script that fetches/resets its own checkout, changes to that script may not affect the already-running shell process. Expect the first deploy of a self-updating deploy script to still use old in-memory control flow; rerun the workflow after the checkout has landed on the VM before diagnosing the new script as broken.
- Backup validation over multi-GB artifacts can take several minutes because tar headers and checksums are read. Prefer deploy logic that creates a fresh backup only when `latest-vm` fails schema validation; otherwise health can validate the existing complete backup without producing another multi-GB archive on docs-only deploys.
- Verify public routes with strict TLS first (no `curl -k` unless explicitly diagnosing certificates), and verify DNS for every intended browser-facing hostname. A missing hostname such as `memory.vm...` is either a routing gap or an out-of-scope surface; label it explicitly.
- For Codex egress, prefer an actual `codex-vpn exec --skip-git-repo-check "Print exactly: ..."` smoke over curl-only endpoint probes. Curl `401`/`403` can still be useful as network evidence, but it does not prove the authenticated Codex CLI path works.
- `codex-vpn exec ...` or the current Codex egress checker succeeds on the VM without direct-region `403`/timeout.
- Run bridge smoke per active profile/compatibility alias (`kira`, friend aliases) before declaring users ready. A green VM/Web UI health check is not enough: friend profiles can still fail with `No Codex credentials stored` if their profile lacks provider auth.
- Product naming check: friend profile runtime may use compatibility aliases such as `sonya`/`polina`, but visible assistant/display name should be `Кира`; owner names are labels only.
- Friend browser smoke: friend sees only their Kira instance/profile, can write only in their workspace, and cannot read Maxim's Kira namespace such as `/data/kira/profiles/kira` or `/data/kira/users/werserk/assistants/kira`.
- No-Telegram acceptance: VM Web UI, Authentik redirect, bridge profiles, backup/restore, Paperclip, agentmemory, and egress can be accepted without enabling `hermes-gateway-kira.service`; keep the VM gateway disabled/inactive while the PC gateway is active.
- Full browser-facing acceptance still needs real SSO/Web UI login for each target account. Do not report it complete if only the Authentik login page/redirect was verified.
- For VM beta tenant Web UI acceptance, distinguish Authentik access from Web UI JWT access and from Hermes Agent runtime success. A browser can reach the chat route while `/api/auth/me` is still `401`; smoke tests should establish/check the Web UI tenant token separately. A chat message can then reach the bridge but still fail if the tenant profile lacks an inference provider. Report these as separate gates: public route/auth, Web UI tenant API mapping, bridge reachability, provider/model readiness, and tool-loop policy denial.
- For dummy/friend tenant provider setup, use a scoped provider key rather than copying Maxim/operator `.env`. If the user provides an OpenRouter **management key**, use the OpenRouter API directly (`POST https://openrouter.ai/api/v1/keys` with `limit` and `limit_reset`) before asking for browser login. A normal OpenRouter inference key is not enough to create subkeys; verify capability with `/api/v1/auth/key` (`is_management_key`). Store the newly-created plaintext key immediately in a scoped secret such as Yandex Lockbox and tenant `.env`; never write it to repo evidence. Record only key name, spending limit, reset period, and hash.
- Tenant Web UI units need a real Hermes Agent root and a tenant-scoped Agent Bridge endpoint. If routed chat fails with `Agent Bridge is not reachable: connect ENOENT configured endpoint`, verify the unit has `HERMES_AGENT_ROOT=/opt/kira/services/hermes-agent`, `HERMES_AGENT_BRIDGE_BASE_HOME=<tenant hermes-root>`, and `HERMES_AGENT_BRIDGE_ENDPOINT=ipc://<tenant web-ui-state>/agent-bridge.sock`. Do not leave multiple tenants sharing the default `/tmp/hermes-agent-bridge.sock`.
- For VM beta tenant Web UI acceptance, distinguish Authentik access from Web UI JWT access and from Hermes Agent runtime success. A browser can reach the chat route while `/api/auth/me` is still `401`; smoke tests should establish/check the Web UI tenant token separately. A chat message can then reach the bridge but still fail if the tenant profile lacks an inference provider. Report these as separate gates: public route/auth, Web UI tenant API mapping, bridge reachability, provider/model readiness, and tool-loop policy denial.
- For G9 backup/restore acceptance, do not stop at a temp-only restore smoke once a real dummy tenant exists. Add or run a repo-owned live restore drill that archives the real tenant components (`profile`, `web-ui-state`, `agentmemory`, runtime/Hermes root, `workspace`, `uploads`, `exports`) into the tenant backup directory, verifies `manifest.json` and `checksums.sha256`, restores only into a clean separate `/data/kira/restore-drills/<uid>-...` target, checks restored file privacy, and confirms the tenant service restarts/returns active. Never restore over the live tenant root during acceptance proof.
- For G10 support/disable evidence, separate runtime observability from Authentik control-plane health. It is a partial pass if the operator can see tenant service health, `/health`, bridge socket, provider/model, and effective tool policy, but disable/status helpers that depend on Authentik still need a currently valid API token. If an Authentik helper returns `403 {"detail":"Token invalid/expired"}`, record a blocked evidence artifact and rotate/replace the token before claiming G10 pass or moving to G11.
- `kira-ops` secret scanning can flag non-secret default names in helper scripts when literals look like `TOKEN`/`SECRET` assignments with long values. Do not disable scanning or store secrets in repo; either split non-secret key-name constants into shorter string fragments or add an explicit safe pattern to the scanner, then rerun `./bin/kira validate all` locally and on the VM checkout.

## Evidence discipline

Record operational evidence under `kira-ops/docs/evidence/` and keep the Obsidian plan as the human-readable target state. Evidence should list commits, applied VM paths, enabled timers, validation commands, and remaining blockers such as missing friend Telegram IDs or deferred gateway cutover.
