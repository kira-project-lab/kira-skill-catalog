# Deploy / restart race note

Session finding:
- In this profile, the live `hermes-web-ui.service` already points directly at the repo checkout's `dist/server/index.js` (`WorkingDirectory=/home/werserk/2-kira/hermes-web-ui`).
- After `git merge upstream/main`, `npm run build`, `git push origin main`, and `systemctl --user restart hermes-web-ui.service`, a direct immediate `curl http://127.0.0.1:8648/health` can fail briefly even when `systemctl --user is-active` already reports `active`.

Verification sequence that avoided a false failure:
1. Check `systemctl --user status hermes-web-ui.service`.
2. Check `ss -ltnp | grep ':8648'` to confirm the listener exists.
3. Then call `/health` in a fresh request.

Implication:
- For deploy handoff, treat `systemctl is-active` as necessary but not sufficient; confirm the listener and then re-check health after the startup window.
