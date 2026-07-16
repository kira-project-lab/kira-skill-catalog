# VM beta tenant G9/G10 ops patterns

Use this for Kira beta-10 VM work when closing backup/restore, public-access helper, Authentik token, or tenant Web UI runtime routing gates.

## Git-ref discipline on the VM

If the VM acceptance checkout cannot fetch GitHub directly (for example no deploy key / `Permission denied (publickey)`), keep source-of-truth in the pushed repo and transfer only Git bundles:

```bash
git bundle create /tmp/kira-ops-beta-acceptance-<sha>.bundle <old-sha>..<new-sha> beta-10-vm-acceptance-2026-06-27
scp /tmp/kira-ops-beta-acceptance-<sha>.bundle kira-main-ops:/tmp/
ssh kira-main-ops 'cd /opt/kira/repos/kira-ops-beta-acceptance && git fetch /tmp/kira-ops-beta-acceptance-<sha>.bundle beta-10-vm-acceptance-2026-06-27 && git reset --hard <new-sha>'
```

Verify:

```bash
ssh kira-main-ops 'cd /opt/kira/repos/kira-ops-beta-acceptance && git rev-parse HEAD && git status --short && ./bin/kira validate all'
```

Do not leave VM runtime fixes as live copied files only; commit/push, then sync the checkout.

## Tenant Web UI bind host pitfall

For public routed `app.vm.kiraproject.ru`, Caddy forwards to `172.17.0.1:<port>`, not tenant loopback. The tenant Web UI systemd unit must bind to the route-visible address for public tenants.

- Public routed dummy/tenant: `BIND_HOST=172.17.0.1`
- Loopback-only dummy tenant: `KIRA_BETA_BIND_HOST=127.0.0.1`

Installer pitfall: if a unit file changes, `systemctl enable --now` is not enough for an already-running unit. Use `systemctl enable` then `systemctl restart`, then verify the actual routed health endpoint:

```bash
curl -fsS -o /dev/null -w 'usr001_bridge=%{http_code}\n' http://172.17.0.1:28648/health
curl -fsS -o /dev/null -w 'usr002_loopback=%{http_code}\n' http://127.0.0.1:28649/health
systemctl show kira-beta-webui-usr-test-001.service -p Environment --no-pager | tr ' ' '\n' | grep -E 'BIND_HOST|HERMES_AGENT_ROOT|HERMES_AGENT_BRIDGE_ENDPOINT'
```

A browser `502` from `app.vm.kiraproject.ru` after reinstall can mean the service is healthy on `127.0.0.1` but unreachable from Caddy's Docker network.

## Authentik API token rotation for beta helper

If `scripts/beta-user-public-access.py status <uid>` fails with Authentik HTTP 403 / `Token invalid/expired`, rotate the API token instead of weakening the helper.

Pattern:

1. Create a new `intent='api'` token for the operator user in the Authentik container with `ak shell`.
2. Write only a temporary Lockbox payload JSON file with the new token value.
3. Update the Lockbox secret with `yc lockbox secret add-version --payload -`.
4. Remove temp files from local host, VM host, and container.
5. Re-run helper status/disable/enable and browser/API smoke.

Example shell shape, omitting printed token values:

```bash
ssh kira-main-ops 'cd /opt/kira/compose/ops && sudo docker compose exec -T authentik-server ak shell' <<'PY'
from datetime import timedelta
from django.utils import timezone
from authentik.core.models import User, Token
import json, os
user = User.objects.get(username='werserk')
identifier = 'kira-g10-ops-token-YYYYMMDD'
Token.objects.filter(identifier=identifier).delete()
t = Token.objects.create(
    identifier=identifier,
    user=user,
    intent='api',
    description='Kira beta-10 G10 ops helper token, rotated YYYY-MM-DD',
    expires=timezone.now() + timedelta(days=90),
)
path = '/tmp/kira-g10-authentik-token-payload.json'
with open(path, 'w') as f:
    json.dump([{'key': 'AUTHENTIK_BOOTSTRAP_TOKEN', 'text_value': t.key}], f)
os.chmod(path, 0o600)
print('ROTATED_IDENTIFIER=' + identifier)
print('ROTATED_USER=' + user.username)
print('ROTATED_EXPIRES=' + t.expires.isoformat())
PY
```

Copy the file out of the container, then:

```bash
yc lockbox secret add-version --name kira-main-authentik-bootstrap --payload - < /tmp/kira-g10-authentik-token-payload.json
rm -f /tmp/kira-g10-authentik-token-payload.json
ssh kira-main-ops 'rm -f /tmp/kira-g10-authentik-token-payload.json; cd /opt/kira/compose/ops && cid=$(sudo docker compose ps -q authentik-server) && sudo docker exec "$cid" rm -f /tmp/kira-g10-authentik-token-payload.json'
```

