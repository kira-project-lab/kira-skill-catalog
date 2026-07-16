# Hermes Web UI prod/dev bridge endpoint isolation

Use when running more than one Hermes Web UI instance on the same host, especially `hermes-web-ui.service` and `hermes-web-ui-dev.service`.

## Root cause pattern

If two Web UI instances both use the default agent bridge endpoint:

```text
ipc:///tmp/hermes-agent-bridge.sock
```

the later-started bridge unlinks and re-binds the same Unix socket path. Existing runs from the first instance may then be polled through the second instance's broker, whose in-memory run registry does not contain that run id.

Typical symptom in the first instance:

```text
Error: 'unknown run: <run_id>'
```

The run was not necessarily lost in the chat DB; the polling request was routed to the wrong bridge broker.

## Evidence to collect

```bash
systemctl --user show hermes-web-ui.service hermes-web-ui-dev.service \
  -p Id -p ActiveState -p MainPID -p ExecStart -p WorkingDirectory -p Environment --no-pager

ss -ltnp | grep -E ':(8648|8649)\b' || true

stat -Lc 'path=%n inode=%i mode=%A mtime=%y' /tmp/hermes-agent-bridge*.sock 2>/dev/null || true

journalctl --user -u hermes-web-ui.service --since '10 min ago' --no-pager | grep -E 'unknown run|agent-bridge|CLI bridge run started' || true
journalctl --user -u hermes-web-ui-dev.service --since '10 min ago' --no-pager | grep -E 'unknown run|agent-bridge|CLI bridge run started' || true
```

Also inspect the Web UI bridge logs:

```bash
grep -nE 'unknown run|run_id|ready at ipc:///tmp/hermes-agent-bridge' ~/.hermes-web-ui/logs/bridge.log ~/.hermes-web-ui-dev/logs/bridge.log 2>/dev/null
```

## Required topology

Each live instance must have a unique broker endpoint. Example:

Prod unit:

```ini
Environment=HERMES_AGENT_BRIDGE_ENDPOINT=ipc:///tmp/hermes-agent-bridge-prod.sock
```

Dev unit:

```ini
Environment=HERMES_AGENT_BRIDGE_ENDPOINT=ipc:///tmp/hermes-agent-bridge-dev.sock
```

This also separates worker socket namespaces because worker endpoints are derived from the broker endpoint namespace plus worker key.

## Remediation order

1. Add distinct `HERMES_AGENT_BRIDGE_ENDPOINT` values to every concurrently running Web UI systemd unit.
2. Run `systemctl --user daemon-reload`.
3. Restart both services during an acceptable interruption window; live runs may be interrupted.
4. Verify both bridges started with different `--endpoint` args.
5. Verify both health endpoints:
   - prod: `curl -fsS http://127.0.0.1:8648/health`
   - dev: `curl -fsS http://127.0.0.1:8649/health`

## Regression test after isolation

After applying distinct endpoints, deliberately restart only the dev service and verify prod is unaffected:

```bash
systemctl --user restart hermes-web-ui-dev.service
systemctl --user is-active hermes-web-ui.service hermes-web-ui-dev.service
curl -fsS http://127.0.0.1:8648/health
curl -fsS http://127.0.0.1:8649/health
ps -eo pid,ppid,cmd | grep -E 'hermes_bridge.py --endpoint ipc:///tmp/hermes-agent-bridge-(prod|dev)\.sock|dist/server/index.js' | grep -v grep
```

`systemctl is-active` can turn `active` before the dev HTTP listener is ready; if dev health fails immediately after restart, wait briefly and retry. Prod health should remain OK throughout.

## Pitfall

Enabling dev autostart (`systemctl --user enable hermes-web-ui-dev.service`) before isolating bridge endpoints can break active prod chat runs even if prod itself is not restarted.