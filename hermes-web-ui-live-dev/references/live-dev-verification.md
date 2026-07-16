# Live-dev verification

Use this checklist when deciding whether a Hermes Web UI change is actually active on `hermes.dev.ops.kiraproject.ru`.

## What to compare

- Local worktree: `git status --short --branch`
- Intended commit: `git rev-parse HEAD`
- Running host: `https://hermes.dev.ops.kiraproject.ru/health`
- Host commit: `git_commit` from `/health`
- Host runtime: `runtime` should be `live-dev`
- Service identity: `service` should be `hermes-web-ui-dev.service`

## Decision rule

A change is active on the dev host only if:

- the host runtime is `live-dev`, and
- the host commit matches the commit that contains the change.

A dirty local checkout does **not** imply the host is updated.

## Useful probes

```bash
git status --short --branch
git rev-parse HEAD
curl -fsS https://hermes.dev.ops.kiraproject.ru/health
```

## Common interpretation

- Local edits present + host commit older = change is not deployed/active yet.
- Host commit matches intended ref + tests passed = change is active.
- Host commit matches but UI still looks stale = likely cache/HMR/browser state, not deploy state.
