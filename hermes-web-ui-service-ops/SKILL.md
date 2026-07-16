---
name: hermes-web-ui-service-ops
description: "Mandatory runtime/live-service companion for Hermes Web UI work. Load for any Hermes Web UI task that touches, verifies, updates, restarts, diagnoses, or depends on a running dev/preview/prod service."
---

# Hermes Web UI Service Ops

Use this skill for **runtime evidence and verification** on Hermes Web UI.

For VM beta tenant provider provisioning, see `references/beta-tenant-provider-provisioning.md`: when an OpenRouter management key is available, create a limited tenant key by API, store it in scoped Lockbox, install only into the tenant Hermes root, and verify routed chat plus key-leak hygiene. It covers service state, ports, health, logs, persistence, bridge/socket failures, and post-deploy checks.

For beta-10 G9/G10 hardening, use `references/vm-beta-tenant-g10-g9-ops.md`: sync VM checkouts from pushed Git refs (bundle fallback when GitHub auth is unavailable), keep public tenant Web UI binding aligned with Caddy (`172.17.0.1` vs loopback), rotate expired Authentik API tokens through `ak shell` + Lockbox `add-version`, avoid secret-scanner false positives without disabling scanning, and run non-destructive live tenant backup/restore drills.

For first real trusted beta user G11 onboarding, use `references/vm-beta-real-user-g11-onboarding.md`: map Authentik username separately from tenant UID, run the live tenant contour + route + negative-matrix sequence, require a separate capped provider key/config before chat E2E, and report `PARTIAL / BLOCKED` rather than overclaiming when provider setup is missing.

For G12 prep-only cohort work, use `references/g12-prep-stub-cohort.md`: if Maxim is preparing mechanics rather than doing a real users 2–10 rollout, do not block on real names or routing decisions. Generate deterministic `usr_stub_002`..`usr_stub_010` placeholders with `$2/month` budgets, run tenant validation and dry-run provisioning, and report `PREP PASS / REAL ROLLOUT NOT STARTED`.

For G11 note/vault write failures after chat/provider/upload pass, use `references/vm-beta-tenant-note-file-access.md`: keep broad file operations superadmin-only, allow tenant users only whitelisted tenant-safe note/workspace prefixes, verify with focused server tests plus a browser note smoke, and watch for tenant runtime ownership/listener readiness pitfalls after beta deploys.

Pair it with `hermes-web-ui-operating-model` for planned source-code work: operating-model decides branch/worktree/deploy policy; this skill proves what is actually running.

For Codex coding-agent failures in Web UI global mode (refresh-token reuse, expired tokens, unsupported model, or `Error: [object Object]`), use `references/codex-oauth-global-runs.md`: verify profile-backed `CODEX_HOME`, preserve child-process stderr into user-visible run errors, and prefer a ChatGPT-account-compatible default model such as `gpt-5.4-mini`.

## Live runtime baseline

Verify the current service topology before acting:

- Production public URL: `https://app.kiraproject.ru` (canonical; verify with `/health`, not just inventory)
- Production service: `hermes-web-ui.service`
- Production checkout: `/home/werserk/2-kira/hermes-web-ui`
- Production port: `127.0.0.1:8648`
- Production state: `/home/werserk/.hermes-web-ui`
- Dev live-reload public URL: `https://app.dev.kiraproject.ru` (canonical; verify with `/health`, not just inventory)
- Dev live-reload service: `hermes-web-ui-dev.service`
- Dev live-reload checkout: `/home/werserk/2-kira/hermes-web-ui-dev`
- Dev live-reload frontend port: `8649`
- Dev live-reload backend port: `8647`
- Dev live-reload state: `/home/werserk/.hermes-web-ui-dev`
- Live-dev startup command: `bash scripts/start-live-dev.sh`
- Branch preview command: `bash scripts/deploy-dev-branch.sh <branch>`
- Live-dev transition details: `references/live-dev-transition.md`

## First checks

Run these before diagnosis or success reporting:

```bash
systemctl --user is-active hermes-web-ui.service
systemctl --user show hermes-web-ui.service -p MainPID -p WorkingDirectory -p ExecStart -p Environment --no-pager
ss -ltnp | grep -E ':(8648|8649|8647)\b'
curl -fsS http://127.0.0.1:8648/health
```

For source/runtime drift:

