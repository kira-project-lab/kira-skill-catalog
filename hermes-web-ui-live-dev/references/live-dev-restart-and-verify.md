# Live-dev restart and verify

Use this when a Hermes Web UI change has passed local tests/build and must be made active on the public dev host.

## Preferred path

From `/home/werserk/2-kira/hermes-web-ui-dev`:

```bash
git fetch origin dev
git status --short --branch
git rev-parse HEAD
systemctl --user restart hermes-web-ui-dev.service
```

Then poll the frontend health surface, not backend port 8647:

```bash
curl -fsS http://127.0.0.1:8649/health
curl -fsS https://app.dev.kiraproject.ru/health
```

Expected fields:

- `runtime: live-dev`
- `git_branch: dev`
- `git_commit` equals the intended checkout/ref
- `service: hermes-web-ui-dev.service`
- `service_port: 8647`
- `frontend_port: 8649`

A brief `502` during restart is a transient restart window; keep polling until green or until a real timeout.

## If restart via systemd is unavailable

Do not switch to `sudo systemctl` first. If the user-unit is unavailable in the current tool session, or systemd returns an interactive-auth/sudo prompt, use the documented live-dev script instead:

```bash
cd /home/werserk/2-kira/hermes-web-ui-dev
bash scripts/start-live-dev.sh
```

For agent/tool execution, start it as a tracked long-lived background process rather than shell-backgrounding with `&`; then verify with `/health` on 8649 and the public dev host. The Vite frontend process can serve `/health` on `8649` even when direct `127.0.0.1:8647/health` is not reachable in live-dev mode.

## Reporting rule

Do not claim the public dev host is updated solely because tests/build passed or CodeGraph synced. Report live-dev activation only after `/health` shows the expected commit/runtime. If restart is blocked by permissions or tool-session limits, say exactly that and leave the next command.
