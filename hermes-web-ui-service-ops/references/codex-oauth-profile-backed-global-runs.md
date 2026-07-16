# Codex OAuth profile-backed global runs

Use this when a Hermes Web UI coding-agent session runs `Codex + Global config` and fails with OAuth/token refresh errors even though a user thinks Codex CLI works elsewhere.

## Symptom

Typical user-visible error after stderr is surfaced:

```text
Your access token could not be refreshed because your refresh token was already used. Please log out and sign in again.
```

Codex may emit JSON events like:

```json
{"type":"error","message":"Your access token could not be refreshed because your refresh token was already used. Please log out and sign in again."}
{"type":"turn.failed","error":{"message":"Your access token could not be refreshed because your refresh token was already used. Please log out and sign in again."}}
```

## Root cause pattern

Do not assume `global` Codex uses the same auth store as the operator's terminal. Check the effective process environment and token stores:

- normal Codex CLI usually reads `${HOME}/.codex/auth.json` unless `CODEX_HOME` is set;
- Hermes Web UI live-dev/prod services may run with different `HOME`, `HERMES_HOME`, profile selection, and state dirs;
- Hermes profile auth may hold fresher OpenAI Codex OAuth tokens in `<hermes-profile>/auth.json` under `providers.openai-codex.tokens`;
- an older `.codex/auth.json` can contain an expired access token plus a refresh token that OpenAI has already rotated/invalidated.

A reused refresh token is not a model error and not a serialization bug. It means the Codex process is reading stale OAuth state.

## Correct fix shape

For `Codex + Global config` launched from Hermes Web UI, prefer a profile-backed `CODEX_HOME` instead of relying on ambient `${HOME}/.codex`:

```text
<web-ui-home>/coding-agent/model/<profile>/global/codex/auth.json
```

Populate that `auth.json` from the selected Hermes profile's `auth.json`:

```json
{
  "auth_mode": "chatgpt",
  "OPENAI_API_KEY": null,
  "tokens": {
    "access_token": "...",
    "refresh_token": "...",
    "id_token": "...",
    "account_id": "..."
  },
  "last_refresh": "..."
}
```

Then launch Codex with:

```text
CODEX_HOME=<web-ui-home>/coding-agent/model/<profile>/global/codex
```

Important guardrail: do not overwrite a profile-backed Codex auth file with older profile tokens if the existing `tokens.access_token` expires later than the source profile token. Compare JWT `exp` when both are JWTs.

## Verification probes

1. Confirm token source and expiry without printing secrets:
   - list token keys and JWT `exp` only;
   - compare `<profile>/auth.json` vs the `CODEX_HOME/auth.json` that Web UI will launch.
2. Run a narrow Codex exec with explicit `CODEX_HOME`:

```bash
CODEX_HOME=<profile-backed-codex-home> \
  codex exec --json --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox \
  --cd /tmp 'say ok'
```

3. If OAuth refresh succeeds but Codex still fails, treat the next error separately.

## Common next-layer model errors

With ChatGPT-account OAuth, some model names are not accepted by a given Codex CLI version/account:

- `gpt-5.3-codex` can fail with: model is not supported when using Codex with a ChatGPT account.
- `gpt-5.5` can fail with: requires a newer Codex CLI.
- Known working examples in this session: `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.3-codex-spark`.

Do not conflate these with OAuth. Once token refresh is fixed, model compatibility is a separate provider/model selection issue.
