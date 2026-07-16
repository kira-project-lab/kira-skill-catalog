# Dev integration branch flow

Use this for Kira Hermes Web UI micro-feature staging.

## Branch roles

- `origin/main`: production-ready line. Production deploys only from here.
- `origin/dev`: integration/review/staging line. It starts from `origin/main` and accumulates approved micro-features before a later `dev -> main` decision.
- `feat/*`, `fix/*`, `refactor/*`: short-lived feature branches.

## Default workflow

1. Refresh base refs:
   ```bash
   git fetch origin main dev --prune
   ```
2. Create micro-feature branches from `origin/dev`:
   ```bash
   git switch -c feat/<small-feature> origin/dev
   ```
3. Open PRs with base `dev`, not `main`:
   ```bash
   gh pr create --repo kira-project-lab/hermes-web-ui --base dev --head feat/<small-feature> ...
   ```
4. Deploy a feature branch to Hermes dev only when Maxim asks for live preview; do not infer that opening a PR means deploy.
5. Merge approved micro-feature PRs into `dev` first.
6. Promote `dev` to `main` only after Maxim explicitly decides the integrated set is production-ready.

## Existing PR retargeting

When the workflow changes from `main`-based PRs to `dev`-based staging, retarget open micro-feature PRs instead of recreating them:

```bash
gh pr edit <PR> --repo kira-project-lab/hermes-web-ui --base dev
gh pr view <PR> --repo kira-project-lab/hermes-web-ui --json baseRefName,headRefName,mergeable,mergeStateStatus,statusCheckRollup
```

Verify after retargeting:

- `baseRefName` is `dev`;
- PR remains `MERGEABLE` / `CLEAN` or the conflict is understood;
- existing checks are still green or rerun/queued as expected.

## Creating `origin/dev`

If `origin/dev` does not exist and Maxim asks to initialize it from current `origin/main`:

```bash
git fetch origin main --prune
git ls-remote --heads origin dev
git push origin origin/main:refs/heads/dev
git fetch origin dev
git rev-list --left-right --count origin/main...origin/dev
```

Expected initial divergence: `0 0`.

## Pitfalls

- Do not merge feature PRs directly to `main` unless the task is a production hotfix or Maxim explicitly chooses `main`.
- Do not deploy production from `dev`; dev is an integration decision branch, not the production source.
- Do not assume Hermes dev runtime follows `origin/dev`; it serves whichever branch is checked out in `/home/werserk/2-kira/hermes-web-ui-dev` and built/restarted.