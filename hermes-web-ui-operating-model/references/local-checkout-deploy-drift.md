# Local checkout deploy drift: why a pre-merge branch can show up on the live host

This session confirmed a recurring Hermes Web UI pitfall:

- GitHub Actions `build.yml` is a CI gate only; it validates PRs and `main` pushes but does not deploy the app.
- `hermes-web-ui.service` is a local systemd service that runs `node /home/werserk/2-kira/hermes-web-ui/dist/server/index.js` from the canonical checkout.
- If that checkout is switched to a feature branch and the service is restarted, the live host will serve that branch even before merge.
- `hermes-web-ui-dev.service` is a separate preview checkout and port; it is not the production host.

Verification commands that proved the drift in this session:

```bash
systemctl --user show hermes-web-ui.service -p WorkingDirectory -p Environment -p ExecStart --no-pager
systemctl --user show hermes-web-ui-dev.service -p WorkingDirectory -p Environment -p ExecStart --no-pager
git -C /home/werserk/2-kira/hermes-web-ui branch --show-current
git -C /home/werserk/2-kira/hermes-web-ui rev-parse --short HEAD
git -C /home/werserk/2-kira/hermes-web-ui-dev branch --show-current
git -C /home/werserk/2-kira/hermes-web-ui-dev rev-parse --short HEAD
```

Practical rule:

- When a live-host behavior changes before merge, first inspect the active service unit and checkout branch before assuming CI or deploy automation caused it.
