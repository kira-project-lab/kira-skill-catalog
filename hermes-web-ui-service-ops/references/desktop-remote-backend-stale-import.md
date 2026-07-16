# Hermes Desktop remote backend stale import

Use when Hermes Desktop on one machine shows a Python import error after a Hermes Agent update, especially when the visible path is a source file such as `/home/werserk/.hermes/hermes-agent/agent/model_metadata.py` but local import smokes pass.

## Failure shape

Example UI error:

```text
Hermes error
cannot import name 'is_output_cap_error' from 'agent.model_metadata'
(/home/werserk/.hermes/hermes-agent/agent/model_metadata.py)
```

Important pitfall: the desktop window may not be using the local checkout as its chat backend. It can be in remote mode and talk to a tunneled backend such as:

```json
~/.config/Hermes/connection.json
{
  "mode": "remote",
  "remote": { "url": "http://127.0.0.1:19119" }
}
```

That `127.0.0.1` is local to the desktop machine; it may be an SSH `-L` tunnel to another host's `hermes serve` service.

## Diagnostic order

1. On the desktop machine, read the active connection mode:

```bash
sed -n '1,120p' ~/.config/Hermes/connection.json
pgrep -af '127.0.0.1:19119|19119:127.0.0.1:9119|ssh -N.*9119'
```

2. If `mode=remote`, inspect the target backend host/service, not only the desktop checkout.

For Maxim's PC-backed contour:

```bash
systemctl --user show hermes-kira-serve.service -p MainPID -p ExecStart -p Environment --no-pager
pid=$(systemctl --user show hermes-kira-serve.service -p MainPID --value)
tr '\0' ' ' </proc/$pid/cmdline; echo
journalctl --user -u hermes-kira-serve.service --since '1 hour ago' --no-pager \
  | grep -E 'cannot import|ImportError|model_metadata|conversation_loop' -C 3
```

3. Verify the import with the same Python path the service uses:

```bash
cd /home/werserk/.hermes/hermes-agent
/home/werserk/.hermes/hermes-agent/venv/bin/python - <<'PY'
from agent.model_metadata import is_output_cap_error
import agent.conversation_loop
print('service_python_import_smoke=OK', is_output_cap_error('Invalid value: max_tokens should be <= 8192'))
PY
```

4. Restart the stale backend process after code updates. If running inside the gateway process blocks `systemctl restart`, kill only the service MainPID and let systemd restart it:

```bash
pid=$(systemctl --user show hermes-kira-serve.service -p MainPID --value)
kill -KILL "$pid"
for i in $(seq 1 30); do
  new=$(systemctl --user show hermes-kira-serve.service -p MainPID --value 2>/dev/null || echo 0)
  [ "$new" != "$pid" ] && [ "$new" != 0 ] && break
  sleep 1
done
curl -fsS --max-time 5 http://127.0.0.1:9119/api/status
```

5. From the desktop machine, verify the tunnel sees the restarted backend:

```bash
curl -fsS --max-time 5 http://127.0.0.1:19119/api/status
```

## Interpretation

- If file-level import smoke passes but the service log still reports the old import error, the live `hermes serve` process is stale. Restart that backend, not the local desktop checkout.
- A clean local `git status` on the laptop does not prove the remote backend is clean or restarted.
- A desktop process tree that only shows Electron can still use a remote backend; the chat failure may be on the tunneled PC service.
- After deleting/rebuilding venvs, keep launcher/unit paths aligned (`venv` vs `.venv`) before starting the desktop or backend services.
