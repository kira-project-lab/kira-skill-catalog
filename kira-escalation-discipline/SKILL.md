---
name: kira-escalation-discipline
description: Kira Lab escalation boundaries for owner confirmations, structured product questions, and conditional Kira consultation. Use when a missing decision or protected action blocks delivery.
---

# Escalation discipline

Escalation is for a decision or protected action that cannot be resolved from
the assigned scope and available evidence. It is not a status-reporting path.

## Owner confirmations

Use the **approval / request_confirmation mechanisms** (never assignment, never
mentions) when the action needs the owner's signature:

- spending money, deleting data, changing production infrastructure,
  outbound communications, irreversible operations;
- any instruction/skill mutation gated by a confirmation (Reflection Coach
  pattern).

**Staging is an autonomous zone (ADR 0043): never open an owner gate for an
action confined to staging** — deploys, converges, restarts, the standing
keygate identity. The owner gates above are the complete list; "it touches
infrastructure" is not a gate if the infrastructure is staging. KIR-132 spent
hours of the CEO-1 rollout waiting on a confirmation this rule now answers.

The gate itself reaches the owner automatically. Bind it to the exact
resource/action; include the exact diff or command.

## Missing product decisions

If delivery requires an owner choice that the brief does not contain, use the
smallest structured `ask_user_questions` interaction on the direction issue.
Include:

1. **Context** — one paragraph: what was being done, what happened.
2. **Options** — 2–4, each with a one-line trade-off.
3. **Recommendation** — exactly one, with why.
4. **Impact** — what cannot proceed without the answer.

Do not use `request_confirmation` for ordinary plans, architecture choices, or
reversible implementation details. Make those decisions as Technical CEO when
the issue and repository provide enough evidence.

## Kira consultation

Use Kira only when the task explicitly asks for Kira or requires Kira-owned
knowledge or memory. Follow `kira-ask-kira`. Do not route ordinary questions,
technical research, planning, or prioritization through Kira by default.

## Hard rules

- **Never** set `assigneeUserId` to the board user yourself.
- Do not @mention the owner in comments; use a structured interaction or gate.
- `blocked` status is a planning tool, not a pager: it alerts nobody. Set it
  freely with a clear reason (dependency, missing input, who unblocks).
- Killing issues follows the kill order: cancel -> verify terminal ->
  hide. Never hide a non-terminal issue (a hidden live issue is an
  invisible zombie that keeps running).
- One escalation per decision. Wait for its continuation event; do not poll or
  create duplicate interactions on silence.

## Never escalate at all

- Anything the dev pipeline rules or roster routing already decide.
- Status updates, progress, FYI — the board and merge cards show them.
- Questions answerable from the repo, the issue history, authoritative docs,
  or a bounded engineer research task.
