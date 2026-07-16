# Integration Branch to Dev Promotion

Use after an upstream sync branch has passed local gates and branch-preview/live QA, and Maxim explicitly approves merging it into `origin/dev`.

## Preconditions

- Integration branch is pushed, e.g. `origin/integration/upstream-0.6.17`.
- Branch preview or live-dev QA passed.
- Local gates passed for the integration branch:
  - `npm run harness:check`
  - `npm run test`
  - `npm run test:coverage`
  - `npm run test:e2e`
  - `npm run build`
- PR/check expectations are explicit:
  - confirm the current base branch workflow config already includes `dev` in `pull_request.branches` before waiting for GitHub checks;
  - if the integration PR itself adds that workflow trigger, GitHub will not use it to create checks for the same PR, because `pull_request` workflows are read from the base branch;
  - either land a CI-bootstrap change into `dev` first, or state that promotion depends on local/live-preview gates plus manual approval.
- Maxim approved merge into `origin/dev`.
- `origin/main` / production are out of scope unless separately approved.

## Safe promotion flow

Use the live-dev checkout because `dev` should become the working dev surface:

```bash
cd /home/werserk/2-kira/hermes-web-ui-dev

git status --short --branch
git fetch origin dev main integration/upstream-<version> --prune

git switch dev
git reset --hard refs/remotes/origin/dev

git merge --ff-only refs/remotes/origin/integration/upstream-<version>
git push origin dev
```

Prefer fast-forward when `origin/dev` has not moved since the integration branch was based. If fast-forward is not possible, stop and inspect the new `origin/dev` commits before merging.

## Switch live-dev from preview to dev

After pushing `dev`, ensure the public dev host is no longer pinned to the preview branch:

```bash
systemctl --user restart hermes-web-ui-dev.service

curl -fsS http://127.0.0.1:8647/health | jq '{status,webui_version,runtime,git_branch,git_ref,git_commit}'
curl -fsS https://app.dev.kiraproject.ru/health | jq '{status,webui_version,runtime,git_branch,git_ref,git_commit}'
```

Expected after promotion:

```text
git_branch: dev
git_ref: origin/dev
runtime: live-dev
```

If `/health` still reports `preview/<...>`, the source branch was pushed but the runtime is still pinned to the preview checkout/branch. Switch the live-dev checkout to `dev` and restart before reporting success.

## Minimal post-merge smoke

- API login with dev `kira` superadmin works.
- `/api/auth/me` reports `kira`, `super_admin`, `active`.
- Any public static assets introduced by the integration branch are served.
- Browser QA does not need to be fully rerun if the exact same commit already passed preview QA and health now reports that same commit on `dev`; run a focused smoke only.

## Report shape

```text
Merged integration/upstream-<version> into origin/dev.
origin/dev: <sha>
Live-dev: <version>, git_branch=dev, git_ref=origin/dev, git_commit=<sha>
Smoke: <items passed>
Prod/main untouched.
```
