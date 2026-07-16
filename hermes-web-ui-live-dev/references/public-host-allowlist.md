# Hermes Web UI live-dev public host allowlist

Use this when `https://hermes.dev.ops.kiraproject.ru/` opens a blank black page with a message like:

- `Blocked request.`
- `<host> is not allowed`
- Vite suggests adding the host to `server.allowedHosts`

## What this means

This is usually the Vite dev server rejecting the public hostname, not an application bug.

## Fix pattern

1. Add the public dev hostname to `server.allowedHosts` in `vite.config.ts` for the live-dev checkout.
2. Keep the list narrow; include only the dev hostname(s) you intend to serve publicly.
3. Restart the live-dev service.
4. Reopen the public URL and confirm the app shell renders.

## Verification

```bash
curl -fsS http://127.0.0.1:8649/health
ss -ltnp | grep -E ':(8647|8649)\b'
```

The health payload should show `runtime: live-dev` and the expected frontend/backend ports.
