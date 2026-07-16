# Live service baseline

Use this before changing or reporting on a running Hermes Web UI service.

## Expected Kira production target

- Unit: `hermes-web-ui.service`
- Checkout: `/home/werserk/2-kira/hermes-web-ui`
- ExecStart: `/usr/bin/node /home/werserk/2-kira/hermes-web-ui/dist/server/index.js`
- Port: `127.0.0.1:8648`
- Hermes profile: `/home/werserk/.hermes/profiles/kira`
- Web UI state: `/home/werserk/.hermes-web-ui`

## Probe sequence

```bash
systemctl --user status hermes-web-ui.service --no-pager
systemctl --user show hermes-web-ui.service -p MainPID -p WorkingDirectory -p ExecStart -p Environment --no-pager
ss -ltnp | grep ':8648'
curl -fsS http://127.0.0.1:8648/health
```

If any command fails, do not guess. Inspect fresh logs:

```bash
# Use read_file/tooling when available rather than cat.
# Log paths:
~/.hermes-web-ui/logs/server.log
~/.hermes-web-ui/logs/bridge.log
```

## Source/package drift checks

```bash
cd /home/werserk/2-kira/hermes-web-ui
git status --short --branch
git rev-parse HEAD
git log -1 --oneline --decorate
readlink -f /home/werserk/.npm-global/lib/node_modules/hermes-web-ui
node -e "console.log(require('/home/werserk/.npm-global/lib/node_modules/hermes-web-ui/package.json').version)"
```

The global npm package is not authoritative unless systemd `ExecStart` or `WorkingDirectory` points there.

## After restart

```bash
systemctl --user restart hermes-web-ui.service
systemctl --user is-active hermes-web-ui.service
ss -ltnp | grep ':8648'
curl -fsS http://127.0.0.1:8648/health
```

If `/health` fails immediately after restart but systemd is active, check listener state and retry once in a fresh command before declaring failure; binding can lag briefly.

## Report evidence

For runtime claims, report only the evidence that matters:

- active/inactive service state;
- actual `ExecStart`/`WorkingDirectory`;
- listener and health status;
- source commit or active package version;
- relevant fresh log error if present.
