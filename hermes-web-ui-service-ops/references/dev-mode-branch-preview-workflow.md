# Dev Mode Branch Preview workflow

Use this when Maxim wants to review fork PRs by switching the running preview to a PR branch from the Web UI.

## Product pattern

Target review loop:

1. A fork-review PR appears in `kira-project-lab/hermes-web-ui`.
2. The PR is based on a shared review base that already contains Dev Mode Preview.
3. Maxim opens Settings → Dev Mode / Branch Preview.
4. Maxim selects the PR branch, builds it in an isolated worktree, and activates/serves that built preview.
5. Maxim manually verifies behavior and approves or requests changes.
6. Maxim returns the preview to `fork-review/review-base` or switches to another PR branch.

## Branch strategy

Do **not** add the Dev Mode Preview infrastructure commit to every feature PR. Seed it once into a shared base:

```text
fork-review/upstream-main + Dev Mode Preview = fork-review/review-base
```

Future fork-review PRs that need live preview should use:

```text
base: fork-review/review-base
head: fork-review/<feature>
```

Keep upstream submission separate and only after Maxim explicitly approves it.

## Implementation guardrails

- `dev.enabled` is off by default.
- Branch preview controls are visible only when Dev Mode is enabled.
- Endpoints are admin/super-admin guarded.
- Build selected branches in isolated worktrees/cache dirs, not in the active checkout.
- Do not accept arbitrary shell commands from the UI.
- Use strict branch/ref validation and argument-array process spawning.
- One active build at a time is enough for MVP.
- Capture status and log tail per profile.
- Activation should target a controlled review preview, not blindly mutate a production checkout.
- Always provide a return/reset action to `fork-review/review-base`.

## Deploy pattern after merge

When the Dev Mode Preview PR has passed CI and Maxim says it is verified:

1. Merge the fork PR into `fork-review/upstream-main`.
2. Push/update `fork-review/review-base` to the same SHA:
   ```bash
   git fetch origin
   git push origin origin/fork-review/upstream-main:refs/heads/fork-review/review-base
   ```
3. Use a dedicated deploy worktree for the live review instance, e.g. `/home/werserk/2-kira/hermes-web-ui-dev-mode-branch-builds`.
4. Switch it to `origin/fork-review/review-base`:
   ```bash
   git switch -C fork-review/review-base origin/fork-review/review-base
   pnpm run build
   ```
5. If the user-service package is symlinked, repoint the symlink intentionally:
   ```bash
   ln -sfn /home/werserk/2-kira/hermes-web-ui-dev-mode-branch-builds /home/werserk/.npm-global/lib/node_modules/hermes-web-ui
   systemctl --user restart hermes-web-ui.service
   ```
6. Verify the *served* app, not only git:
   ```bash
   systemctl --user is-active hermes-web-ui.service
   ss -ltnp | grep ':8648'
   curl -fsS http://127.0.0.1:8648/health
   readlink -f /home/werserk/.npm-global/lib/node_modules/hermes-web-ui
   git -C /home/werserk/.npm-global/lib/node_modules/hermes-web-ui rev-parse HEAD
   ```

Pitfall: immediately after `systemctl restart`, `/health` can fail for a few seconds while the server starts. Check systemd status/journal and retry health before assuming deploy failed.

## PR/ticket wording

For Kanban tasks and PR bodies, be explicit:

- "Seed Dev Mode Preview into `fork-review/review-base`; do not duplicate this infrastructure into every feature PR."
- "Future feature PRs can target `fork-review/review-base` for live preview."
- "No upstream PR actions unless Maxim explicitly approves."