# Merging `upstream/main` into Kira `dev`

Use when Maxim asks to bring the author's upstream changes into the Kira integration branch.

## Choose the integration direction first

Do not assume the right move is always `git merge upstream/main` into the current Kira `dev`. When upstream has advanced several releases and Kira has its own large fork, first compare both directions:

```bash
git fetch origin dev main
git fetch upstream main
git rev-list --count origin/dev..upstream/main
git rev-list --count upstream/main..origin/dev
git log --format=%s --no-merges upstream/main..origin/dev | head -120
git diff --stat --find-renames upstream/main...origin/dev
```

If Kira-only work is mostly shallow styling, a direct upstream-into-`dev` merge may be fine. If Kira-only work includes chat/session architecture, server-authoritative state, bridge/runtime behavior, deploy topology, Paperclip, profile/OAuth/STT safety, or persistence APIs, prefer a branch-from-upstream strategy:

1. Create an integration branch from the author's current release, e.g. `integration/upstream-0.6.17` from `upstream/main`.
2. Carry Kira changes onto it by layers rather than one blind merge:
   - Kira deploy/topology and Paperclip support.
   - Server/session persistence contracts.
   - Bridge/runtime/profile/STT/provider behavior.
   - Chat/session UI architecture.
   - Visual design/Obsidian shell/composer polish last.
3. Validate the branch, then merge the reconciled result into `origin/dev`.
4. Promote `dev` to `main` only after review and runtime validation.

This direction keeps the newest upstream runtime/provider/desktop fixes as the base and reduces the chance that older Kira fork code silently overwrites them. It is especially appropriate when the local fork is many commits ahead but much of the value is selective UI/UX that can be re-applied on top of the author's newer architecture.

## Direct upstream-into-dev workflow

Use this only after the direction check shows that a direct merge is still the best path.

1. Work in `/home/werserk/2-kira/hermes-web-ui-dev` on `dev` and verify cleanliness first.
2. Fetch both remotes and measure divergence:
   ```bash
   git fetch origin dev
   git fetch upstream main
   git rev-list --left-right --count origin/dev...upstream/main
   ```
3. Fast-forward local `dev` to `origin/dev`, then merge upstream:
   ```bash
   git pull --ff-only origin dev
   git merge --no-edit upstream/main
   ```
4. Resolve conflicts by preserving Kira-local behavior plus upstream fixes when both are compatible. Common conflict patterns seen here:
   - `docs/cli-chat-sessions.md`: upstream moved change history to `docs/chat-chain-changes/`; keep the fragment-based policy instead of extending the old central table.
   - `packages/client/src/stores/hermes/chat.ts`: preserve local title-generation handling and upstream reasoning/abort cleanup when both appear in the same run-completion/stop-streaming area.
   - `packages/server/src/services/hermes/run-chat/handle-bridge-run.ts`: keep both local session-title-generator imports and upstream abort helpers if both are referenced.
   - tests that mock chat socket APIs may need new upstream handlers such as `onSessionTitleUpdated` added to existing mocks.
5. Stage resolved files and confirm no conflict markers remain in affected files.

## Build dependency pitfall

If the shell has `NODE_ENV=production`, `npm ci --ignore-scripts` may omit devDependencies and make `npm run build` fail with missing build tools such as `vue-tsc`. For merge validation, install with dev dependencies explicitly:

```bash
NODE_ENV=development npm ci --ignore-scripts
npm run build
```

This is a validation-environment guard, not a claim that the project build is broken.

## Success criteria

For broad upstream merges, conflict-free Git state and a passing build are not enough to publish `origin/dev`. Before push:

- `NODE_ENV=development npm ci --ignore-scripts` has completed successfully.
- `npm run harness:check` passes.
- `npm run build` passes after conflict resolution.
- `npm run test:coverage` passes; if it is red, stop before push and report blockers.

After push:

- Merge commit is pushed to `origin/dev`.
- `git merge-base --is-ancestor upstream/main origin/dev` succeeds.
- Working tree is clean.
- Live-dev restart/health validation has run only after the pushed green merge.

See `references/upstream-main-merge-validation-pitfalls.md` for common post-merge test and TypeScript reconcile issues.