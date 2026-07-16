# Codex OAuth in Hermes Web UI global coding-agent runs

Use when Codex works in one shell/CLI context but fails from Hermes Web UI with OAuth errors such as:

- `Your access token could not be refreshed because your refresh token was already used`
- `refresh_token_reused`
- `Provided authentication token is expired`
- `codex exec exited` with code `1`

## Root cause pattern

Codex has multiple token/config stores:

- user CLI default: `~/.codex/auth.json` and `~/.codex/config.toml`
- Hermes profile home: `<profile>/home/.codex/...`
- Web UI global coding-agent scope: `<HERMES_WEB_UI_HOME>/coding-agent/model/<profile>/global/codex/...`
- Hermes profile auth: `<hermes-root>/profiles/<profile>/auth.json` provider `openai-codex`

A stale `~/.codex/auth.json` can contain an expired access token plus a refresh token that has already been consumed, while the selected Hermes profile still has fresher `openai-codex` OAuth tokens. In that state, direct CLI checks may differ depending on `HOME` / `CODEX_HOME`.

## Durable fix pattern

For `Codex + Global config`, do not let Web UI implicitly use ambient `~/.codex`. Prepare a profile-backed `CODEX_HOME` and launch Codex with it:

```text
<HERMES_WEB_UI_HOME>/coding-agent/model/<profile>/global/codex
```

Write:

- `auth.json` from selected Hermes profile `auth.json` → `providers.openai-codex.tokens`
- `config.toml` with a known ChatGPT-account-compatible default model, currently:

```toml
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
```

When syncing auth, avoid overwriting an existing scoped `auth.json` if it already has an equal-or-newer JWT expiry than the profile token. Otherwise a stale profile token can roll back a refreshed scoped token.

## Verification probes

After deploy/restart:

```bash
CODEX_HOME=<HERMES_WEB_UI_HOME>/coding-agent/model/<profile>/global/codex \
  codex exec --json --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox \
  --cd /tmp 'say exactly ok'
```

Expected:

- exit code `0`
- `turn.completed`
- no `refresh_token_reused`

If auth succeeds but model fails:

- `gpt-5.3-codex` may be unsupported for ChatGPT accounts.
- `gpt-5.5` may require a newer Codex CLI.
- Known working choices from this incident: `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.3-codex-spark`.

## UI/server error reporting contract

For coding-agent child processes, keep stderr user-visible:

- buffer sanitized stderr from `codex exec`
- include it in `run.failed.error.message`
- client must normalize object errors (`message`, `error`, or JSON) instead of rendering `Error: [object Object]`

This separates the actual child-process failure from UI serialization bugs.
