# Claude subscription backend research notes

Use these notes when a user asks whether Hermes can use Claude as a backend through a Claude Pro/Max subscription, especially after a 400/429 error.

## Current practical verdict from the July 2026 research pass

No stable merged first-class Claude subscription backend was found in Hermes main at the time of this pass. Community work exists, but the main options were open/draft or not fully end-to-end verified.

The user-visible answer should separate:

- **Current stable path**: use `anthropic` with an API key or documented extra-usage-backed Anthropic OAuth, or use another supported provider such as OpenRouter/Nous Portal.
- **Experimental community paths**: test a PR/branch in an isolated checkout, not in the live Kira install.
- **Not equivalent**: request-shape fixes for OAuth billing classifiers are not the same as a real Claude CLI/Agent SDK backend.

## Issue / PR map checked

- `NousResearch/hermes-agent#52362` — duplicate feature request for Claude SDK backend. Duplicate of `#25267`.
- `#25267` — canonical feature request: Claude Agent SDK provider with subscription OAuth.
- `hashbender/hermes-agent#352` mirrors `NousResearch/hermes-agent#56413`.
- `#56413` — draft Claude Agent SDK backend using Python `claude-agent-sdk`; explicitly says real Claude-subscription turn through `claude` CLI was not verified.
- `#12229` — `claude-code-acp` provider; broad ACP/sandbox/MCP approach, describes live dogfooding and many tests, but was still open in the checked state.
- `#31796` — `claude-cli` provider through an external OpenAI-compatible HTTP shim (`claude-bridge`); open, depends on separate shim/service.
- `#38588` — `/claude-runtime` subprocess bridge through raw `claude -p`; open, E2E pending valid subscription.
- `#26634` — RFC/draft CLI shim for shelling out to claude/codex/gemini CLIs via OAuth.

Related OAuth/billing fixes and reports:

- `#40014` — closed by maintainer as expected/documented behavior; reported `out of extra usage` / third-party billing lane with Claude Code OAuth.
- `#46675` — request-shape issue: single-underscore `mcp_` tool names caused OAuth requests to be classified as third-party/extra-usage.
- `#47723` — merged fix for the `mcp_`/`mcp__` tool-name classifier issue.
- `#47738` — open fix for relocating OAuth system prompt to first user message; aimed at content-based classifier problems.
- `#53212` / `#53213` — root-cause/mitigation around app-specific system prompt content and auxiliary OAuth fallback; not the same as a backend provider.
- `#45250`, `#45254`, `#46251`, `#47333` — stale Anthropic OAuth token endpoint/login 404 fixes around `platform.claude.com` vs `console.anthropic.com`.

## Error interpretation

If the error says:

```text
HTTP 400: You're out of extra usage. Add more at claude.ai/settings/usage and keep going.
```

or:

```text
Third-party apps now draw from your extra usage, not your plan limits.
```

then do **not** frame it as only a local misconfiguration. Current Hermes docs may treat the `anthropic` OAuth path as requiring Claude Max extra usage credits rather than base subscription allowance. Check live docs before finalizing.

If the error is OAuth login `404`, check whether the local install includes the token-endpoint fallback to `https://platform.claude.com/v1/oauth/token`.

If the error appears only on tool-bearing requests, inspect whether the local `anthropic_adapter.py` has the merged `mcp__` handling from `#47723`.

## Local-install comparison pattern

When the user asks about their own Hermes install, compare upstream research to the live install:

1. `hermes --version` and source commit.
2. Active profile `config.yaml` model provider/default model.
3. `hermes auth list anthropic` redacted to identify API key vs OAuth/Claude Code source.
4. Source markers in the live checkout:
   - `mcp__` in `agent/anthropic_adapter.py` for `#47723`-class fix.
   - `platform.claude.com/v1/oauth/token` for endpoint fallback.
   - `HERMES_OAUTH_SYSTEM_BUDGET` or `<system_context>` relocation for system-prompt classifier mitigations.
   - `agent/claude_agent_sdk_adapter.py`, `claude-code-acp`, or `claude-cli` provider/plugin files for backend-provider PRs.

Do not use environment-dependent absence (missing repo, missing binary) as durable knowledge. Treat it as live-state evidence only.

## Recommended answer shape

```text
Short verdict: <stable solution exists / no stable merged solution / local install is behind / policy-limited>.

What I found:
- <canonical issue and state>
- <relevant merged fixes>
- <open backend PRs and their testing status>

For your error:
- <classification based on exact error text>
- <whether current config can solve it>

Best next step:
- <update / switch provider / use API key / test branch in isolated worktree>
```

Keep the answer compact. The user usually wants whether a solution exists and what to do now, not a full GitHub archaeology dump.
