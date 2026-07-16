# Bridge timeout deploy verification

Session note: if you change `packages/server/src/services/hermes/agent-bridge/client.ts` or any timeout-related source, do **not** assume the live service picked it up.

## Verify the active runtime path

- Check what the systemd unit actually executes:
  - `systemctl --user show hermes-web-ui.service -p ExecStart -p WorkingDirectory -p Environment --no-pager`
- Check the installed package target:
  - `readlink -f /home/werserk/.npm-global/lib/node_modules/hermes-web-ui`
- Check the built server bundle in the active install:
  - inspect `dist/server/index.js` for the timeout literal / env lookup (`HERMES_AGENT_BRIDGE_TIMEOUT_MS`).

## Safe sequence after a timeout change

1. Update source or env var.
2. Rebuild the project.
3. Refresh the global install target if it points at a stale worktree.
4. Restart `hermes-web-ui.service`.
5. Re-check the active runtime path and the served bundle, not just the repo source.

## Why this matters

A stale global install or symlink can make the repo show `360000` while the live service is still serving an older bundle and logging the older timeout text. The error string in an already-running session is also historical; it does not rewrite after redeploy.
