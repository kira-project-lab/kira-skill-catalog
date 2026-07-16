# SQLite readonly database recovery for Hermes Web UI

## Symptom
- Browser panel shows: `Error: attempt to write a readonly database`
- Web UI may still answer `/health`, but some UI actions fail.

## What we found in the last recovery
- The active systemd user service was `hermes-web-ui.service`.
- The process was started from a deleted AppImage extraction directory, so the logged cwd was not reliable for DB-path reasoning.
- The unit was missing `NODE_ENV=production`.
- Adding `NODE_ENV=production` to the service environment and restarting the unit removed the error.

## Fix sequence
1. Inspect the unit env:
   - `systemctl --user show hermes-web-ui.service -p Environment`
2. Ensure these are set in the service unit:
   - `HERMES_HOME=/home/<user>/.hermes/profiles/<profile>`
   - `NODE_ENV=production`
3. Reload and restart:
   - `systemctl --user daemon-reload`
   - `systemctl --user restart hermes-web-ui.service`
4. Verify:
   - `systemctl --user is-active hermes-web-ui.service`
   - `ss -ltnp | grep ':8648'`
   - `curl -fsS http://127.0.0.1:8648/health`
5. Re-check `~/.hermes-web-ui/logs/server.log` for fresh SQLite errors.

## Notes
- Prefer the live listener PID and latest logs over stale PIDs in older log lines.
- If the browser still shows an error after `/health` is OK, check the browser console and the newest server log line before touching the database file itself.
