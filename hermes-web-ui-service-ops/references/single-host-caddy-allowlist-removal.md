# Removing an IP allowlist from a single Caddy-hosted dev surface

Use when Maxim asks whether a browser-facing dev surface is restricted by an IP allowlist and wants only that barrier removed.

## Discovery

- Identify the actual proxy first. On the Kira host, public `hermes.dev.ops.kiraproject.ru` can be served by a Docker Caddy container (`caddy-hermes`) with a bind-mounted Caddyfile, not host/systemd Caddy.
- Inspect mounts with `docker inspect caddy-hermes` and read the mounted source Caddyfile, not a guessed `/etc/caddy/Caddyfile` path.
- In Caddyfile syntax, a reusable snippet such as `(kira_allowlist)` plus `import kira_allowlist`, `handle @allowed`, and `respond "Forbidden" 403` means the host is allowlisted.

## Narrow change pattern

- Remove the allowlist only from the requested hostname block.
- Leave the shared `(kira_allowlist)` snippet and other sensitive host blocks intact.
- Convert the host block to a direct `reverse_proxy` block for the intended upstream.
- Do not alter DNS/router/firewall/prod domains unless explicitly requested.

Example shape:

```caddyfile
hermes.dev.ops.kiraproject.ru {
    reverse_proxy 127.0.0.1:8649 {
        header_up Host {host}
        header_up X-Real-IP {remote_host}
    }
}
```

## Verification

- `docker exec caddy-hermes caddy validate --config /etc/caddy/Caddyfile`
- `docker exec caddy-hermes caddy reload --config /etc/caddy/Caddyfile`
- If the host file was edited with a tool that replaces the file inode, a Docker **single-file bind mount** may keep exposing the old inode inside the container. Compare host/container `stat` or checksums; if they differ, restart `caddy-hermes` so the bind mount is re-opened before trusting `validate`, `reload`, or HTTP results.
- Public health/header check returns the intended status: `200` for direct app auth, or `302` to Authentik when replacing the allowlist with SSO.
- Adapted config for the target host has no `remote_ip` matcher. A robust check is to adapt to JSON and inspect only the route whose host is the target hostname.
- Report the security posture explicitly: removing proxy allowlist makes the surface public at the reverse-proxy layer; remaining protection must be the app's auth/session layer or Authentik forward-auth.