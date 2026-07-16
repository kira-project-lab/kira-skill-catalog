# Live hostname cutover for Hermes/Codex edge

Use this when a Hermes-family service must move to new public hostnames and the change must be applied live, not only in repo configs.

## Pattern from the June 2026 cutover

- Old names were replaced with new canonical names:
  - `hermes.kiraproject.ru` → `hermes.ops.kiraproject.ru`
  - `hermes.dev.kiraproject.ru` → `hermes.dev.ops.kiraproject.ru`
  - `codex.int.werserk.com` → `codex.ops.werserk.com`
- The same home public IP continued to serve the services.
- DNS was changed in live authoritative zone data, then verified against the authoritative resolver.
- The home reverse proxy (`caddy-hermes`) was restarted after the Caddyfile change so the new hostnames were actually served.
- Success required verifying both:
  - authoritative DNS resolution
  - HTTPS reachability on the new hostnames

## Recommended sequence

1. Update the source-of-truth inventory and generated configs first.
2. Apply live DNS to the authoritative zone, not just generated files.
3. Verify with an authoritative resolver, not only local `dig` or cached system resolver.
4. Update the live reverse proxy/Caddy config to include the new hostnames.
5. Restart or reload the proxy container/service.
6. Confirm ACME/TLS issuance completed for the new names.
7. Verify the public URLs with HTTPS and the relevant health endpoint.

## Verification cues

- `dig +short <name> A @ns1.yandexcloud.net` should return the live edge IP.
- `curl -fsSI https://<name>/` should return a successful HTTPS response.
- Proxy logs should show certificate issuance or renewal for the new names.

## Pitfalls

- A working local config file does not mean live DNS changed.
- Resolver caches can briefly show stale answers; authoritative queries are the ground truth.
- If the proxy file is mounted by exact filename, keep any compatibility copy needed for the runtime mount while renaming the canonical file in the repo.
- Do not treat a `200` on the old hostname as success once the cutover target has changed; verify the new canonical hostname specifically.
