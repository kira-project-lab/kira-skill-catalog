# Hermes Web UI upgrade / fork drift audit

Use this when a `hermes-web-ui` upgrade unexpectedly removes local improvements or Maxim asks which branches/features are no longer active.

## Symptom

The service is healthy and reports the new upstream version, but previously deployed fork improvements are missing. Example: after upgrading to `hermes-web-ui@0.6.0`, the user lost native navigation / clean URL behavior even though those commits existed in `origin/main`.

## Key distinction

Do not assume the live service is running the repo worktree. Check the actual systemd target and npm global package path:

```bash
systemctl --user show hermes-web-ui.service -p WorkingDirectory -p ExecStart -p Environment --no-pager
readlink -f /home/werserk/.npm-global/lib/node_modules/hermes-web-ui
node -e "console.log(require('/home/werserk/.npm-global/lib/node_modules/hermes-web-ui/package.json').version)"
curl -fsS http://127.0.0.1:8648/health
```

If `/home/werserk/.npm-global/lib/node_modules/hermes-web-ui` is a real installed package rather than a symlink to `/home/werserk/2-kira/hermes-web-ui-main`, then `npm upgrade` likely replaced the previously linked fork deployment.

## Audit recipe

1. Fetch both remotes:

```bash
git fetch origin --prune
git fetch upstream --tags --prune
```

2. Identify live package probes. Use source files when the live package is linked; use `dist/` and `package.json` when it is an installed npm package:

```bash
cd /home/werserk/.npm-global/lib/node_modules/hermes-web-ui
for p in \
  packages/client/src/components/common/RouteLinkItem.vue \
  packages/client/src/composables/usePersistentRecord.ts \
  docs/plans/2026-05-24-web-ui-native-navigation.md \
  scripts/check-installed-katex-rendering.mjs; do
  test -e "$p" && echo "yes $p" || echo "no  $p"
done

grep -R -n "openSessionInNewTab\|RouteLinkItem\|createWebHistory\|external_dirs" dist package.json 2>/dev/null | head -40
```

3. Compare fork branches against upstream and fork main:

```bash
git log --oneline --cherry-pick --right-only upstream/main...origin/main
git log --oneline --cherry-pick --left-only upstream/main...origin/main | head -60

git for-each-ref --format='%(committerdate:short) %(refname:short) %(subject)' \
  --sort=-committerdate refs/remotes/origin refs/heads | head -80
```

4. For each suspected feature, compare exact source probes:

```bash
git grep -n "openSessionInNewTab\|RouteLinkItem\|external_dirs" origin/main -- packages scripts docs tests
git grep -n "openSessionInNewTab\|RouteLinkItem\|external_dirs" upstream/main -- packages scripts docs tests || true

git show origin/main:packages/client/src/router/index.ts | sed -n '1,100p'
git show upstream/main:packages/client/src/router/index.ts | sed -n '1,100p'
```

## Common fork features to check

- Native navigation / middle-click links: `RouteLinkItem.vue`, `openSessionInNewTab`, session rows as `<a href>`.
- Clean URLs / history routing: `createWebHistory()`, `/session/:sessionId`, `/history/session/:sessionId`, `/group-chat/room/:roomId`, legacy `/hermes/*` redirects.
- External skill dirs: `config.skills?.external_dirs` in server skills controller.
- Bridge runtime provider compatibility: local bridge/provider compatibility commits.
- LaTeX/KaTeX: may already be in upstream; verify by checking dependencies and `MarkdownRenderer.vue`, not by assuming it was lost.

## Recommended recovery pattern

Create an integration branch from `upstream/main` / the current release tag, then port only the missing fork improvements:

```bash
git checkout -b integrate-v0.6.0-local-improvements upstream/main
# cherry-pick or manually port origin/main-only commits
# resolve conflicts preserving upstream profile-aware fixes
git log --oneline --cherry-pick --right-only upstream/main...origin/main
```

Then verify and deploy from the integrated worktree:

```bash
npm test -- <targeted tests>
npm run build
npm run test:e2e -- <targeted e2e specs>
npm link
systemctl --user restart hermes-web-ui.service
curl -fsS http://127.0.0.1:8648/health
curl -fsSI https://hermes.kiraproject.ru/ | head -20
```

## Pitfalls

- Do not claim a branch is active just because it exists in git; prove the live service path contains the feature or is symlinked to the right worktree.
- Do not blindly deploy old `origin/main` over a new upstream release. Port fork improvements onto the new release so upstream profile/user-scope fixes are preserved.
- `package.json` dependencies alone are insufficient proof of UI behavior; grep source/dist for the actual feature markers and, for rendering, smoke-test in the browser when needed.