```bash
cd /home/werserk/2-kira/hermes-web-ui
git status --short --branch
git rev-parse HEAD
git log -1 --oneline --decorate
readlink -f /home/werserk/.npm-global/lib/node_modules/hermes-web-ui
node -e "console.log(require('/home/werserk/.npm-global/lib/node_modules/hermes-web-ui/package.json').version)"
```

Prefer the current listener PID, systemd `ExecStart`, and `WorkingDirectory` over old logs, shell cwd, or the repo currently open in the terminal.

## Symptom routing

| Symptom / task | Do this |
|---|---|
| Service down, wrong port, 5xx, restart needed | Run first checks, inspect fresh logs, verify `/health` after restart |
| SQLite readonly/locked/path error | Verify `HERMES_WEB_UI_HOME`, `HERMES_WEBUI_STATE_DIR`, file ownership/writability, `NODE_ENV=production` |
| Create a Web UI space for another person with filesystem privacy | Use a separate Linux user/container, not just a Hermes profile. Set `<root>/active_profile`, run the service as that user, harden systemd paths, change the default Web UI password, and verify OS-level read denial. If Maxim expects the production custom UI, do **not** install stock/npm Web UI; run the custom codebase as the isolated service. See `references/isolated-user-profile-webui.md` and `references/new-user-profile-onboarding.md`. |
| Quickly onboard or polish a new person on existing `app.kiraproject.ru` after Maxim accepts shared runtime/file access | Create a Web UI user plus a separate Hermes profile/workspace under `/home/werserk`; copy working profile auth, set `terminal.cwd`, write user-specific `SOUL.md`/memories, map the user to exactly that profile, verify login/profile visibility and a one-shot chat smoke-test. For later rename/avatar cloning or “make it like Maxim's profile but remove personal paths,” use `references/new-user-profile-onboarding.md`. |
| Extend the YC VM contour for Maxim + friends before PC cutover, beta-10 multi-user work, or `/data/kira/users/<uid>` provisioning | Start with `references/kira-beta-10-vm-target.md`: beta-10 live access targets the explicitly verified Yandex Cloud VM, not the home PC / `werserk-tachka`; home PC is dev/operator/fallback and local `/tmp` smoke only. Then use `references/beta-10-vm-acceptance-execution.md` for gate execution: reconcile inventory vs current YC/SSH reality, treat host-key changes as G0 security blockers, use git bundles if VM GitHub auth is unavailable, record evidence per gate, use loopback-only Web UI tenant runtimes for A7/A8 before public Authentik/Caddy routing, and never call beta-10 complete until the acceptance contract is complete. Then use `references/kira-vm-multi-user-ops.md`: make every change reproducible in `kira-project-lab` repos; model **Kira as an assistant template/brand** with user-owned instances, not assistants named after users; keep separate tenant/runtime namespaces plus compatibility Hermes profile aliases while the runtime catches up; map Web UI accounts to the correct Kira instance/profile alias with the ops script; harden friend preview profiles with explicit provider credentials and `no_mcp`/tool-surface validation; prepare one Telegram bot → many user-owned Kira instances via `profile_routes`; and do not enable VM gateway while the PC gateway is active. For moving Maxim's own full-power Kira to VM as Desktop-first runtime with self-evolution, use `references/maxim-kira-vm-desktop-self-evolution.md`: stage `/data/kira/profiles/maxim-kira`, sync only durable non-secret profile state, use an isolated current `hermes serve` checkout if the VM service checkout lacks `serve`, verify `/api/status` reports the staged profile, and keep Web UI/Telegram cutover approval-gated. For copying Maxim's current PC Kira into the VM tenant route, use `references/pc-kira-to-vm-tenant-copy.md`: identify the actual Caddy upstream/port first, map that port to process env/state paths, snapshot live SQLite with backup API, copy only the intended state/profile, re-apply VM Web UI credentials after the PC DB copy, and verify through public browser login plus real session titles. For routed tenant Web UI and runtime-provider blockers, use `references/vm-beta-tenant-provider-readiness.md`: separate Authentik access, Web UI JWT, bridge reachability, provider/model readiness, and tool-loop denial; use tenant-scoped bridge endpoints and provider keys; OpenRouter key creation requires a management key, not a normal inference key. For a rebuild/cutover acceptance gate, also use `references/kira-vm-fresh-rebuild-acceptance.md`: prove a fresh VM can be provisioned, restored from an explicit backup, run user services, pass tenant isolation, and report caveats before touching the PC contour. |
| Plan or drive Kira YC from beta/preview to fully production-ready | Use `references/kira-yc-production-readiness.md`: keep repo-ready/main-VM/fresh-rebuild/browser-acceptance/ops-readiness/cutover states separate; make browser login and negative tenant checks first-class gates; treat temp password resets, fresh rehearsal VM, DNS cutover, and Telegram gateway cutover as approval-gated; retain PC fallback until cutover and bake pass. |
| Kira VM disk usage, backup bloat, backup deletion/suspension, backup retention, `/data/kira` storage design, or route `502` after a disk-full incident | Use `references/kira-vm-backup-storage-policy.md`: diagnose `/data` vs root disk, enforce daily backup frequency guard, prevent implicit deploy-time backups, keep only short local rollback retention, archive longer history to Object Storage cold/ice appropriately, exclude rebuildable caches/dependencies, and prefer a separate 256 GiB `network-hdd` data disk over root resize. If Maxim explicitly orders deleting `/data/kira/backups` and pausing backup creation, stop/disable `kira-vm-backup.timer`, delete the directory, report that no local backups remain, and treat the VM as not DR-ready until a fresh bounded backup plus restore-smoke pass. After freeing disk, check for stale Docker mount failures and force-recreate only the broken upstream container before broad restarts. |
| Maxim needs temporary VM browser/login credentials for acceptance testing | Use `references/vm-test-access-password-reset.md`: do not reveal old passwords/hashes; generate temporary passwords, reset Authentik and Hermes Web UI credentials, verify both with their native hash/check paths, report only the temp credentials and rotation instruction. |
| VM Web UI chat fails on `openai-codex` with OpenAI/Cloudflare HTML `Unable to load site` / HTTP 403 from the VM IP | Use `references/vm-webui-codex-selective-egress.md`: prove direct-vs-proxied behavior, put `HTTPS_PROXY`/`ALL_PROXY` on the Web UI systemd service, raise `HERMES_CODEX_TTFB_TIMEOUT_SECONDS`, disable Web UI gateway autostart when Telegram cutover is deferred, then verify through the bridge socket. |
| VM Web UI feels much slower than PC, especially for simple chat | Use `references/vm-webui-provider-latency-benchmark.md`: run the same prompts through the PC and VM bridge sockets, then use a direct provider override only as a control to distinguish VM/bridge overhead from provider/egress latency. If the user explicitly wants VM fixed first, audit the VM tenant first before dwelling on PC context: service health → tenant bridge ping/backlog → direct provider timing → tenant bridge model run → tenant logs. For OpenRouter/free-model slowness or `HTTP 429` retry loops, use `references/vm-beta-openrouter-model-rate-limit.md`; a slow 18–20s response with `API call failed after 3 retries` is a failed model path, not healthy generation. Do **not** present provider switching as the fix when the target is to keep `openai-codex`; treat it as a diagnostic control only. If the symptom is slow prod chat rather than VM-vs-PC comparison, use `references/webui-chat-latency-context-split.md` and `scripts/chat_latency_context_split.py` to separate HTTP health, bridge ping, fixed tool/schema overhead, raw history size, compression snapshot size, compression duration, and provider/runtime latency before recommending a fix. Continue with `references/vm-vs-pc-codex-network-path-analysis.md` when the provider path remains suspect. |
| Upgrade lost Kira fork features | Verify active checkout/package and served bundle before porting code |
| Update live Hermes Agent while keeping Kira reachable | Use `references/hermes-agent-update-recovery.md`: stop gateway/Web UI dependents, back up git/systemd state, discard tracked local edits only after approval, normalize `origin` when the updater expects `origin/main`, run `hermes update --yes --backup --branch main`, then restart and verify gateway plus prod/dev Web UI health. |
| Hermes Desktop on one host shows a Python import error after update, while local checkout/import smoke looks clean | Read `references/desktop-remote-backend-stale-import.md`: first inspect `~/.config/Hermes/connection.json`; if Desktop is in remote mode through an SSH `-L` tunnel, debug and restart the remote `hermes serve` service (for Maxim, `hermes-kira-serve.service` on PC), not just the laptop checkout/Electron process. |
| Maxim asks what Tools & Keys → Tools/Settings rows mean, or asks for the whole list | Read `references/tools-keys-settings-inventory.md`: treat rows as profile `.env` variables, list names/meanings without secret values, inspect `OPTIONAL_ENV_VARS` plus `_EXTRA_ENV_KEYS`, explain visible rows first, then group the full list by category. |
| Browser shows old UI after deploy | Compare source commit, built assets, served HTML asset hashes, browser cache/localStorage |
| Dev has current code but wrong users/profiles/access/model visibility vs prod | Treat as dev/prod state drift, not a deploy failure. Compare unit env, `HERMES_WEB_UI_HOME`, `HERMES_HOME`, DB `users`/`user_profiles`, and `config.json`; see `references/dev-prod-access-profile-drift.md`. If Maxim wants dev to show the same chats/statuses as prod without risking prod sockets/state, use the one-way snapshot mirror in `references/prod-to-dev-state-snapshot-mirror.md`: SQLite backup snapshots, stop only dev, preserve dev QA login, copy prod Web UI DB + Hermes profile state/sessions into dev, restart dev, verify prod remains active. |
| Kira needs autonomous browser QA access on dev / create or rotate the dev `kira` superadmin | Use `references/dev-superadmin-qa-account.md`: credential file is local/0600, do not save the password in memory, and remember live-dev `NODE_ENV=development` uses `packages/server/data/hermes-web-ui.db`, not the production-like `HERMES_WEB_UI_HOME` DB. For post-deploy browser smoke through this account, use `references/dev-superadmin-browser-qa.md`; inject API tokens into `localStorage.hermes_api_key`, not guessed auth-token keys. |
| Hermes VoiceSettings integration with a custom/OpenAI-compatible TTS endpoint | Use the existing Voice UI/provider first. If the endpoint is OpenAI-compatible, set `hermes-tts-settings-v2` / the existing `OpenAI TTS` fields (`baseUrl`, `model`, `voice`, optional key) and verify in-browser; do not add server routing, rebuild, or restart just to apply browser-side settings. |
| Hermes VoiceSettings test fails with `TypeError: Failed to fetch` | Check the browser voice settings, direct fetch to the TTS endpoint, and CORS/preflight on the backend before blaming Hermes UI |
| Connect a custom TTS/voice endpoint to Hermes Voice settings | Use the existing OpenAI-compatible Voice UI first (`provider=openai`, base URL/model/voice fields, or `hermes-tts-settings-v2` localStorage). Do not add server-side routing, a new provider, rebuild, or restart the Web UI unless the existing UI cannot express the endpoint. See `references/browser-tts-voice-integration.md`. |
| Connect a custom/OpenAI-compatible browser TTS service such as `voice.ops.kiraproject.ru` | Use the existing **Settings → Voice → OpenAI TTS** UI/localStorage first; do not reroute server TTS or restart production unless code/runtime changes are explicitly needed. See `references/browser-tts-openai-compatible-voice.md`. |
| Deploy/update committed `dev` work to `hermes.dev.ops.kiraproject.ru` | For Maxim's Hermes Web UI dev work, do this automatically after committing unless he explicitly says not to deploy/update. Push `dev`, restart `hermes-web-ui-dev.service`, then verify local and public `/health` report the committed SHA. If the live-dev service is already healthy on the target SHA, do not leave an extra ad-hoc `scripts/start-live-dev.sh` watcher running; kill any temporary duplicate process after verification. |
| Deploy a PR/branch to `hermes.dev.ops.kiraproject.ru` | Use the branch-preview workflow only when explicitly requested; switch `/home/werserk/2-kira/hermes-web-ui-dev`, build, restart the dev service, then verify health and served bundle. If the target branch is already checked out in another worktree, create a short-lived preview branch from the same commit and deploy that instead (see `references/preview-branch-worktree-conflict.md`). If the deployed branch lacks dev-host wrapper files or Vite blocks `hermes.dev.ops.kiraproject.ru`, use `references/branch-preview-dev-host-service-wrapper.md`. |
| Sync `origin/dev` with `origin/main` and verify dev host | Treat branch sync and deployment as separate actions. First fetch and compare ancestry/counts; if `origin/dev` is an ancestor of `origin/main`, a fast-forward push (`git push origin origin/main:dev`) is the narrow update. Then verify `hermes.dev.ops.kiraproject.ru/health`; if it still reports a preview branch/old commit, report source/runtime drift and ask before switching or redeploying the dev service. Do not imply that updating `origin/dev` updated the live dev host. |
| Merge `upstream/main` into live-dev `dev` and verify dev host | After conflicts/build/push, do a controlled `hermes-web-ui-dev.service` restart before declaring stability. Live-dev watchers can observe conflict-marker or half-installed states during a merge, leaving Vite frontend alive while the backend is crashed or stuck. Verify both listeners (`8647`, `8649`) plus local and public `/health` on the merged commit. |
| Convert `hermes.dev.ops.kiraproject.ru` to live-dev | Use `scripts/start-live-dev.sh`, verify `/health`, and confirm the browser-visible change via HMR or controlled restart |
| Bridge timeout/socket closed/Broken pipe/ECONNREFUSED/ENOENT | Read `references/bridge-boundary-troubleshooting.md` |
| Kira/Hermes is active but Telegram messages do not arrive; logs repeat `Conflict: terminated by other getUpdates request` / `Telegram polling conflict` | Read `references/telegram-polling-conflict-duplicate-poller.md`: prove whether another Bot API `getUpdates` poller exists, search across users/system services, stop or reconfigure the duplicate poller, then restart Kira gateway and verify conflict-free polling. |
| Maxim asks whether Telegram Kira is connected through only one Hermes Agent, or reports replies to old/already-finished messages | Read `references/telegram-singleton-and-late-replies.md`: count real gateway argv, compare with `hermes-gateway-kira.service` MainPID/restarts, check Bot API conflict evidence, and distinguish duplicate pollers from delayed background-process/tool completions or reconnect catch-up. |
| Coding agent session fails with `Error: [object Object]`, `Run failed`, `codex exec exited code=1`, or only a user message persisted | Read `references/coding-agent-error-reporting.md`; separate the real child-process failure from UI error serialization, inspect the active Web UI DB session row, and ensure stderr is surfaced in `run.failed.error.message` |
| Codex global run fails with `refresh_token_reused` / “refresh token was already used”, while CLI auth seems fine elsewhere | Read `references/codex-oauth-profile-backed-global-runs.md`; compare the effective `CODEX_HOME`/`HOME` token store with the selected Hermes profile `auth.json`, then use a profile-backed `CODEX_HOME` rather than ambient `.codex` auth |
| `Blocked request` / Vite says host is not allowed | Verify `vite.config.ts` for the live-dev checkout includes `server.allowedHosts` for `hermes.dev.ops.kiraproject.ru`; restart the live-dev service and recheck the public URL |
| `unknown run: <run_id>` appears after starting/restarting another Web UI instance | Check for shared `HERMES_AGENT_BRIDGE_ENDPOINT`; read `references/prod-dev-bridge-endpoint-isolation.md` |
| Session pin does not sync across devices/windows | Inspect the server prefs rows and the owning `sessions.profile`; read `references/session-pins-cross-device-sync.md` before changing code |
| Chat route opens the wrong existing session, session row status drifts/demotes, active session flips after late async callbacks, or Playwright chat/session fixtures drift | Read `references/chat-session-state-stability.md`; keep `/hermes/chat` draft-owned, route-selected sessions explicit, row-state snapshots version-gated, and background catch-up non-selecting. |
| Session says already running/stuck/compression didn't apply | Read `references/session-runtime-ops.md` |
| For browser QA of chat status dots, read/unread transitions, or row state drift | Read `references/session-attention-states.md`; validate the real route/UI flow, API `row_state`, rendered dots, and console together. Read receipts require active route presence fields, not a bare POST. |
| Opening `#/hermes/session/:sessionId` should mark the session read | Treat as a read-receipt contract check, not a navigation bug. Read `references/session-read-status-root-cause.md`; verify route selection, receipt emission, and server schema/API support together before proposing a fix. |
| Session-list pagination might break direct session links | Read `references/session-list-pagination-deep-links.md`; verify first-page request, `Load more` offset request, and a direct hash-route link to a session from a later page. For current hash-router links, use `/#/hermes/session/:id` or `/#/hermes/history/session/:id`, not plain `/hermes/session/:id`. |
| Bulk unread regression repair / backfill | Read `references/bulk-read-status-repair.md`; use a direct DB backfill for a one-time administrative fix after a bad deploy, then verify per-user unread totals. Do not use it as a substitute for the normal browser receipt path. |
| ADR-005 runtime/read semantics | Read `references/adr-005-session-read-runtime-status.md`; `running`/`streaming` should be blue/active, and read receipts should require dwell + focus + visibility + latest-visible-message gating. |
| Context compression `Errno 2`, Unicode surrogate, Codex context cap | Start with bridge/session references; confirm whether compression recovered or snapshot persisted |
| Public hostname/DNS/TLS/Caddy issue | Treat as ops deployment; use the appropriate ops/reverse-proxy skill and verify externally |
| Remove IP allowlist from only one Caddy-hosted dev surface | Use `references/single-host-caddy-allowlist-removal.md`: identify the actual Docker/host Caddyfile, remove `import kira_allowlist` only from the requested host block, validate/reload Caddy, and verify the adapted route has no `remote_ip` matcher |

