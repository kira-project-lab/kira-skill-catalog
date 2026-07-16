# Kira control-plane improvement plan decisions

Session reference from 2026-07-10. This is planning context, not authorization to change the live profile.

## Goal

Reduce recurring prompt, skill, tool-schema, and loop overhead while preserving Kira's quality, natural style, judgment, capabilities, safety, and completion reliability.

## Selected architecture

Use a self-maintaining federated context graph:

```text
Thin SOUL
  -> compact USER with global routes
  -> on-demand domain and maintenance skills
  -> project-local AGENTS/HERMES/docs
  -> canonical repositories and live tools
```

Responsibility split:

- `SOUL.md`: identity, relationship posture, universal behavior, epistemic and safety boundaries.
- `USER.md`: stable preferences and high-degree routes, not an encyclopedic dossier.
- `GOALS.md`: canonical active goal hierarchy.
- `MEMORY.md` and Agentmemory: continuity and observations, not critical operational truth.
- `kira-profile-culture`: profile-file ownership, deduplication, memory promotion, validation, and review.
- `project-culture`: repository evidence gathering, initialization, ADRs, diff-based wrap-up, and documentation maintenance.
- domain skills: topology, terminology, hard constraints, and routes to canonical sources.
- project-local files: actual architecture, commands, decisions, conventions, and current state.

Defer a centralized typed registry until measured duplication justifies it.

## Locked decisions

- Target strong GPT-5.6-class models; remove weak-model reasoning scaffolding rather than maintaining a universal dual-mode core.
- Improve the full control plane: core context, skills, tool/MCP surface, runtime settings, and project culture.
- Build a temporary isolated `kira-lean` profile and compare it with live Kira before promotion.
- Project culture starts as a skill plus one bounded `pre_verify` nudge. It inspects the real diff and updates docs or records `none`; it does not autonomously rewrite semantic documentation.
- Reversible in-scope local work may proceed automatically. Ask for external, destructive, public, production, financial, or security-sensitive actions.
- First domain capsules: `kira-operations`, `orangehack`, and `personal-infrastructure`.
- Promotion requires no material quality, safety, style, or capability regression. Token or latency savings are accepted only inside that boundary.

## Non-regression suite

Use a broad 12-task suite covering:

1. Kira/Hermes operations;
2. OrangeHack work;
3. infrastructure and devices;
4. evidence-based research;
5. expert judgment;
6. implementation planning;
7. long-running execution;
8. browser work;
9. natural writing and editing;
10. health coordination or research;
11. study support;
12. personal productivity.

Measure task success, completeness, corrections, safety, style fidelity, exposed tool/schema size, skill loads and bytes, API/tool loops, input/output/cache/reasoning tokens, latency, and cost.

## Prompting evidence incorporated

Official OpenAI GPT-5.6 guidance supports:

- starting with the smallest prompt and tool set that passes evals;
- outcome-first contracts with success, evidence, permission, validation, and stop rules;
- removing repeated rules, generic reasoning/brevity scaffolding, irrelevant examples, and unrelated tools;
- preserving current reasoning effort as a baseline, then testing one level lower;
- changing prompt, tools, reasoning, and runtime separately so effects remain attributable;
- evaluating the final user-visible result rather than token savings alone.

Use the local `prompt-engineering` skill and its `references/openai-gpt-5.6-sol.md` dated fallback for the detailed workflow.

## Remaining read-only closure work

Before finalizing Plan v1.0:

1. Map `/data/kira/profiles/kira` to the durable GitOps repository and autocommit/push mechanism.
2. Verify `kira-lean` clone isolation for gateways, cron, delivery, credentials, sessions, and mutable state.
3. Determine whether broad runtime skill-loading language can be overridden at profile level; patch the Hermes fork only if necessary.
4. Measure tool/MCP schema bytes and compare allowlists against Tool Search on representative tasks.
5. Verify exact `pre_verify` payload, one-nudge termination, and irrelevant-diff filtering.
6. Reproduce the baseline in fresh sessions.
7. Produce a line-by-line SOUL/USER/MEMORY/GOALS/HERMES migration matrix.
8. Produce candidate configuration experiments, the exact A/B rubric, rollout, and rollback runbooks.

## Rollout order

1. Establish rollback and GitOps control.
2. Create isolated `kira-lean`.
3. Freeze and reproduce the baseline.
4. Redesign core context.
5. Add profile-culture and selected domain capsules.
6. Narrow skill routing and library exposure.
7. Narrow tool/MCP exposure.
8. Tune runtime settings one variable at a time.
9. Add project-culture and its bounded hook.
10. Run the full A/B suite.
11. Promote proven slices to live Kira with observation and rollback gates.
