# Prod vs runtime drift: compact verification pattern

Use this when the question is whether the latest `origin/main` is actually deployed.

## Rule

Check each live surface independently. Do not assume branch sync means deployment sync.

## Minimal probe set

1. Fetch remotes.
2. Compare the runtime-reported `git_commit` from each public health endpoint against `origin/main`.
3. Report any mismatch as source/runtime drift.

## Example outcome

- `origin/main` and `origin/dev` can point at the same commit.
- `hermes.dev.ops.kiraproject.ru` may already report that commit.
- `hermes.ops.kiraproject.ru` can still be on an older commit.

## Evidence to quote

- public prod health: `https://hermes.ops.kiraproject.ru/health`
- public dev health: `https://hermes.dev.ops.kiraproject.ru/health`
- repo refs: `git rev-parse origin/main origin/dev`

## Reporting rule

Say explicitly:

- what `origin/main` is,
- what prod reports,
- what dev reports,
- and whether prod is current.
