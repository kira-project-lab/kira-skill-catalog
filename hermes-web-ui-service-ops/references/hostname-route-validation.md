# Hostname / route validation notes

Session-derived deployment lesson for Hermes Web UI routing.

## Canonical current home routes

Observed home Caddy routing in the Kira workspace currently uses:

- `hermes.ops.kiraproject.ru` -> `127.0.0.1:8648`
- `hermes.dev.ops.kiraproject.ru` -> `127.0.0.1:8649`

## Pitfall

Do not infer a hostname by rearranging subdomains. `ops.dev` and `dev.ops` are different names and may not exist in DNS or in the current route map.

Before deploying to a requested host:

1. Verify the exact FQDN the user asked for.
2. Check the authoritative route map / generated Caddyfile / inventory for that exact hostname.
3. If the requested hostname is not present, stop and ask for confirmation rather than guessing an adjacent name.

## Verification cues

- If `curl` reports `Could not resolve host`, that is often a missing DNS/route record, not an app failure.
- If a host exists in local config but not in DNS, the deployment target is not ready even if the app process is healthy.
- For Kira home deployments, treat `hermes.ops.kiraproject.ru` and `hermes.dev.ops.kiraproject.ru` as the known canonical pair unless the inventory is explicitly updated.
