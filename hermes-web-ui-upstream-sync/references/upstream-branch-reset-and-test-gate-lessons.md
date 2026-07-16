# Upstream integration branch reset and test-gate lessons

Context captured from the June 2026 Hermes Web UI sync stabilization work.

## Branch/reference pattern

When a previous upstream adoption attempt destabilizes `dev`, do not assume the newest `integration/upstream-*` branch is the current baseline. First inspect the exact refs:

```bash
git branch -a --list '*integration*' '*upstream*' '*backup*'
git show-ref | grep -E 'integration/upstream|backup/dev-before' || true
```

Expected pattern from this session:

- `integration/upstream-0.6.17` existed locally and remotely as an older adoption line.
- `integration/upstream-0.6.18` existed as a later adoption line.
- `backup/dev-before-main-reset-<timestamp>` preserved the old `dev` tip before resetting.
- The stable baseline was deliberately reset to `origin/main`, not inferred from either integration branch.

## Reset discipline after a failed adoption

If `dev` must be returned to stable baseline:

1. Create a backup ref for the current `dev` tip before force-updating anything.
2. Reset `origin/dev` to the stable `origin/main` commit only after the backup exists.
3. Reset the live-dev checkout to `origin/dev` and verify worktree cleanliness.
4. Verify live-dev health and version metadata from `/health`.
5. Treat old integration branches as inspection/backup lines, not as proof that they are safe to continue.

## Before creating or continuing the next `integration/upstream-*`

Do not start the next upstream update just because a special branch already exists. First require a minimal P0 certification gate around the product contracts that broke or were at risk:

- session list discoverability, chronology, pins, tags, filters;
- session-browser prefs persistence and profile scoping;
- chat row lifecycle/read/running/error state;
- runtime/provider/coding-agent launch contracts;
- static assets and Kira-specific settings preservation.

Use CodeGraph for blast-radius and affected-test selection, but treat tests/build/live health as the actual proof.

If the old integration branch was already promoted and then abandoned via `dev -> main` reset, do not continue it as if it were still the live integration base. Keep it for diff archaeology and create a new clean attempt, normally `integration/upstream-<version>-v2` for the same target or `integration/upstream-<current-version>` if upstream moved on. In the status answer, explicitly distinguish:

- historical special branch/worktree that existed;
- whether it reached `origin/dev` / live-dev;
- the reset/backup ref that preserved it;
- the recommended fresh branch for the next attempt.

## Session-list regression pattern

One concrete regression found during certification: logged-in session lists can under-scan Hermes rows before applying claim/pin/tag filtering. A low page limit plus many newer unclaimed sessions can hide older claimed sessions. Protect this with a deterministic server/controller regression test before upstream promotion.