## Runtime verification rules

- For VM beta tenant Web UI runtime/provider debugging, use `references/vm-beta-tenant-provider-and-bridge-smoke.md` for gate separation, tenant-scoped bridge endpoint, scoped OpenRouter key provisioning, and evidence hygiene.
- For beta-10 G9/G10 VM operations, use `references/vm-beta-tenant-g10-g9-ops.md`: rotate expired Authentik API tokens without printing secrets, update Lockbox via a new version, distinguish operator-side helper permissions from VM Lockbox permissions, bind public routed tenant Web UI services to the Docker bridge host while keeping private dummy tenants loopback-only, and prove live backup/restore into a clean separate target.
- For beta tenant provider setup and G7/G8 routed runtime smokes, use `references/beta-tenant-provider-and-tool-smokes.md`. Pitfalls from the first `usr_test_001` run: if Maxim supplies an OpenRouter management key, use the OpenRouter API directly instead of asking for browser login; Yandex Lockbox `--payload -` expects a JSON array of entries; if key creation succeeds but secret storage fails, delete the orphaned key by hash or securely store the one-time plaintext immediately; grep evidence/script paths for `sk-or-v1` before reporting success.
- A completed document, plan, temp smoke test, or single acceptance gate is not the overall goal. When executing beta/multi-user/runtime work, report the specific gate or artifact as `PASS`/`PARTIAL`/`BLOCKED` and name remaining gates; do not say “goal complete” until the governing acceptance contract is fully satisfied.
- A build is not a deploy; verify the running service separately.
- A merged PR is not a deploy; check the `Build` workflow outcome and only trust `Deploy Hermes Prod` when it is a real non-skipped deploy for the target commit.
- A red `Playwright` workflow is not automatically a product/e2e failure: inspect the failed step. If `Run Playwright tests` passed and only `Upload Playwright report` failed with GitHub artifact storage quota, treat it as a CI artifact-retention caveat, not a deploy blocker, after local e2e + `Build` + `Deploy Hermes Prod` + `/health` on the target SHA are green. See `references/github-actions-artifact-quota-after-tests.md`.
- A restarted service is not enough; verify listener and `/health` in a fresh command after restart.
- For live-dev restarts, Vite on `8649` often becomes ready before the backend on `8647`; initial `ECONNREFUSED` proxy/health errors during boot are not proof of failure. Wait for the backend listener or `[bootstrap] listening on ...:8647`, then retry local and public `/health` before reporting a restart problem.
- Healthy backend is not enough for browser-visible work; verify served bundle and browser boot when UI changed.
- For browser TTS work, a successful direct fetch to the audio endpoint is stronger evidence than a UI test button alone.
- If Hermes VoiceSettings already has a compatible provider (for example OpenAI-compatible speech), prefer filling the existing UI/localStorage settings over code changes. A settings-only browser change does not require a build or service restart.
- For live-dev, success means the browser-visible change propagates through HMR or a controlled watch restart; do not rely only on `/health`.
- After restarting `hermes-web-ui-dev.service`, `systemctl is-active` can turn `active` before the backend listener on `:8647` is ready. If the first `/health` curl gets `ECONNREFUSED`, wait and verify `ss -ltnp` shows both `:8647` and `:8649` before treating it as a failure.
- After starting a new standalone Web UI instance, `systemctl active` can precede `[bootstrap] listening on ...:<port>` by several seconds. Check the journal for the listening log and retry HTTP before reporting a startup failure.
- Source commit and served asset hash are separate evidence layers; report both when diagnosing deploy drift.
- When answering “is the latest `origin/main` deployed?”, compare the runtime-reported `git_commit` on each live surface against `origin/main` explicitly. `origin/main` matching `origin/dev` does **not** imply prod is current; prod and live-dev are separate deploy targets and must be checked independently.
- For live-dev Vite SFC verification, distinguish script source from compiled scoped style modules: `/src/components/Foo.vue` verifies template/script selectors, while CSS rules may only appear under `/src/components/Foo.vue?vue&type=style&index=0&scoped=<id>&lang.scss` or the built CSS asset. If checking a style fix such as active colors or separators, verify the served style module/bundle, not only the main `.vue` module.
- In Vite live-dev, `/src/components/Foo.vue` is often a transformed module rather than literal SFC text: template attributes and SVG paths can be normalized into hoisted JS objects. For deployed-source checks, prefer semantic substrings that survive transform (class names, path `d` fragments without exact tag syntax, absence of removed glyph path fragments) instead of exact raw-SFC lines unless you intentionally request a raw import.
- Stale browser tabs, cached assets, and localStorage can hide successful deploys; hard-refresh/reopen before changing code.
- Do not infer DB/state paths from a deleted cwd in `ps`; use systemd environment and fresh logs.
- When prod/dev/preview Web UI instances run concurrently on one host, each unit must set a distinct `HERMES_AGENT_BRIDGE_ENDPOINT`; the default `/tmp/hermes-agent-bridge.sock` is singleton-shaped and can route `get_output` to the wrong in-memory broker, causing `unknown run` errors.
- See `references/prod-vs-runtime-drift.md` for a compact verification pattern and example outputs.

