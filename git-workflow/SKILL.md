---
name: git-workflow
description: Dev/main branching with promotion trains — batch owner review of a cumulative diff instead of per-PR review, no-squash promotion, hotfix path, layered rollback. Use when working in a repo that has a dev branch, or when setting up the delivery flow for a project whose owner wants to review results, not every PR.
---
<!-- vendored from werserk/dev-culture@3fc1388 — edit there and re-run scripts/vendor.sh -->

# Git workflow: dev/main with promotion trains

Two long-lived branches. `main` is the certified canon — production deploys only from it,
and it is never broken. `dev` is the integration branch — feature work merges there
continuously, conflicts are resolved as they land, and it is allowed to be briefly broken.
The owner reviews **one cumulative diff** per promotion train, not every feature PR.

```
feature/x ──PR──▶ dev ──── one promotion PR ────▶ main ──▶ production
feature/y ──PR──▶ dev      (owner reviews the
feature/z ──PR──▶ dev       cumulative diff once)
```

## Applicability

- The target repo **has a `dev` branch** → work by this scheme.
- It does not → follow that repo's default flow. Never introduce `dev` into a repo
  unilaterally; adoption is an owner decision (see "Adopting" below).

## Daily rules

1. **Feature work**: branch off `dev` with a typed prefix (`feat/…`, `fix/…`, `docs/…`,
   `ops/…`), one concern per branch, PR back into `dev`. Squash-merge is fine here —
   it keeps `dev` history clean.
2. **Never push directly to `main`.** Not even "just docs". The repo's `.githooks/`
   block it locally; `ALLOW_MAIN_PUSH=1` exists for emergencies only.
3. **Conflicts are resolved in `dev`**, at feature-merge time — the second PR rebases
   onto current `dev`. `main` never sees an unresolved conflict.

## The promotion train (dev → main)

- **When**: around a meaningful milestone, but at most a week apart — a bigger batch
  stops being reviewable, which defeats the whole point.
- **How**: open a PR with base `main`, head `dev`. Its diff must equal
  `git diff main...dev` exactly. The owner reviews and merges.
- **Merge method — the load-bearing rule**: the promotion PR is merged as a **merge
  commit, NEVER squash** (fast-forward also acceptable). A squashed promotion makes
  git forget that `dev` was merged: every later train re-shows old changes, and the
  diff becomes a lie that compounds. Feature PRs into dev may squash; promotion must not.
- **After the train**: `git checkout dev && git merge main` (brings the merge commit
  back so histories stay convergent). Then `git diff main...dev` must be empty.

## Hotfix path

Production is broken and cannot wait for a train: branch off `main` → PR into `main`
directly → deploy. Immediately after: `git merge main` into `dev`, or the next train
will silently revert the hotfix.

## Rollback layers (cheapest first)

1. A bad feature still in `dev`: revert it in `dev`; `main` never noticed.
2. A bad train already in `main`: `git revert -m 1 <merge-commit>` on main, then merge
   main back into dev.
3. Stateful damage (DB migrations, runtime state): restore the pre-deploy snapshot the
   deploy pipeline took (VM/container snapshot, DB dump). Git cannot roll back state —
   take the snapshot BEFORE converging, not after.

## Adopting this flow in a repo

Run `scripts/git-workflow-init.sh` from the canonical repo
(https://github.com/werserk/dev-culture) inside the target clone. It creates and pushes
`dev`, sets it as the GitHub default branch (so new PRs target it), installs
`.githooks/` (pre-push + pre-commit main protection), and enables `core.hooksPath`.
Manual follow-ups it prints: add a "deploys only from main" guard to the repo's
Makefile/CI if it has a deploy entry point, and record the flow in CONTRIBUTING.md.

## For agents working under this flow

- Check the branch layout before the first commit: `git branch -r | grep origin/dev`.
- Target `dev` in every PR unless the task is explicitly a hotfix or the promotion
  train itself.
- Report the branch and PR target explicitly when done — a PR opened against the wrong
  base is a process defect worth flagging, not silently retargeting.
