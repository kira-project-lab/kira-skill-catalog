# Hermes Web UI live-dev transition notes

This reference captures the live-dev contract for `hermes.dev.ops.kiraproject.ru`.

## Canonical live-dev runtime

- checkout: `/home/werserk/2-kira/hermes-web-ui-dev`
- service: `hermes-web-ui-dev.service`
- startup: `bash scripts/start-live-dev.sh`
- frontend port: `8649`
- backend port: `8647`
- runtime label: `live-dev`
- state dir: `/home/werserk/.hermes-web-ui-dev`

## Health metadata expectations

`/health` should include:

- `runtime`
- `git_branch`
- `git_ref`
- `git_commit`
- `build_time`
- `service`
- `service_port`
- `frontend_port`

## Verification sequence

1. Check `systemctl --user show hermes-web-ui-dev.service -p ExecStart -p WorkingDirectory -p Environment`.
2. Confirm listeners on `8647` and `8649`.
3. Query `http://127.0.0.1:8649/health`.
4. Verify browser-visible change through HMR or a controlled backend restart.

## Transition pitfall

The live-dev starter should validate the checkout with `git -C "$REPO_DIR" rev-parse --is-inside-work-tree` instead of assuming the working directory itself is the only safe test. This avoids false failures when the service starts from systemd with an explicit repo path.
