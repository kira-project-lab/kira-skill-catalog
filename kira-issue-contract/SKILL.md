---
name: kira-issue-contract
description: The issue template every executable Kira Lab issue follows — outcome title, checkbox acceptance criteria, hard delivery gate, and the three rules that make an issue a contract. Use when creating, decomposing, or auditing any issue for agent execution.
---

# Issue contract

An issue is a contract, not a note. A worker must be able to execute it without guessing,
a reviewer must be able to verify it without chat context, and an auditor must be able to
tell "done" from "claimed done" months later.

## Template

```md
# <Title = the outcome, not the process>

## Why
<The problem that exists and why this issue exists at all.>

## Goal
<One independently valuable result.>

## Scope
- [ ] <Included work, as concrete items>

## Non-goals
- [ ] <What this issue deliberately does NOT touch>

## Context
- Repo: `<owner/repo>`, base branch: `<branch>`
- Paths: `<path>` — <why it matters>
- Links: ADRs / PRs / docs — <why to read them>
- Prior decisions: <what is already decided and not up for debate>

## Acceptance criteria
- [ ] <A checkable condition, not an adjective>
- [ ] <Every stated requirement, rewritten as a checkbox>

## Hard delivery gate
- [ ] Commit on the issue branch; branch pushed
- [ ] PR against `<base>`; URL posted in an issue comment
- [ ] Reviewer verified the diff, the criteria, and the PR metadata
- [ ] `done` is set only by the Reviewer; the implementer stops at `in_review`
  <or, for operator work: "No PR is required because: …" + artifact path + rollback note>

## Verification
- [ ] <Exact command or manual check>

## Dependencies
- Blocked by: <…> · Blocks: <…> · Coordinate with: <parallel issues in the same files>

## Risks / edge cases
- [ ] <Risk and how to catch/mitigate it>

## Notes for worker
<Constraints, preferred patterns, what not to touch.>

## Reviewer instructions
- [ ] Check every acceptance-criteria checkbox and the delivery gate
- [ ] Required PR missing → request changes
```

## The three rules that make it work

1. **Everything that gates "done" is a checkbox.** Prose outside checklists is context, not
   a requirement — an agent will honor it only by mood.
2. **One Goal; Non-goals are mandatory.** Without non-goals the worker expands scope;
   without a single goal nobody can verify completion.
3. **"Done" is not the implementer's call.** Push + PR + independent review is the
   completion contract; "code changed locally" is the primary agent failure mode.

## Rule four: reference capabilities, never describe access

An issue names the standing capability a step uses — **standing staging key** (keygate),
**prodgate** (prod converge from main), **dev-CI** — and never spells out an access
mechanism of its own. Access mechanics written into issue text go stale the moment the
platform evolves and then stall the program (every access stall in the KIR-118
retrospective traced to exactly this). If a step seems to need an access path no standing
capability covers, that is a missing-capability escalation, not a paragraph in the issue.

## Rule five: a contract change is a boundary, never a drift

Changing acceptance criteria (or Goal / Non-goals) while the issue is in flight is an
explicit boundary event, not a silent continuation — silent drift is how one issue
accumulates several incompatible architectures and unbounded review rounds (KIR-299
retrospective). When the contract changes:

1. **Amend visibly.** Update the issue's criteria checkboxes (or the `plan`/decision
   document) in one revision, and say in a comment what changed and why. Every review
   decision after the change is made **against the updated contract only**; findings
   against the superseded contract are void.
2. **Name what is approved.** Any approval recorded near a contract change must name the
   exact artifact it approves — PR head SHA or document key + revision. "Approved" without
   an artifact identity is not an approval.
3. **Or cancel and reopen.** When the change invalidates the implementation approach (not
   just details), cancel the issue and open a fresh one with a new branch and PR; the old
   branch is a historical artifact and is never reused.

If nobody can say which contract revision a review round was judged against, the issue is
already past the boundary — stop and apply one of the three moves before any further
remediation.

Company-specific pipeline mechanics (branches, native review/approval stages, release)
live in `kira-dev-pipeline`; this skill owns only the shape of the contract itself.
