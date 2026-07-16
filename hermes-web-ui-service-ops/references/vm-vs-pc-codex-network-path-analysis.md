# VM vs PC Codex network-path analysis

Use after a bridge-level benchmark shows the YC VM `openai-codex` path is much slower than the home PC. The goal is to compare the **effective egress path**, not to change provider/model.

## Key lesson from 2026-06-19

A provider override such as OpenRouter can prove that VM/Web UI overhead is not the bottleneck, but Maxim may explicitly reject provider switching as a workaround. In that case, keep `openai-codex` fixed and analyze network paths.

Observed root-cause pattern:

- Home PC also uses VPN, but via **Hiddify TUN + policy routing**:
  - Web UI service has no `HTTPS_PROXY` / `ALL_PROXY`.
  - `HiddifyCli tunnel run` is active.
  - `ip rule` points traffic to table `2022`.
  - `ip route show table 2022` shows default via `tun3`.
  - `api.openai.com/v1/models` returns `401` in about `0.6s`.
- YC VM uses a different path: **app-level Xray SOCKS**:
  - Web UI service has `HTTPS_PROXY=socks5h://127.0.0.1:18080` and `ALL_PROXY=socks5h://127.0.0.1:18080`.
  - `codex-xray-proxy.service` runs `/usr/local/bin/xray ...` and listens on `127.0.0.1:18080`.
  - VM default route remains direct cloud egress.
  - Direct cloud egress to OpenAI is fast but blocked (`403` in ~50ms).
  - SOCKS egress can alternate between quick responses and full 20–60s TLS/TTFB timeouts.

When these conditions hold, the likely bottleneck is the VM SOCKS/Xray outbound path, not Hermes Web UI bridge overhead and not model generation speed.

## Probe checklist

Run on both PC and VM, without changing runtime config:

```bash
systemctl --user show <webui-service> \
  -p ActiveState -p MainPID -p WorkingDirectory -p ExecStart -p Environment --no-pager

ss -ltnp | grep -E ':(8648|18648|18080|1080|7890|2080)\\b' || true
ps -eo pid,etime,comm,args | grep -Ei 'hiddify|sing-box|xray|mihomo|clash|v2ray|hermes-web-ui|bridge' | grep -v grep

ip -br addr
ip route
ip rule show
ip route show table 2022 2>/dev/null || true

for u in https://api.ipify.org https://ifconfig.me/ip https://icanhazip.com; do
  printf '%s ' "$u"; curl -4 -fsS --max-time 12 "$u" || true; echo
done

for u in https://api.openai.com/v1/models https://chatgpt.com/backend-api/codex; do
  echo "URL=$u"
  for i in 1 2 3 4 5; do
    curl -4 -sS -o /tmp/curl-body \
      -w 'http=%{http_code} dns=%{time_namelookup} connect=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer} total=%{time_total} err=%{errormsg}\\n' \
      --max-time 20 "$u" || true
    head -c 120 /tmp/curl-body | tr '\n' ' '; echo
  done
done
```

If the VM service uses SOCKS, repeat target probes through the proxy:

```bash
for u in https://api.openai.com/v1/models https://chatgpt.com/backend-api/codex; do
  echo "URL=$u via SOCKS"
  for i in 1 2 3 4 5; do
    curl -4 -sS --socks5-hostname 127.0.0.1:18080 -o /tmp/curl-body \
      -w 'http=%{http_code} connect=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer} total=%{time_total} err=%{errormsg}\\n' \
      --max-time 20 "$u" || true
    head -c 120 /tmp/curl-body | tr '\n' ' '; echo
  done
done

journalctl --user --since '20 min ago' --no-pager \
  | grep -Ei 'xray|sing-box|hiddify|timeout|connect|openai|chatgpt|error|warn' \
  | tail -160
```

## Interpretation

- `api.openai.com/v1/models` returns `401`: network path reached OpenAI; auth is the expected blocker for unauthenticated curl.
- Direct VM returns fast `403`: the cloud IP path is blocked but not slow.
- Proxy path has mixed fast responses and full timeout windows: the proxy outbound is unstable; expect Codex bridge runs to stack these stalls.
- PC has Hiddify TUN/table `2022` and no local SOCKS: do not claim “both use VPN, so VPN is equal.” They are different egress mechanisms.

## Reporting

Keep conclusion root-cause oriented:

```md
Status: analysed, no config changes.
Суть: ПК and VM both involve VPN, but not the same path. PC uses Hiddify TUN; VM uses Xray SOCKS. VM SOCKS alternates fast responses with full TLS/TTFB timeouts, matching bridge latency.
Следующий шаг: compare/replace the VM egress path while keeping provider/model fixed.
```
