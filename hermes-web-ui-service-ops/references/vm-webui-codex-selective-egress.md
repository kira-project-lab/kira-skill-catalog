# VM Web UI Codex selective egress

Use this when a Hermes Web UI service on a cloud VM fails on `openai-codex` with an HTML OpenAI/Cloudflare page such as `Unable to load site`, HTTP 403, or a page showing the VM public IP.

## Root-cause pattern

The host may already have a selective SOCKS/VPN path for Codex CLI, but Web UI chat runs through the Hermes bridge process inside the Web UI systemd unit. If that unit does not inherit proxy env vars, the bridge calls `https://chatgpt.com/backend-api/codex` directly from the VM public IP and can be blocked by Cloudflare/OpenAI.

Evidence to collect:

```bash
systemctl --user show hermes-web-ui-preview.service -p Environment --no-pager
journalctl --user -u hermes-web-ui-preview.service --since '30 min ago' --no-pager | tail -120
tail -120 /data/kira/profiles/kira/logs/errors.log
```

Look for:

- provider `openai-codex`
- base URL `https://chatgpt.com/backend-api/codex`
- `PermissionDeniedError` / HTTP 403
- HTML page with `Unable to load site`
- public VM IP in the error body

## Probe direct vs proxied

Run from the same profile and Hermes binary. Direct should reproduce the block; proxied should pass:

```bash
HERMES_HOME=/data/kira/profiles/kira \
HOME=/data/kira/profiles/kira/home \
/opt/kira/services/hermes-agent/.venv/bin/hermes chat \
  -q 'Print exactly: direct-probe-ok' --source probe --quiet

HERMES_HOME=/data/kira/profiles/kira \
HOME=/data/kira/profiles/kira/home \
HTTPS_PROXY=socks5h://127.0.0.1:18080 \
ALL_PROXY=socks5h://127.0.0.1:18080 \
HERMES_CODEX_TTFB_TIMEOUT_SECONDS=60 \
/opt/kira/services/hermes-agent/.venv/bin/hermes chat \
  -q 'Print exactly: proxy-probe-ok' --source probe --quiet
```

If proxied Codex times out with `Codex stream produced no bytes within 12s`, increase `HERMES_CODEX_TTFB_TIMEOUT_SECONDS` to `60` before changing provider/model. The selective egress can have slower first-token latency. If logs say the timeout is capped to 20s, also set `HERMES_CODEX_TTFB_MAX_SECONDS=90` or higher. If Codex still produces no bytes across normal Web UI sends, switch the VM profile default to a direct provider such as OpenRouter and add `openrouter.ai,.openrouter.ai` to `NO_PROXY`; otherwise the service-level SOCKS proxy can break OpenRouter with connection errors.

## Runtime fix

Use a systemd drop-in for the Web UI service, not a full-tunnel VPN:

```ini
[Service]
Environment=HTTPS_PROXY=socks5h://127.0.0.1:18080
Environment=ALL_PROXY=socks5h://127.0.0.1:18080
Environment=NO_PROXY=127.0.0.1,localhost,::1,openrouter.ai,.openrouter.ai
Environment=HERMES_CODEX_TTFB_TIMEOUT_SECONDS=60
Environment=HERMES_CODEX_TTFB_MAX_SECONDS=90
```

For the VM preview contour where Telegram cutover is intentionally deferred, also prevent the Web UI from starting profile gateways under this proxy environment:

```ini
Environment=HERMES_WEB_UI_DISABLE_GATEWAY_AUTOSTART=1
```

Apply:

```bash
systemctl --user daemon-reload
systemctl --user restart hermes-web-ui-preview.service
systemctl --user show hermes-web-ui-preview.service -p Environment --no-pager
```

## Bridge-level verification

A Web UI health check only proves the server is up. Verify the bridge path, because the failure happens inside the agent run:

```bash
python3 - <<'PY'
import json, socket
req = {
  'action': 'chat',
  'profile': 'kira',
  'session_id': 'vm-webui-egress-smoke',
  'message': 'Print exactly: webui-bridge-proxy-ok',
  'source': 'probe',
  'wait': True,
  'timeout': 150,
}
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.settimeout(180)
s.connect('/tmp/hermes-agent-bridge-yc-preview.sock')
s.sendall((json.dumps(req) + '\n').encode())
b = b''
while not b.endswith(b'\n'):
    chunk = s.recv(65536)
    if not chunk:
        break
    b += chunk
print(b.decode(errors='replace')[:4000])
PY
```

Expected output contains `webui-bridge-proxy-ok`.

## Reproducibility rule

For Kira VM ops, record the drop-in and evidence in `kira-project-lab/kira-ops`; do not leave runtime-only systemd changes on the VM. If the VM cannot `git fetch` because GitHub auth is unavailable, sync from the local clean ops checkout and deploy the runtime ops tree, then fix repo access separately.
