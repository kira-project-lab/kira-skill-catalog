# Maxim Kira VM Desktop backend + self-evolution pattern

Use this reference when moving Maxim's own Kira profile to the YC VM as a Desktop-first runtime, or when adding `hermes-agent-self-evolution` as a report-only ops loop.

## Durable pattern

- Treat Maxim's VM Kira as the first full-power Kira instance, not as a generic beta Web UI tenant.
- Keep PC as fallback until Desktop-to-VM backend acceptance and any Telegram cutover bake pass.
- Stage the profile first under `/data/kira/profiles/maxim-kira`; do not immediately replace live PC runtime.
- Copy only durable non-secret profile state: `SOUL.md`, `config.yaml`, `memories/MEMORY.md`, `memories/USER.md`, `skills/`, and selected plugin code/templates.
- Exclude `.env`, auth tokens, runtime SQLite DBs, sessions, logs, caches, browser state, and generated runtime state.
- Install `hermes-agent-self-evolution` as a proposal generator. It may dry-run and write reports/diffs, but must not auto-apply to the live profile.
- Archive Hermes Web UI/Studio only after Desktop VM acceptance passes; archive means stop/disable/snapshot with rollback, not delete repos.
- Telegram cutover is separate and approval-gated; never run the same bot from PC and VM without an explicit cutover window.

## Useful VM layout

```text
/data/kira/profiles/maxim-kira
/data/kira/workspaces/maxim
/data/kira/repos/hermes-agent-self-evolution
/data/kira/repos/hermes-agent-desktop-backend
/data/kira/evolution/{runs,datasets,reports}
```

## Safe profile sync allowlist

```bash
ssh kira-yc 'sudo install -d -o kira -g kira -m 0755 /data/kira/profiles /data/kira/profiles/maxim-kira'

rsync -a --delete \
  --include='/SOUL.md' --include='/config.yaml' \
  --include='/memories/' --include='/memories/MEMORY.md' --include='/memories/USER.md' \
  --include='/skills/***' \
  --include='/plugins/' --include='/plugins/*.py' --include='/plugins/*/SKILL.md' \
  --exclude='*' \
  /home/werserk/2-kira/kira-hermes-profile/profile/ \
  kira-yc:/data/kira/profiles/maxim-kira/
```

Verify absence of accidental secrets/runtime state:

```bash
ssh kira-yc '
  test ! -e /data/kira/profiles/maxim-kira/.env
  test ! -e /data/kira/profiles/maxim-kira/state.db
  HERMES_HOME=/data/kira/profiles/maxim-kira \
    /path/to/current/hermes config check
  HERMES_HOME=/data/kira/profiles/maxim-kira \
    /path/to/current/hermes skills list | sed -n "1,80p"
'
```

## Desktop backend pitfall

On the YC VM, an older service checkout under `/opt/kira/services/hermes-agent` may not support `hermes serve`. Do not mutate that production service checkout just to satisfy Desktop.

Instead, install an isolated current backend checkout such as:

```text
/data/kira/repos/hermes-agent-desktop-backend
```

Service pattern:

```ini
[Unit]
Description=Maxim Kira Hermes backend server on YC VM
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/data/kira/workspaces/maxim
Environment=HOME=/home/kira
Environment=HERMES_HOME=/data/kira/profiles/maxim-kira
ExecStart=/data/kira/repos/hermes-agent-desktop-backend/.venv/bin/hermes serve --host 127.0.0.1 --port 9119 --isolated
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

Verify with `/api/status`, not only `/health`:

```bash
ssh kira-yc '
  systemctl --user is-active maxim-kira-hermes-serve.service
  ss -ltnp | grep :9119
  curl -fsS http://127.0.0.1:9119/api/status
'
```

Expected payload should include:

```text
"hermes_home":"/data/kira/profiles/maxim-kira"
"config_path":"/data/kira/profiles/maxim-kira/config.yaml"
"gateway_running":false
```

`/api/health` can return `401 Unauthorized`; that is not by itself a backend failure.

## Self-evolution dry-run check

```bash
ssh kira-yc '
  cd /data/kira/repos/hermes-agent-self-evolution
  . .venv/bin/activate
  python -m evolution.skills.evolve_skill \
    --skill systematic-debugging \
    --iterations 1 \
    --eval-source synthetic \
    --hermes-repo /data/kira/profiles/maxim-kira \
    --dry-run
'
```

Expected:

```text
DRY RUN — setup validated successfully.
```

## Acceptance gates before claiming completion

- Desktop is actually configured to VM backend and a real chat/tool session runs on `kira-main-ops-01`.
- Backend `/api/status` reports the staged Maxim profile path.
- Terminal/file smoke proves VM execution and intended workspace scoping.
- Required secrets are recreated from Lockbox/scoped env, not copied raw from PC.
- Web UI archive/disable happens only after Desktop VM acceptance.
- Telegram cutover happens only after duplicate-gateway risk is resolved and Maxim approves.
