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

## Rule five: file against state you re-read, not state you remember

Before opening an issue whose whole point is that something is *not* done — a PR still open,
a branch still behind, a service still stopped — read that state at the moment you file, and
quote what you read. Live state moves while you write. TES-37 was filed at 15:49 asserting
that PR #208 was unmerged and `dev` sat at the pre-feature SHA; the PR merged at 15:51. The
issue then blocked, spawned a child, and the child pulled the company into work it could not
do — all from a premise that was already false.

Prefer **reopening the parent** over filing a sibling verification issue. A parent that was
closed early is one status change away from correct; a sibling adds a second issue that can
drift from the first, and both then need closing.

## Rule six: never make a boundary depend on parsing someone else's grammar

An acceptance criterion may not require predicting how a third-party program will parse its
own arguments, when that prediction decides which credential is minted, what permission is
held, or any other security boundary. Such a criterion has no finite set of tests: the other
program's grammar is per-command, version-dependent, and open-ended, so every round of review
can produce one more valid invocation that the prediction gets wrong, forever.

Scope by the role's permission template. That is a property of our own configuration, and it
is checkable.

TES-32 required the `gh` shim to resolve the repository a command addresses before minting a
token. Four review rounds, every finding real and reproduced against the installed client,
the resolver growing to 838 lines with per-command flag-arity tables pinned to
`AUDITED_GH_VERSION = "2.96.0"`. Cancelled, both PRs closed unmerged. What shipped instead
mints installation-wide and changes 12 lines.

**Reviewer:** a criterion of this shape is a defect of the contract. Return it to the CEO and
say so; do not request changes on the head. A head cannot be fixed into satisfying it.

## Rule seven: cancelling an issue means clearing its edges

Cancellation is not finished when the status changes. Every `blockedByIssueIds` edge pointing
at the cancelled issue must be cleared or replaced with an actionable unblock issue in the
same action.

The platform will not do it for you, deliberately: it raises a `harness_liveness_escalation`
and asks a manager to decide. TES-35 is that escalation, filed three minutes after TES-32 was
cancelled because TES-31 was still blocked by it.

## Rule eight: a contract change is a boundary, never a drift

Changing acceptance criteria, the Goal or the Non-goals while an issue is in flight is an
explicit boundary event. Silent continuation is how one issue accumulates several incompatible
architectures and unbounded review rounds: eight of them once, each finding real against a
different contract, ending in cancellation and a replacement issue.

Do one of three things, and never a fourth:

1. **Amend visibly.** Update the criteria in one revision and say in a comment what changed and
   why. Every review decision after that is made against the updated contract only; findings
   against the superseded one are void.
2. **Name what is approved.** An approval recorded near a contract change names the artifact
   identity it approves — the exact pull-request head SHA, or the document revision. "Approved"
   without an identity is what turns one changed contract into two disagreeing roles.
3. **Cancel and reopen.** When the change is large enough that the work so far is superseded,
   cancel and open the successor rather than carrying the old issue across the boundary. Clear
   its edges as rule seven requires.

If nobody can say which contract revision a review round judged, the issue is already past the
boundary: stop and apply one of the three before any further remediation.

Company-specific pipeline mechanics (branches, native review/approval stages, release)
live in `kira-dev-pipeline`; the boundary around the physical host lives in
`kira-host-boundary`; this skill owns only the shape of the contract itself.
