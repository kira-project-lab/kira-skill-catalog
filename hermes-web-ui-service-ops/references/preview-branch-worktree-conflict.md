# Preview branch vs worktree conflict

Use this workflow when `scripts/deploy-dev-branch.sh <branch>` refuses to deploy because the target branch is already checked out in another worktree.

## Symptom

Git/deploy output looks like:

- `fatal: '<branch>' is already used by worktree at '...'`

## Why it happens

Hermes Web UI uses multiple worktrees/checkouts for different runtime surfaces. Git will not let the deploy flow repurpose a branch that is already attached to another worktree.

## Durable workaround

1. Keep the review branch unchanged.
2. Create a short-lived preview branch from the same base or commit.
3. Cherry-pick or merge the reviewed commit onto that preview branch.
4. Push the preview branch to origin.
5. Deploy the preview branch with `scripts/deploy-dev-branch.sh <preview-branch>`.
6. Verify the runtime reports the preview branch/commit in `/health`.

## Rules of thumb

- Do not fight the existing worktree lock by reusing the same branch name.
- Keep the PR branch for review and the preview branch for deployment separate when they need to coexist.
- Report both the review branch and the deployed preview branch so reviewers can trace what is running.
