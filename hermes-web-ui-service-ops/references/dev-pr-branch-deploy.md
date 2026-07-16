# Deploy a PR branch to Hermes Web UI dev

Use when Maxim asks to deploy a Hermes Web UI PR/branch to the dev preview service (`hermes.dev.ops.kiraproject.ru`). This is for the dedicated dev runtime, not production.

## Target topology

Expected dev runtime:

- Checkout: `/home/werserk/2-kira/hermes-web-ui-dev`
- Service: `hermes-web-ui-dev.service`
- Backend/API port: `8647`
- Frontend/Vite port: `8649`
- Public URL: `https://hermes.dev.ops.kiraproject.ru/`
- State: `/home/werserk/.hermes-web-ui-dev`
- Bridge endpoint: `ipc:///tmp/hermes-agent-bridge-dev.sock`

Always verify these from systemd before reporting success. Use `8647` for `/health`; `8649` is the browser-facing Vite frontend in live-dev mode.

## Workflow

1. Inspect current dev runtime and checkout:
   ```bash
   systemctl --user is-active hermes-web-ui-dev.service || true
   systemctl --user show hermes-web-ui-dev.service -p MainPID -p WorkingDirectory -p ExecStart -p Environment --no-pager || true
   ss -ltnp | grep -E ':(8647|8649)\\b' || true
   curl -fsS http://127.0.0.1:8647/health || true
   cd /home/werserk/2-kira/hermes-web-ui-dev
   git status --short --branch
   git rev-parse HEAD
   git log -1 --oneline --decorate
   ```

2. Switch the dev checkout to the PR branch:
   ```bash
   git fetch origin <branch>
   git switch <branch>
   git pull --ff-only
   ```

   If the requested branch is already checked out in another worktree, create a short-lived deploy branch from the same commit (for example `preview/<feature>-dev`) and deploy that branch instead. Keep the deploy branch explicitly named as a preview/deploy artifact, not as the review branch.

Prefer a non-destructive preview branch flow over force-push/rewrite when the target commit is already available remotely:
```bash
git fetch origin <review-branch>
git branch <preview-branch> origin/<review-branch>
git push origin <preview-branch>
bash scripts/deploy-dev-branch.sh <preview-branch>
```
Only use `git branch -f` / `git push -f` for preview redeploys after explicit user confirmation. A safer new preview branch avoids Hermes destructive-command confirmation and preserves the review branch unchanged.

   After switching, verify the branch still contains the dev service entrypoint used by the systemd unit:
   ```bash
   test -x scripts/start-live-dev.sh || git show origin/<known-live-dev-branch>:scripts/start-live-dev.sh > scripts/start-live-dev.sh
   chmod +x scripts/start-live-dev.sh
   ```
   Some feature branches are based before the live-dev helper existed. `scripts/deploy-dev-branch.sh` can successfully switch/build and then break `hermes-web-ui-dev.service` with `status=203/EXEC` because the unit's `ExecStart` points to the now-missing `scripts/start-live-dev.sh`. Commit the restored helper to the deploy branch before reporting the preview as deployed.

   Also check `vite.config.ts` for `server.allowedHosts` when serving through `hermes.dev.ops.kiraproject.ru`; add the host once if the branch predates the dev-host config. If later merging this deploy branch into `main`, resolve duplicate `allowedHosts` entries instead of leaving two same-name object keys.

3. Build from that checkout:
   ```bash
   npm run build
   ```

   If the target branch fails to build, do not restart the dev service into a broken checkout. Investigate the error narrowly, apply the smallest build-fix on the deployed branch, rerun `npm run build`, commit and push that fix, and report that the deployed branch now differs from its base by the fix commit. A common post-merge pattern is a TypeScript surface mismatch where new template usage or API metadata was merged but the Pinia store return shape/type did not expose it; fix the source type/export contract, not the consuming component.

4. Restart only the dev service:
   ```bash
   systemctl --user restart hermes-web-ui-dev.service
   ```

5. Verify after restart. The first health probe may race startup; if `curl` fails immediately after restart, check journal and retry after a few seconds before treating it as failure:
   ```bash
   sleep 3
   systemctl --user is-active hermes-web-ui-dev.service
   ss -ltnp | grep -E ':(8647|8649)\\b'
   curl -fsS http://127.0.0.1:8647/health
   curl -fsS https://hermes.dev.ops.kiraproject.ru/health
   git status --short --branch
   git rev-parse HEAD
   git log -1 --oneline --decorate
   journalctl --user -u hermes-web-ui-dev.service -n 30 --no-pager
   ```

6. For browser-visible changes, verify the served bundle, not just source/health. Avoid `curl | python`; write the response to a temp file, then parse it:
   ```bash
   curl -fsS https://hermes.dev.ops.kiraproject.ru/ -o /tmp/hermes-dev-index.html
   python -c "import re; html=open('/tmp/hermes-dev-index.html').read(); print('\n'.join(re.findall(r'/assets/(?:js|css)/[^\"<> ]+', html)))"
   ```
   Then fetch the relevant asset and search for stable tokens from the change when applicable.

7. For behavior that depends on runtime providers, sockets, DB state, or model calls, run an end-to-end browser check after bundle verification. Do not report "works" from health/bundle evidence alone. Example for session-title generation: create a fresh chat in the intended profile, wait for a real assistant text reply, then verify the title row/visible sidebar changed or inspect the feature's API result/reason.

## Report shape

Keep the report concise:

- branch and commit deployed;
- service active/listener/health status;
- public URL;
- served-bundle evidence for UI changes;
- one requested manual check if human verification is still needed.

Do not report production details unless production was touched; this workflow must not touch `hermes-web-ui.service` or `/home/werserk/2-kira/hermes-web-ui`.