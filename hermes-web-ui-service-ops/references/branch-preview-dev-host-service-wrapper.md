# Branch preview deploy when the branch lacks dev-host service files

Use when deploying a Hermes Web UI branch to `hermes.dev.ops.kiraproject.ru` via `/home/werserk/2-kira/hermes-web-ui-dev` and the branch does not contain the local dev service wrapper expected by `hermes-web-ui-dev.service`.

## Symptom

After `scripts/deploy-dev-branch.sh <branch>`, the dev service fails with:

```text
status=203/EXEC
Unable to locate executable '/home/werserk/2-kira/hermes-web-ui-dev/scripts/start-live-dev.sh'
```

Root cause: the deploy script hard-resets the dev checkout to the branch. If that branch predates or omits `scripts/start-live-dev.sh`, systemd's `ExecStart` points to a file that no longer exists.

A second common dev-host-only symptom is Vite rejecting the public hostname:

```text
Blocked request. This host ("hermes.dev.ops.kiraproject.ru") is not allowed.
```

## Safe pattern

1. If the requested feature branch is already checked out in another worktree, create a dedicated preview branch from the same commit:

```bash
SRC=/home/werserk/2-kira/hermes-web-ui-paperclip-entrypoint
cd "$SRC"
BR=preview/<feature>-dev
SHA=$(git rev-parse origin/<feature-branch>)
git branch -f "$BR" "$SHA"
git push -f origin "$BR"
```

2. Deploy the preview branch into `/home/werserk/2-kira/hermes-web-ui-dev`:

```bash
cd /home/werserk/2-kira/hermes-web-ui-dev
bash scripts/deploy-dev-branch.sh "$BR"
```

3. If the service fails with missing `scripts/start-live-dev.sh`, restore the wrapper from a known dev-host branch or recreate it in the preview branch. The wrapper should write `.hermes-web-ui-build.json`, export live-dev metadata, set `HERMES_WEB_UI_STOP_GATEWAYS_ON_SHUTDOWN=0`, then `exec npm run dev`.

4. If public HTTPS returns the Vite host block, add the dev hostname to `vite.config.ts` in the preview branch:

```ts
server: {
  port: FRONTEND_PORT,
  strictPort: true,
  allowedHosts: ['hermes.dev.ops.kiraproject.ru'],
  proxy: {
    // ...
  },
}
```

5. Commit and push the preview-only dev-host fix:

```bash
git add scripts/start-live-dev.sh vite.config.ts
git commit -m "chore: make <feature> preview deployable on dev host"
git push origin "$BR"
systemctl --user restart hermes-web-ui-dev.service
```

## Verification

```bash
curl -fsS http://127.0.0.1:8649/health
curl -fsS https://hermes.dev.ops.kiraproject.ru/health
curl -fsS -I https://hermes.dev.ops.kiraproject.ru/<route>
```

The health response should show:

```json
{
  "runtime": "live-dev",
  "git_branch": "preview/<feature>-dev",
  "git_ref": "origin/preview/<feature>-dev"
}
```

For UI-specific changes, also fetch a served source/module or use a browser check to verify the route/component is visible from the public dev host.

## Pitfalls

- Do not patch production checkout or `hermes-web-ui.service` for a dev preview.
- Do not claim a failed deploy is successful just because `npm ci` completed; systemd may still be failing at `ExecStart`.
- Keep these dev-host fixes on a preview branch unless they are intentionally promoted into the feature/base branch.
