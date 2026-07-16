# Hermes Web UI version update runbook

Use when Maxim asks to update Hermes Web UI to a newer version/release/upstream state.

## Principle

For Kira production, update the canonical git checkout and rebuilt `dist`, then restart `hermes-web-ui.service`. Do **not** use `hermes-web-ui update` / global `npm install -g` unless live systemd proves production runs from the global package.

## Baseline facts to verify

Expected Kira production topology:

- Checkout: `/home/werserk/2-kira/hermes-web-ui`
- Origin: `https://github.com/kira-project-lab/hermes-web-ui.git`
- Upstream: `https://github.com/EKKOLearnAI/hermes-web-ui.git`
- Service: `hermes-web-ui.service`
- ExecStart: `/usr/bin/node /home/werserk/2-kira/hermes-web-ui/dist/server/index.js`
- Port: `127.0.0.1:8648`
- Hermes profile: `/home/werserk/.hermes/profiles/kira`
- Web UI state: `/home/werserk/.hermes-web-ui`

## Steps

1. **Confirm live source**
   ```bash
   systemctl --user show hermes-web-ui.service -p WorkingDirectory -p ExecStart -p Environment --no-pager
   curl -fsS http://127.0.0.1:8648/health
   ```
   If `ExecStart` does not point at `/home/werserk/2-kira/hermes-web-ui/dist/server/index.js`, stop and switch to the actual live source path.

2. **Inspect repo state**
   ```bash
   cd /home/werserk/2-kira/hermes-web-ui
   git status --short --branch
   git remote -v
   git fetch origin
   git fetch upstream
   ```
   Classify any dirty files before touching them. Do not overwrite unrelated work.

3. **Choose update source**
   - Upstream release/tag/commit if Maxim asked for a new upstream version.
   - `origin/main` if the task is to deploy the latest canonical Kira version.
   - A named branch only if Maxim explicitly asked for that branch.

4. **Create/update branch**
   ```bash
   git switch main
   git pull --ff-only origin main
   git switch -c update/hermes-web-ui-<version-or-date>
   ```
   Then merge/cherry-pick the selected upstream/tag changes. Resolve conflicts narrowly.

5. **Install/build**
   ```bash
   npm ci --ignore-scripts
   npm run harness:check
   npm run test
   npm run build
   ```
   For broad/breaking updates, also run `npm run test:coverage` and `npm run test:e2e`.

6. **Record build metadata if the repo uses it**
   Keep build metadata aligned with the deployed git ref, service, and port. Do not let metadata claim a commit that is not being served.

7. **Promote**
   - For production-affecting updates, get Maxim approval before merge/deploy if the change is not explicitly requested as immediate production update.
   - Merge to `origin/main` before production deploy.
   - Build production from `origin/main`, not from an arbitrary local branch.

8. **Restart and verify**
   ```bash
   systemctl --user restart hermes-web-ui.service
   systemctl --user is-active hermes-web-ui.service
   ss -ltnp | grep ':8648'
   curl -fsS http://127.0.0.1:8648/health
   ```
   Then verify served assets/bundle if the update is browser-visible.

9. **Rollback path**
   If health or browser boot fails: switch checkout back to the previous known-good commit on `origin/main`, rebuild, restart service, verify `/health`, then report the blocker.

## Success criteria

- Git branch/commit matches intended update source.
- `npm run build` passes.
- `hermes-web-ui.service` is active.
- `127.0.0.1:8648/health` returns 200.
- Served bundle/source metadata matches the intended commit.
- No new critical errors appear in fresh server/bridge logs.
