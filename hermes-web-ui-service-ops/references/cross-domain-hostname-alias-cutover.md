# Cross-domain hostname alias cutover for Hermes Web UI

Use this note when adding a second public hostname to the same live Hermes Web UI runtime, especially when the new hostname is under a different DNS zone/provider profile than the existing `hermes.ops.kiraproject.ru` host.

## Pattern from `chat.werserk.com`

Observed target state:

- Existing Web UI host: `hermes.ops.kiraproject.ru`
- New alias host: `chat.werserk.com`
- Both point to the same home ingress IP: `95.165.95.45`
- Caddy runs in Docker as `caddy-hermes`
- Mounted Caddyfile: `/home/werserk/2-kira/local-secrets/hermes-home-access/Caddyfile.hermes.kiraproject.ru`
- Upstream Web UI: `127.0.0.1:8648`

## Safe sequence

1. Verify the live upstream and existing hostname first:
   - `systemctl --user is-active hermes-web-ui.service`
   - `curl -fsS http://127.0.0.1:8648/health`
   - `curl -Ik https://hermes.ops.kiraproject.ru/`
2. Identify the authoritative DNS provider for the new domain:
   - `dig +short <domain> NS @1.1.1.1`
   - For `werserk.com`, the authoritative NS are Yandex Cloud, not reg.ru.
3. Use the matching `yc` profile for the zone. Do not assume the default profile owns every YC DNS zone:
   - `yc --profile yc-werserk dns zone list --format json`
   - `yc --profile yc-werserk dns zone list-records werserk-com --format json`
4. Add the new A record only if it does not already exist:
   - `yc --profile yc-werserk dns zone add-records werserk-com --record 'chat.werserk.com. 300 A 95.165.95.45'`
5. Add the new hostname to the existing Caddy site label when it should share the same upstream and behavior:
   - `hermes.ops.kiraproject.ru, chat.werserk.com { ... }`
6. Validate Caddy before reload:
   - `docker run --rm -v /path/to/Caddyfile:/etc/caddy/Caddyfile:ro caddy:<same-version> caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile`
7. Reload the live container without restarting the Web UI:
   - `docker exec caddy-hermes caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile`
8. Verify certificate issuance and HTTPS:
   - `docker logs --since 5m caddy-hermes | grep <new-host>`
   - `curl -Ik --resolve <new-host>:443:<ingress-ip> https://<new-host>/`
   - `echo | openssl s_client -servername <new-host> -connect <ingress-ip>:443 2>/dev/null | openssl x509 -noout -subject -issuer -dates -ext subjectAltName`
   - `curl -Ik https://<new-host>/`

## Pitfalls

- Local resolver negative cache can make `curl https://<new-host>/` still fail with `Could not resolve host` after authoritative/public DNS already answers. Flush caches and retry rather than changing DNS again:
  - `resolvectl flush-caches`
  - `getent hosts <new-host>`
- If public DNS is correct and `--resolve` HTTPS works, the remaining failure is usually local resolver cache or propagation, not Caddy/TLS.
- When the new hostname is in another sphere/domain, check whether the IaC repo and live DNS recordset can drift. If there is an OpenTofu source-of-truth for the zone, follow up by adding the record there too instead of leaving an unmanaged live-only record.
