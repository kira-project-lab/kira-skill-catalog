# Hermes Web UI fork upstream-merge policy

Use when Maxim asks to recover from an accidental Web UI upgrade or to bring the fork forward to a new upstream release.

## Preferred branch strategy

- If Maxim says to activate local fork `main`, make `/home/werserk/2-kira/hermes-web-ui-main` the deployed worktree again and merge `upstream/main` into fork `main`.
- Create a backup branch before the merge.
- Preserve upstream release fixes, especially profile/user-scope auth changes, while keeping fork-only UX improvements that Maxim explicitly wants.
- After merge, push `origin/main`, `npm link` the fork worktree, restart `hermes-web-ui.service`, and verify `/health` plus the public domain.

## Feature policy from May 2026

- **Native navigation / middle-click links:** required locally and should be proposed upstream as a separate PR branch based on `upstream/main`, not mixed with clean URLs.
- **Clean URLs:** required locally. Upstream PR #956 adopted partial deep-link behavior but kept hash routing; keep local `createWebHistory()` clean paths unless Maxim changes direction.
- **External skills support:** not required by Maxim; do not spend recovery effort on it unless explicitly requested. If it already exists in fork main, avoid risky removal during a large merge unless the task is specifically to reduce fork delta.
- **KaTeX:** upstream-owned after PR #954; do not re-port old local KaTeX work unless a live regression proves upstream implementation is insufficient.

## Separate upstream PR for native links

When preparing the native navigation PR:

1. Start from fresh `upstream/main` in a separate worktree/branch.
2. Port only navigation-as-anchors changes: reusable route link component, sidebar links, session row links, context menu open/copy link affordances, tests.
3. Keep upstream hash-router URL shapes in that PR (for example `#/hermes/session/:id`) so maintainers can review native-link behavior independently from clean URL routing.
4. Preserve profile-aware session hrefs/copy links.
5. Run targeted unit tests, build, and e2e tests for native navigation/authenticated shell before opening the PR.