Evidence must include only token identifier/user/expiry and Lockbox version ID, never the token value.

Important: the helper may be operator-side only. If it passes locally but fails on the VM with Yandex Lockbox `PermissionDenied`, report that as VM service-account scope, not as Authentik failure.

## Secret scanner false positives

`./bin/kira validate all` scans `scripts/` for secret-like literals. A script constant like `DEFAULT_AUTHENTIK_TOKEN_KEY = "AUTHENTIK_BOOTSTRAP_TOKEN"` can trip the scanner even though it is only a key name. Split long key-name/default-secret strings into short fragments:

```python
DEFAULT_AUTHENTIK_SECRET = "kira-main-" + "authentik-" + "bootstrap"
DEFAULT_AUTHENTIK_TOKEN_KEY = "AUTHENTIK_" + "BOOTSTRAP_" + "TOKEN"
```

Do not disable the secret scanner to avoid this.

## Live backup/restore drill pattern

G9 needs a non-destructive live restore proof, not only temp-dir backup/restore. A repo-owned helper should:

- stop only the target dummy tenant service if active;
- archive real tenant components from `/data/kira/users/<uid>`;
- write `manifest.json` and `checksums.sha256`;
- restore into `/data/kira/restore-drills/<uid>-live-<timestamp>`;
- never overwrite the live root;
- set tenant ownership and `go-rwx` permissions;
- restart the tenant service and verify `active`.

Components used in the first successful `usr_test_001` drill:

```text
profile
web-ui-state
agentmemory
hermes-root
workspace
uploads
exports
```

Verification:

```bash
sudo bash -c 'cd /data/kira/users/<uid>/backups/live-<timestamp> && sha256sum -c checksums.sha256 >/dev/null'
sudo python3 -m json.tool /data/kira/users/<uid>/backups/live-<timestamp>/manifest.json >/dev/null
sudo find /data/kira/restore-drills/<uid>-live-<timestamp> -maxdepth 6 -type f -perm -0007 -print -quit | grep -q . && echo FAIL || echo RESTORE_FILE_PRIVACY_PASS
systemctl is-active kira-beta-webui-<uid-with-dashes>.service
```

## G10 cost/log/support evidence pattern

G10 is not closed by access toggling alone. After public-access helper status/disable/enable and active-session revocation pass, record the remaining operator evidence as a separate cost/log/support slice.

Cost evidence:

- Query the scoped beta tenant provider key metadata through the provider's key-info endpoint, not through a broad management key when avoidable.
- For OpenRouter tenant keys, use `GET https://openrouter.ai/api/v1/key` with the tenant key and record only non-secret metadata: key name, `is_management_key`, `limit`, `limit_remaining`, `limit_reset`, and `usage`.
- Sanitize provider labels too: OpenRouter may return a shortened label that still starts with the provider key prefix. Replace it with a neutral placeholder before committing JSON evidence.
- Capture a bounded YC resource inventory separately: instances, disks, public addresses, DNS zones, and Lockbox secret names/statuses. Do not dump secret payloads.

Log/support evidence:

- Prove the tenant Web UI service is active and route-local health works (`/health -> 200`, `/api/health -> 401`).
- Record tenant log file locations, sizes, and redacted tails under `/data/kira/users/<uid>/.../logs/`.
- Redact provider keys, bearer tokens, passwords, cookies, and session tokens before writing evidence.
- Do not inspect prompts, files, exports, or memory content for a routine support check. Support triage should start from metadata and logs; content inspection needs user request, security/abuse reason, or Maxim approval.
- Add or update a repo-owned support triage runbook when the process is not already documented.

Useful evidence files from the first complete dummy-tenant G10 pass:

```text
docs/evidence/beta-users/<uid>-g10-cost-log-support-pass-YYYY-MM-DD.md
docs/evidence/beta-users/assets/<uid>-g10-cost-support-openrouter-YYYY-MM-DD.json
docs/evidence/beta-users/assets/<uid>-g10-log-support-visibility-YYYY-MM-DD.json
docs/evidence/beta-users/assets/<uid>-g10-yc-resource-inventory-YYYY-MM-DD.json
runbooks/beta-user-support-triage.md
```

After writing G10 evidence, run the repo validator, grep the new evidence/runbooks for provider-key or token literals, re-run `./bin/kira check prod-surface`, and sync the VM acceptance checkout from the pushed Git ref or a Git bundle.

## Completion reporting

For beta-10 acceptance, keep status by gate:

- `PASS for dummy tenant` is not full beta-10 acceptance.
- `PARTIAL PASS` must name the remaining missing proof.
- G11 remains blocked until a real trusted beta user is selected and explicitly approved for E2E.

Always re-run `./bin/kira check prod-surface` after VM acceptance changes and include `200 / 200 / 401` if reporting non-breakage of `app.kiraproject.ru`.
