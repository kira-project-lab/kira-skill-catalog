---
name: wrap-up
description: End-of-task closure — review the diff, decide and state the docs decision (new ADR / update docs / none), verify doc consistency and commit hygiene. Use before declaring any substantial coding task complete.
allowed-tools: Read Glob Grep Bash(git status *) Bash(git diff *) Bash(git log *)
---
<!-- vendored from werserk/dev-culture@3fc1388. Edit it there and copy the file back; there is no
     vendor script in this repository, and the one this banner used to name never existed here. -->

Close out the current task. Work from the actual diff, not memory.

## Steps

1. **Survey the change.** `git status --short` and `git diff` (staged + unstaged; plus commits on this branch not yet merged if relevant). Summarize what actually changed in 2–4 bullets.

2. **Make the docs decision.** Classify the change against the repo's documentation contract (in `CLAUDE.md`; if absent, use this default):
   - Domain rule / invariant / API contract / data ownership / infra topology / security boundary changed → **new ADR**. Where a company carries an `adr` skill, use it; where it does not, follow the repository's own `docs/decisions/` convention — next number, the sections its neighbours use, a row in the index, and a cross-link from anything it supersedes.
   - A previous ADR is contradicted → **superseding ADR**, never silent drift.
   - Behavior described in existing docs, runbooks, or README changed → **update those docs now**, in this same change.
   - Mechanical refactor / copy fix / dependency bump → **none**.

3. **Consistency sweep.** Grep docs for the names of things the diff renamed, removed, or re-scoped; check that any docs touched in the diff still match the code. Fix drift found within the task's scope; report drift outside it.

4. **Repo-specific checks.** If `CLAUDE.md`/`CONTRIBUTING.md` declare a definition of done (locales, migrations policy, test commands), verify each item against the diff.

5. **Commit hygiene.** If asked to commit: follow the repo's CONTRIBUTING (conventional commits, branch flow). Docs changes ride in the same commit/PR as the code they describe.

6. **Final statement.** End with exactly one line, always:
   `Docs decision: <new ADR NNNN | updated <paths> | none> — <one-line reason>.`
