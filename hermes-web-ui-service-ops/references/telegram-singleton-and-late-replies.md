# Telegram singleton and late-reply diagnostics

Use when Maxim asks whether Kira is connected to only one Telegram Hermes Agent, whether duplicate processes are answering, or why Kira appears to answer old messages.

## What to prove

Separate three cases:

1. **Duplicate Telegram poller** — two processes consume the same bot `getUpdates`; Telegram usually logs `Conflict: terminated by other getUpdates request`.
2. **Single gateway with late work** — one gateway is active, but a tool/background process or long agent turn finishes later and delivers output that looks like an answer to an old message.
3. **Reconnect catch-up** — Telegram polling/network errors delay delivery; the gateway catches up after reconnect.

Do not infer duplication from a late reply alone.

## Process proof

Count only real gateway argv, not the current diagnostic shell command that happens to contain the same text:

```bash
python3 - <<'PY'
import os
matches=[]
for pid in filter(str.isdigit, os.listdir('/proc')):
    try:
        args=[x.decode('utf-8','ignore') for x in open(f'/proc/{pid}/cmdline','rb').read().split(b'\0')[:-1]]
        if len(args) >= 5 and args[1:5] == ['-m','hermes_cli.main','--profile','kira'] and 'gateway' in args and 'run' in args:
            matches.append((pid,args))
    except Exception:
        pass
print('gateway_run_count', len(matches))
for pid,args in matches:
    print(pid, ' '.join(args))
PY
```

Then check systemd's view:

```bash
systemctl --user show hermes-gateway-kira.service \
  -p MainPID -p ActiveState -p SubState -p NRestarts -p ExecStart --no-pager
```

A single `gateway_run_count 1` plus a matching `MainPID` is evidence for one active gateway.

## Telegram duplicate-poller evidence

Look for Bot API polling conflicts in the gateway journal:

```bash
journalctl --user -u hermes-gateway-kira.service --since '24 hours ago' --no-pager \
  | grep -Eic 'Conflict|terminated by other|getUpdates request'
```

Interpretation:

- `0` conflicts: no direct evidence of a second Telegram poller in that period.
- Non-zero: use `references/telegram-polling-conflict-duplicate-poller.md` to find and stop the duplicate consumer.

Also inspect recent Telegram network warnings separately; they explain delayed catch-up but not necessarily duplication:

```bash
journalctl --user -u hermes-gateway-kira.service --since '3 hours ago' --no-pager \
  | grep -Ei 'Telegram.*(network|fallback|ReadError|reconnect|unreachable)' | tail -80
```

## Late replies that are not duplicate Telegram agents

If the user sees a reply to an already-finished topic, check for:

- Hermes background process completion notices delivered after the original turn;
- long tool calls that returned late;
- slash workers / TUI gateway workers for an already-started session;
- Telegram network reconnects causing delayed delivery.

Report this distinction explicitly: "no duplicate Telegram gateway evidence; this looks like delayed completion/reconnect" when the process and journal checks support it.

## Pitfalls

- `grep`/substring matching over `/proc/*/cmdline` can count the current diagnostic command as a gateway. Parse argv instead.
- Web UI, bridge, and `hermes-kira-serve` processes are not Telegram consumers by themselves. List them as adjacent services, not duplicate Telegram gateways.
- Do not claim stability from process count alone. Include journal conflict count and restart count.
