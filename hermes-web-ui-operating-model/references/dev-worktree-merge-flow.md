# Dev worktree merge flow

Use this when the canonical `main` checkout has a new commit that must be carried into the live-dev surface.

## Default direction

- Treat `/home/werserk/2-kira/hermes-web-ui-dev` as the default working surface for ongoing Hermes Web UI implementation once the work should continue in `dev`.
- Keep `/home/werserk/2-kira/hermes-web-ui` as the canonical production-oriented checkout.
- When asked to continue future work in `dev`, do not keep editing in the `main` checkout and then copy changes over manually.

## Occupied worktree pitfall

If `dev` is already checked out in a separate worktree, `git switch dev` from the canonical checkout will fail because the branch is in use elsewhere. In that case, operate directly inside the dev worktree instead.

## Safe merge sequence

When `main` has a commit that should land in `dev` and the dev worktree already contains local edits:

1. Stash the dev worktree changes, including untracked files, if needed.
2. Fast-forward or merge `main` into the dev worktree.
3. Restore the stashed worktree changes.
4. Verify the dev worktree HEAD now contains the new `main` commit and that the intended local edits are still present.

## Verification

- Check `git status --short --branch` in the dev worktree.
- Check `git log --oneline --decorate -1` to confirm the imported commit.
- If the service/runtime is involved, verify the live-dev host separately; git state alone is not runtime proof.
