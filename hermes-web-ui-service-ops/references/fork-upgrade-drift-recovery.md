# Hermes Web UI fork upgrade drift recovery

Use when the live `hermes-web-ui` was upgraded to an upstream npm release and Maxim reports that local/fork improvements disappeared.

## Symptom

The service is healthy and reports the new upstream Web UI version, but custom Kira/fork features are missing: native navigation links, clean `/session/:id` URLs, external skill directory listing, bridge runtime compatibility fixes, or other fork-only UX patches.

## Durable diagnosis pattern

1. Check what the systemd service actually runs:
   - `systemctl --user show hermes-web-ui.service -p WorkingDirectory -p ExecStart -p Environment --no-pager`
   - `readlink -f /home/werserk/.npm-global/lib/node_modules/hermes-web-ui`
   - `node -e "console.log(require('/home/werserk/.npm-global/lib/node_modules/hermes-web-ui/package.json').version)"`
   - `curl -fsS http://127.0.0.1:8648/health`
2. Compare active installed package vs fork worktrees:
   - `git worktree list`
   - `git -C /home/werserk/2-kira/hermes-web-ui-main log --oneline -10 --decorate`
   - `git -C /home/werserk/2-kira/hermes-web-ui-main log --oneline --cherry-pick --right-only upstream/main...origin/main`
3. Probe for known fork features in both active install and fork main:
   - Native links: `RouteLinkItem`, `openSessionInNewTab`, `sessionLinkCopied`
   - Clean URLs: `createWebHistory`, `path: '/session/:sessionId'`, `/group-chat/room/:roomId`
   - Skills: `external_dirs`, `externalDirs`
   - Math: `@vscode/markdown-it-katex`, `katex`
4. If active install lacks fork probes but fork main contains them, this is upgrade drift: the deploy points at upstream npm package instead of the integrated fork build.

## What usually should be restored

For Kira's Hermes Web UI fork, the minimum expected fork-only improvements are usually:

- Native navigation: real links for sidebar/session navigation, middle-click/Cmd-click support, `Open in new tab` / `Copy link` session actions.
- Clean path-based URLs: `createWebHistory()`, `/session/:sessionId`, `/history/session/:sessionId`, `/group-chat/room/:roomId`, legacy `/hermes/...` redirects, login redirect preservation.
- External skills directory support: Web UI skills listing must include `config.skills.external_dirs`.
- Bridge/runtime compatibility fixes that were merged into fork main before the upgrade.

Do not assume every remote feature branch is mandatory. Branches such as tool-trace visibility, mobile overlay fixes, token accounting, or group-chat cache work should be classified as candidates unless they were already part of fork `origin/main` or Maxim confirms they are required.

## Recovery approach

Preferred recovery is not to simply downgrade. Instead:

1. Create an integration branch from current `upstream/main` / release tag.
2. Port fork-only commits from `origin/main` with cherry-pick or manual patches.
3. Resolve conflicts in favor of new upstream architecture where appropriate (for example, if upstream added profile-aware route/session fixes, keep them and reapply clean URLs/native-link behavior on top).
4. Run targeted tests for restored features, then build and smoke test:
   - unit tests for navigation/session/link helpers
   - targeted Playwright specs for native navigation and authenticated shell
   - `npm run build`
5. Deploy by linking or installing the integrated fork build, restart the user service, and verify:
   - `systemctl --user is-active hermes-web-ui.service`
   - `curl -fsS http://127.0.0.1:8648/health`
   - external HTTPS route returns 200

## Pitfalls

- A healthy `/health` and correct upstream version do not mean fork improvements are active.
- `readlink -f` on npm global package may return the package directory itself when it is no longer a symlink; explicitly probe for source files/features, not just the path.
- `upstream/main` may already contain some former fork improvements, e.g. KaTeX/LaTeX rendering. Classify these as already active rather than re-porting blindly.
- When reporting, separate: **definitely inactive but should be active**, **already active upstream**, and **candidate branches requiring Maxim confirmation**.
