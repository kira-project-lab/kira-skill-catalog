# Telegram polling conflict: duplicate getUpdates poller

Use when Kira/Hermes is “not working through Telegram” and logs repeat:

```text
Conflict: terminated by other getUpdates request; make sure that only one bot instance is running
Telegram polling conflict (...)
```

## Meaning

Telegram Bot API allows only one active `getUpdates` long-poll consumer per bot token. A healthy gateway can be `active` and still receive no messages if another process/service is polling the same bot.

## Fast evidence sequence

1. Confirm the active gateway and fresh conflict logs:

```bash
systemctl --user status hermes-gateway-kira.service --no-pager -l
journalctl --user -u hermes-gateway-kira.service --since '30 minutes ago' --no-pager -o short-iso | grep -Ei 'telegram|conflict|getUpdates|polling'
```

2. List all gateway-like processes across users; do not assume only the current user has pollers:

```bash
ps -eo user,pid,ppid,lstart,etime,stat,cmd | grep -E 'hermes gateway|gateway run|gateway/run.py|telegram' | grep -v grep
```

3. If current Kira gateway is user-managed, stop it and wait for Telegram’s server-side long-poll to expire before probing:

```bash
systemctl --user stop hermes-gateway-kira.service
sleep 35
```

4. Probe Bot API once without printing the token:

```bash
python3 - <<'PY'
import pathlib, re, requests
p = pathlib.Path('/home/werserk/.hermes/profiles/kira/.env')
token = re.search(r'^TELEGRAM_BOT_TOKEN=(.+)$', p.read_text(), re.M).group(1).strip().strip('"\'')
r = requests.post(f'https://api.telegram.org/bot{token}/getUpdates', json={'timeout': 1, 'limit': 1, 'allowed_updates': []}, timeout=10)
body = r.json() if r.headers.get('content-type','').startswith('application/json') else {}
print({'status_code': r.status_code, 'ok': body.get('ok'), 'error_code': body.get('error_code'), 'description': body.get('description')})
PY
```

Interpretation:
- `ok: true` while Kira gateway is stopped means the current Kira gateway was one poller, but it does not rule out a second poller starting later.
- `409 Conflict` while Kira gateway is stopped proves another poller exists.

5. If needed, run a minimal PTB poller for 20–30 seconds after Kira gateway is stopped. If it receives `Conflict`, the duplicate poller is external to the Kira service.

## Common root cause on Maxim’s host

A different Web UI/system service may auto-start its own `hermes gateway run --replace` children under another Linux user. Check cgroups for suspicious gateway PIDs:

```bash
for p in <pid1> <pid2>; do echo "## $p"; cat /proc/$p/cgroup 2>&1 || true; done
systemctl status <owning-system-service>.service --no-pager -l
```

Example pattern:

```text
/system.slice/hermes-web-ui-polina.service
... hermes gateway run --replace
... hermes gateway run --replace
```

## Fix

Stop or reconfigure the duplicate poller, then restart Kira’s gateway:

```bash
sudo systemctl stop <duplicate-service>.service
systemctl --user restart hermes-gateway-kira.service
```

If the duplicate service is needed, remove/replace its Telegram bot token or disable its gateway autostart instead of leaving two services with the same token.

## Verification

```bash
systemctl --user is-active hermes-gateway-kira.service
journalctl --user -u hermes-gateway-kira.service --since '2 minutes ago' --no-pager -o short-iso | grep -Ei 'telegram|conflict|connected|error'
```

Pass criteria: `Connected to Telegram (polling mode)` and no fresh `Telegram polling conflict` after the duplicate service is stopped and the long-poll expiry window has passed.

## Pitfalls

- Restarting Kira alone may not fix it; it can briefly connect and then conflict again.
- `systemctl --user` only sees the current user’s services. Duplicate pollers can live in root/system units or another user’s Web UI service.
- Do not print Telegram bot tokens. Hashes or redacted status fields are enough.
- A visible Telegram Desktop connection is not a Bot API poller; focus on `hermes gateway run`, bot/webhook services, and Bot API clients.