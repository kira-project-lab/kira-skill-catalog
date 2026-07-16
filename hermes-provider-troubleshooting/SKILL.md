---
name: hermes-provider-troubleshooting
description: "Troubleshoot Hermes Agent model provider, auth, routing, and billing failures. Use when Maxim asks why a Hermes provider/model returns 400/401/429, whether a provider path exists, or whether community PRs/issues already solve a Hermes backend problem. Complements the protected hermes-agent skill and official docs."
version: 1.0.0
author: Kira
license: MIT
metadata:
  hermes:
    tags: [hermes, providers, auth, billing, troubleshooting, github-research]
    related_skills: [hermes-agent, github-workflows, official-document-lookup]
---

# Hermes Provider Troubleshooting

Use this skill for Hermes Agent provider/model failures and provider-path research: Anthropic/Claude, OpenRouter, Nous Portal, Codex, Copilot, custom endpoints, OAuth, credential pools, and provider billing behavior.

The protected `hermes-agent` skill and live Hermes docs remain authoritative for current commands and supported configuration. This skill captures the operational research pattern and recurring provider pitfalls.

## Core workflow

1. **Classify the failure by surface and error.**
   - Provider/model configured in `config.yaml` or CLI flags.
   - Auth source: API key, OAuth credential pool, local CLI credential, custom endpoint key.
   - Error class: 400 request-shape/billing-policy, 401/403 auth, 404 stale endpoint, 429 quota/rate/billing, transport/local endpoint failure.

2. **Check official docs first.**
   - Use live Hermes docs for provider support and current policy language.
   - Treat GitHub PRs/issues as evidence of in-flight work, not as stable support.
   - Separate merged fixes from open drafts and abandoned/duplicate reports.

3. **Read the canonical issue chain, not only the linked PR.**
   - Inspect the user-provided issue/PR.
   - Follow cross-links to canonical issues, related PRs, duplicates, and maintainer comments.
   - For GitHub, capture: state, merged status, testing status, branch scope, and whether the PR changes docs, provider registration, runtime behavior, or only tests.

4. **Compare against the local live installation when asked about the user’s setup.**
   - Check Hermes version, live source checkout, active profile config, provider/model, and credential type.
   - Look for specific fix markers in source only after identifying the upstream fix being tested.
   - Do not claim a solution exists locally just because a PR exists upstream.

5. **State the practical verdict.**
   - `supported now`, `merged but user is behind`, `open/draft/untested`, `policy-limited by design`, or `workaround only`.
   - Name the least risky next action: update, switch provider, use API key, test in isolated worktree, or wait.

## Claude subscription / Anthropic OAuth pattern

For Claude subscription questions, keep three lanes separate:

- **Anthropic API key**: standard pay-per-token API billing.
- **Hermes `anthropic` OAuth / Claude Code credentials**: may use Anthropic’s Claude Code credential path but can still require Max extra-usage credits depending on current Hermes/docs behavior; do not assume it consumes base Pro/Max plan allowance.
- **Local Claude CLI / Agent SDK / ACP backend**: community in-flight approaches that try to route through `claude`/Claude Code/Agent SDK as the backend. Treat open PRs as experimental until merged and live-tested.

When the user reports a 400/429 around Claude OAuth, distinguish:

- stale OAuth endpoint/login failure;
- request-shape/tool-name classifier failure;
- system-prompt/request-classifier failure;
- provider policy/billing behavior that Hermes documents as expected;
- missing extra-usage credits.

See `references/claude-subscription-backend-research.md` for the current issue/PR map and answer pattern.

## Pitfalls

- Do not tell the user “use Claude subscription with Hermes” from a community PR title alone. Check merged state and testing notes.
- Do not equate `claude_code oauth` in Hermes with base Claude Pro/Max subscription allowance. Check current docs and exact error text.
- Do not apply a request-shape patch as if it were a first-class provider/backend. A billing classifier workaround and a real CLI/SDK backend are different solutions.
- Do not patch the live Hermes install with large provider PRs unless the user explicitly asks; recommend isolated worktree/venv testing first.
- Do not save PR numbers to memory. Keep incident maps in `references/`, not global memory.
