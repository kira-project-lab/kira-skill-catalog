# VM beta Codex auth latency trace

Use this when Maxim asks to compare VM beta speed with the home PC using `openai-codex / gpt-5.5`, or when VM Codex looks “slow” but produces empty output.

## Key lesson

Do not treat VM `openai-codex / gpt-5.5` timing as model latency until the tenant has a valid Codex/ChatGPT auth session. A VM tenant can have `.codex/config.toml` and still fail because `.codex/auth.json` is missing.

Failure signature from 2026-06-29:

```text
provider=openai-codex
base_url=https://chatgpt.com/backend-api/codex
model=gpt-5.5
HTTP 403 — HTML error page
PermissionDeniedError
Non-retryable client error
```

The bridge may mark the run `complete` quickly with no assistant output; that is a fast authentication failure, not a successful fast model response.

## Compare PC vs VM safely

Check only presence/metadata of credential files; do not print secrets.

Typical PC profile shape:

```text
~/.hermes/profiles/kira/home/.codex/config.toml   present
~/.hermes/profiles/kira/home/.codex/auth.json     symlink/present
```

Typical VM tenant path:

```text
/data/kira/users/<uid>/assistants/kira/hermes-root/home/.codex/config.toml
/data/kira/users/<uid>/assistants/kira/hermes-root/home/.codex/auth.json
```

If VM `auth.json` is missing, stop before latency conclusions and report `Codex auth missing for tenant`.

## Timing pattern from 2026-06-29

Same prompts and forced provider/model override:

| Surface | Prompt | Start ack | First text | Total | Result |
|---|---|---:|---:|---:|---|
| PC `kira` | `готово` | ~7.5s | ~13.2s | ~13.6s | success |
| PC `kira` | `Привет...` | ~7.6s | ~43.4s | ~46.2s | success |
| VM `usr_polina` | `готово` | ~7.7s | none | ~8.3s | empty output + 403 in logs |
| VM `usr_polina` | `Привет...` | ~7.7s | none | ~8.3s | empty output + 403 in logs |

Shared `context_estimate` overhead was ~7.7–7.8s on both surfaces, so the VM-specific Codex blocker was auth, not basic bridge or network latency.

## Safe fix options

Do not copy the operator PC `auth.json` into a VM tenant without explicit approval; it is a credential/session secret.

Approved paths:

1. create a separate Codex/ChatGPT auth session for the VM tenant Linux user; or
2. install an operator-approved Codex auth secret into the tenant root with `0600 <tenant-user>:<tenant-user>`, then restart the tenant service and rerun the trace.

After auth is fixed, rerun the same bridge trace before recommending provider/model changes.
