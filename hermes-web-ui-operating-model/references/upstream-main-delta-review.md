# Upstream main delta review

Use when Maxim asks what is new on upstream/main relative to Kira origin/main, before deciding whether to merge/cherry-pick upstream work.

## Goal

Produce a concise feature/fix/risk summary without editing, merging, or deploying anything.

## Workflow

1. Use the Kira Hermes Web UI checkout/worktree that has both remotes configured, usually `/home/werserk/2-kira/hermes-web-ui-dev` for dev questions.
2. Record branch/worktree state first with `git status --short --branch`; do not modify or clean unrelated local work.
3. Fetch both refs explicitly:
   - `git fetch origin main --prune`
   - `git fetch upstream main --prune`
4. Verify both remote refs exist with explicit full refs, one ref per verification:
   - `git rev-parse --verify --short refs/remotes/origin/main`
   - `git rev-parse --verify --short refs/remotes/upstream/main`
   Avoid multi-ref `git rev-parse origin/main upstream/main` in scripted probes; if one token is ambiguous or not resolved as expected it can fail the whole probe and obscure which ref was bad.
5. Compare divergence with full remote refs:
   - `git rev-list --count refs/remotes/origin/main..refs/remotes/upstream/main`
   - `git rev-list --count refs/remotes/upstream/main..refs/remotes/origin/main`
   - `git merge-base refs/remotes/origin/main refs/remotes/upstream/main | cut -c1-8`
   Avoid `git merge-base --short`; some Git versions do not support that option.
6. Summarize upstream-only changes from commits and files:
   - `git log --oneline --decorate --no-merges refs/remotes/origin/main..refs/remotes/upstream/main`
   - `git diff --stat --find-renames refs/remotes/origin/main...refs/remotes/upstream/main`
   - inspect `package.json` version and changelog/i18n entries if present. Robust package-version probe: `git show refs/remotes/origin/main:package.json | python3 -c 'import sys,json; print(json.load(sys.stdin)["version"])'` and repeat for `refs/remotes/upstream/main`. Prefer this over fragile nested `node -e` quoting inside tool scripts.
7. Convert raw commits into product buckets: user-visible features, reliability fixes, security/storage changes, UI polish, and Kira-sensitive conflict surfaces.
8. Report whether the update is fast-forwardable or divergent. If divergent, recommend cherry-pick or grouped merge planning rather than implying a simple pull.

## Report shape

- Status: checked refs and location.
- Суть: upstream ref, origin ref, ahead/behind counts, version change.
- Bullets: grouped features/fixes, not raw commit dump.
- Risk: touched Kira-sensitive files/areas and likely merge complexity.
- Next: one practical adoption strategy.

## Pitfalls

- Do not answer from memory or old changelog text; always fetch and verify refs.
- Do not conflate `origin/dev` or local `dev` with production `origin/main` unless Maxim asks for dev comparison.
- Do not run merges, rebases, branch switches, deploys, or write implementation plans for a delta review. If Maxim asks “what is new?” answer that question directly; offer a merge plan only as the next step, not as the deliverable.
- If the working tree has local changes, mention only if it affects confidence or action safety; do not derail the summary with a full dirty-tree audit.
