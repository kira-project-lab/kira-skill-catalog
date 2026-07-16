# Hermes Web UI two-folder prod/dev deploy policy

Use this when checking whether a public Hermes Web UI hostname should show prod or dev.

## Mapping

| Host | Service | Port | Code folder | State folder | Git policy |
|---|---|---:|---|---|---|
| `hermes.ops.kiraproject.ru` | `hermes-web-ui.service` | `8648` | `/home/werserk/2-kira/hermes-web-ui` | `/home/werserk/.hermes-web-ui` | `origin/main` only |
| `hermes.dev.ops.kiraproject.ru` | `hermes-web-ui-dev.service` | `8649` | `/home/werserk/2-kira/hermes-web-ui-dev` | `/home/werserk/.hermes-web-ui-dev` | arbitrary pushed branch |

## Practical rule

- Prod updates go through the canonical repo at `/home/werserk/2-kira/hermes-web-ui` and `origin/main`.
- Dev preview is separate and must be deployed to `/home/werserk/2-kira/hermes-web-ui-dev` via `hermes-web-ui-dev.service`.
- A healthy prod deploy does not imply the dev hostname is live.
- If `hermes.dev.ops.kiraproject.ru` returns 502, check `hermes-web-ui-dev.service`, the dev repo checkout, and the dev port/listener first.

## Verification sequence

```bash
systemctl --user list-units 'hermes-web-ui*' --no-pager --all
systemctl --user show hermes-web-ui-dev.service -p WorkingDirectory -p ExecStart -p Environment --no-pager
ss -ltnp | grep -E ':(8648|8649)\b' || true
curl -fsS http://127.0.0.1:8648/health
curl -fsS http://127.0.0.1:8649/health
```

## Deployment commands

- Prod: `bash /home/werserk/2-kira/hermes-web-ui/scripts/deploy-prod.sh`
- Dev branch preview: `bash /home/werserk/2-kira/hermes-web-ui-dev/scripts/deploy-dev-branch.sh <branch>`
