# Dev CI bootstrap and integration promotion

Use this when a Hermes Web UI integration PR targets `dev`, local/live validation is green, but GitHub reports no PR checks or the `dev` branch has not yet been wired for the current workflow triggers.

## Root cause pattern

GitHub evaluates `pull_request` workflow triggers from the **base branch**. Adding `pull_request: branches: [dev]` only in the integration/head branch may not make checks appear on that PR until the workflow file exists in `dev`.

If Maxim explicitly allows direct changes to `dev`, the best route is usually:

1. Bootstrap workflow trigger changes into `dev` first.
2. Promote the already-certified integration branch to `dev` with a backup ref and `--force-with-lease` if the history is intentionally replaced.
3. Trust the resulting `push` workflows on `dev` as the integration gate.
4. Redeploy live-dev from `origin/dev` and verify runtime health/browser smoke.

## Safe command pattern

From `/home/werserk/2-kira/hermes-web-ui-dev`, with integration branch already certified locally/live-preview:

```bash
git fetch origin dev integration/upstream-<version> --prune
OLD_DEV=$(git rev-parse refs/remotes/origin/dev)
NEW_DEV=$(git rev-parse HEAD)
STAMP=$(date -u +%Y%m%d-%H%M%S)
BACKUP="backup/dev-before-upstream-<version>-promotion-$STAMP"

git branch "$BACKUP" "$OLD_DEV"
git push origin "$BACKUP"
git push --force-with-lease=refs/heads/dev:$OLD_DEV origin HEAD:dev

git fetch origin dev --prune
git rev-parse --short refs/remotes/origin/dev
git rev-parse --short HEAD
```

Only use the force-with-lease promotion when the user has authorized direct `dev` changes or the integration plan explicitly calls for replacing `dev` with the certified branch. Otherwise, open/maintain a PR and wait for review.

## Workflow trigger bootstrap

For fork-internal `dev` integration, the core workflows should usually include `dev` in both `push` and `pull_request` triggers, for example:

```yaml
on:
  push:
    branches:
      - dev
      - main
  pull_request:
    branches:
      - dev
      - main
```

If the workflow edits themselves must land in `dev` before PR checks can appear, use a short detached worktree at `origin/dev`, cherry-pick the workflow-trigger commit, run `npm run harness:check` and `git diff --check`, then push `HEAD:dev`. Remove the temporary worktree afterward.

## Artifact quota pitfall

A Playwright CI job can show that tests passed but the overall job failed while uploading reports:

```text
Failed to CreateArtifact: Artifact storage quota has been hit.
```

This is not an E2E failure. Inspect the job steps: if `Run Playwright tests` is green and only `Upload Playwright report` fails, narrow the artifact upload trigger instead of changing tests. For normal CI, prefer uploading Playwright artifacts only on failure:

```yaml
- name: Upload Playwright report
  if: ${{ failure() }}
  uses: actions/upload-artifact@v4
```

Then re-run the `dev` push workflows and verify `Build` and `Playwright` pass.

## Final verification

After promotion:

```bash
gh run list --repo kira-project-lab/hermes-web-ui --branch dev --limit 10
bash scripts/deploy-dev-branch.sh dev
curl -fsS https://app.dev.kiraproject.ru/health | jq '{webui_version,runtime,git_branch,git_ref,git_commit}'
```

Also run the dev superadmin/browser smoke if the integration touched browser-visible areas. Report production as untouched unless `main` was explicitly promoted and prod `/health` verified.