## Minimal recovery order

1. Keep or restore the stable surface first.
2. Confirm active unit, pid, listener, port, health.
3. Inspect newest `server.log` and `bridge.log` lines around the failure.
4. Identify whether the issue is service process, source/bundle drift, persistence/SQLite, bridge/socket, or session lifecycle.
5. Apply the narrowest fix.
6. Restart only the necessary service(s).
7. Re-run health + browser/runtime verification.

## Completion checklist

Before reporting success for runtime work:

- `systemctl --user is-active hermes-web-ui.service` returns `active`.
- `ss -ltnp` shows a listener on `:8648` for production.
- `curl -fsS http://127.0.0.1:8648/health` succeeds.
- Systemd `ExecStart`/`WorkingDirectory` match the intended checkout/package.
- Fresh logs show no new critical SQLite/bridge startup errors.
- Browser-visible changes are verified against served assets or a fresh browser page.

## References

- `references/beta-vm-acceptance-evidence-patterns.md` — repeatable beta VM acceptance evidence patterns: negative matrix smoke shape, G10→G11 transition checklist, and anti-overclaim reporting.

- `references/vm-beta-tenant-provider-readiness.md` — beta VM routed tenant Web UI/runtime readiness: distinguish Authentik access, Web UI JWT, tenant profile visibility, bridge endpoint isolation, provider/model key configuration, OpenRouter management-key requirement, and tool-loop denial evidence.
- `references/hermes-agent-update-recovery.md` — update the live Hermes Agent checkout that gateway/Web UI bridges depend on, with service stop/start order, backup, origin/upstream normalization, and health verification.
- `references/dev-pr-branch-deploy.md` — exact workflow for deploying a PR branch to `hermes.dev.ops.kiraproject.ru` via `/home/werserk/2-kira/hermes-web-ui-dev` and `hermes-web-ui-dev.service`.
- `references/live-service-baseline.md` — exact live service probe sequence.
- `references/live-bundle-verification.md` — source commit vs served asset hash verification.
- `references/browser-tts-voice-integration.md` — browser-side Hermes voice setup, localStorage key, CORS/fetch verification pattern.
- `references/bridge-boundary-troubleshooting.md` — bridge/socket/runtime-provider/compression boundary failures.
- `references/session-pins-cross-device-sync.md` — profile-binding and pruning pitfalls for server-backed pinned-session sync across devices.
- `references/chat-session-state-stability.md` — chat draft-route ownership, explicit session selection, late-callback guards, row-state version gating, and Playwright fixture drift patterns for chat/session stability work.
- `references/session-runtime-ops.md` — session lookup, stuck sessions, Socket.IO commands, compression snapshots.
- `references/coding-agent-error-reporting.md` — Codex / Claude Code run-failure diagnosis and durable stderr + error-normalization contracts.
- `references/codex-oauth-profile-backed-global-runs.md` — Codex global-mode OAuth token-store drift, profile-backed `CODEX_HOME`, refresh-token reuse diagnosis, and model-compatibility follow-up checks.
- `references/session-url-inspection.md` — browser/API workflow for reading and summarizing a Hermes Web UI session URL across profiles.
- `references/telegram-singleton-and-late-replies.md` — Telegram Kira singleton proof: count real gateway argv, compare systemd MainPID/restarts, check Bot API polling conflicts, and distinguish duplicates from late background/tool completions.
- `references/desktop-remote-backend-stale-import.md` — Hermes Desktop remote-mode import errors after agent updates: identify tunneled backend services, restart stale `hermes serve` processes, and verify through the desktop tunnel.
- `references/tools-keys-settings-inventory.md` — safe inventory pattern for Web UI Tools & Keys rows: explain `.env` variable meanings without revealing secrets, using `OPTIONAL_ENV_VARS` plus `_EXTRA_ENV_KEYS` as the source.
- `references/adr-005-session-read-runtime-status.md` — ADR-005-specific mapping for blue `running/streaming` semantics and the dwell/focus/visibility read-receipt gate.
- `references/readonly-database-webui.md` — SQLite readonly recovery.
- `references/fork-upgrade-drift-recovery.md` and `references/upgrade-fork-drift-audit.md` — npm/upstream upgrade drift.
- `references/deploy-restart-race.md` — restart/listener/health timing.
- `references/multi-instance-topology.md` — production/preview isolation model.
- `references/prod-dev-bridge-endpoint-isolation.md` — prevent prod/dev bridge socket collisions and diagnose `unknown run` after another instance starts.
- `references/prod-to-dev-state-snapshot-mirror.md` — safely mirror prod chats/statuses/profiles into live-dev by snapshotting prod DB/profile state, stopping only dev, preserving dev QA access, and verifying prod socket isolation. Includes reusable helper `scripts/prod_to_dev_state_snapshot_mirror.py`.
- `references/new-user-profile-onboarding.md` — fast shared-host onboarding vs isolated onboarding, Web UI user/profile setup, credential-copy pitfall, and smoke-test checklist.
- `references/kira-vm-multi-user-ops.md` — YC VM multi-user contour: reproducible `kira-project-lab` ops, `/data/kira` profile/workspace layout, Web UI account→profile mapping, one Telegram bot→many profile routing, backup/restore/health evidence, and no PC cutover until Maxim approves.
- `references/g12-prep-stub-cohort.md` — prep-only G12 stub cohort pattern: generate deterministic users 2–10 placeholders with `$2/month` budgets, run validation/dry-run provisioning, and avoid asking for real user/routing inputs until live rollout begins.
- `references/kira-vm-fresh-rebuild-acceptance.md` — fresh YC VM rebuild rehearsal: provision from repo, restore explicit backup artifacts, validate user systemd services from root, tenant isolation, service health, and caveat-based acceptance reporting.
- `references/vm-webui-codex-selective-egress.md` — diagnose/fix VM Web UI `openai-codex` Cloudflare/403 HTML blocks by routing the Web UI bridge service through selective SOCKS egress, tuning Codex TTFB, and verifying via bridge socket.
- `references/vm-webui-provider-latency-benchmark.md` — bridge-level PC vs VM latency benchmark pattern for separating VM/Web UI overhead from provider/egress slowdown, including the three-prompt test set and direct-provider control runs.
- `references/vm-beta-openrouter-model-rate-limit.md` — VM beta tenant OpenRouter/free-model latency diagnosis: separate service/bridge health from direct provider timing, catch `HTTP 429` retry loops in tenant logs, and choose a bridge-verified replacement model before changing live tenant config.
- `references/vm-vs-pc-codex-network-path-analysis.md` — follow-up analysis when `openai-codex` must remain the target: compare PC Hiddify TUN/policy routing with VM Xray SOCKS selective egress, curl timings, and proxy timeout signatures before recommending fixes.
- `references/hostname-route-validation.md`, `references/live-domain-cutover.md`, `references/cross-domain-hostname-alias-cutover.md` — hostname/DNS/TLS cutovers.
