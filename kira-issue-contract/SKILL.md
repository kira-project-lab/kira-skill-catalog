---
name: kira-issue-contract
description: The issue template every executable Kira Lab issue follows — outcome title, checkbox acceptance criteria, hard delivery gate, and the rules that make an issue a contract. Use when creating, decomposing, or auditing any issue for agent execution.
---

# Issue contract

An issue is a contract, not a note. A worker executes it without guessing, a reviewer verifies it
without chat context, and an auditor tells "done" from "claimed done" months later.

## Template

```md
# <Title = the outcome, not the process>

## Why
<The problem that exists, and why this issue exists at all.>

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
- Prior decisions: <what is settled and not up for debate>

## Acceptance criteria
- [ ] <A checkable condition, not an adjective>
- [ ] <Every stated requirement, rewritten as a checkbox>

## Hard delivery gate
- [ ] Commit on the issue branch; branch pushed
- [ ] PR against `<base>`; URL posted in an issue comment
- [ ] Reviewer verified the diff, the criteria and the PR metadata against a named head SHA
- [ ] `done` is set only by the role that merges, after the merge is observed; the implementer
      stops at `in_review` and the reviewer's approval advances the stage rather than closing it
  <or, for operator work: "No PR is required because: …" + artifact path + rollback note>

## Verification
- [ ] <Exact command or manual check>

## Dependencies
- Blocked by: <…> · Blocks: <…> · Coordinate with: <parallel issues in the same files>

## Risks / edge cases
- [ ] <Risk and how to catch or mitigate it>

## Notes for worker
<Constraints, preferred patterns, what not to touch.>

## Reviewer instructions
- [ ] Check every acceptance-criteria checkbox and the delivery gate
- [ ] Required PR missing → request changes
```

**An issue whose delivery ends in a merge is created with its stages already on it** — a review stage
and an approval stage held by someone other than the assignee (`executionPolicy.stages`). An issue
filed without them cannot be merged from at all, because the merging role may only act while holding a
decided approval stage. Two orders each lost a cycle to this: five issues existed for no reason other
than to make a merge legal. The converse is equally binding: an issue whose completion falls entirely
inside its assignee's own duty carries **no** approval stage and needs no gate — publishing the
artifact completes it.

## The first three rules that make it work

1. **Everything that gates "done" is a checkbox.** Prose outside a checklist is context, not a
   requirement — an agent honours it by mood.
2. **One Goal; Non-goals are mandatory.** Without a single goal nobody can verify completion;
   without non-goals the worker expands scope.
3. **"Done" is not the implementer's call.** Push, PR and independent review are the completion
   contract; "changed locally" is the primary agent failure mode.

## Rule four: reference capabilities, never describe access

An issue names the standing capability a step uses and never spells out an access mechanism of its
own. Prodgate and dev-CI are active standing capabilities. The standing staging identity may remain
registered, but registration is not mutation authority. Staging mutation is unavailable until a
separate safe non-production guard exists. Record that blocked work and wait, with
no owner or missing-capability escalation and no direct-host workaround. Access mechanics written
into issue text go stale the moment the platform moves and then stall the program; every access
stall in one retrospective traced to exactly this. Except for that known staging refusal, a step
that seems to need a path no standing capability covers is a missing-capability escalation, not a
paragraph in the issue.

**Naming a capability obliges you to check the assignee holds it.** Capabilities are per role, and a
contract that asserts one without looking is a contract that stalls in flight rather than at planning
time. The GitHub role permission table is checked-in data, not folklore:
`ansible/roles/paperclip_team/files/gh-app-token`, the `ROLES` dict. Read the row for the role you are
about to assign. Two orders in one day named a capability their assignee did not hold — a tooling
deploy `prodgate` does not cover, and issue write on a role that carried no `issues` permission at all
— and both were found by the worker hitting the wall mid-run. Both were readable in advance.

**An issue you file is owned or it is parked, never neither.** Either it has an assignee and a next
action that assignee can take, or it says in one line who will pick it up and when. `backlog` with no
owner is how a chain stops without anyone noticing: nothing wakes, nothing fails, and the platform
eventually files a liveness escalation that a manager has to read. Three such issues appeared in two
hours on 2026-07-30, and one had already become an escalation before anyone looked.

## Rule five: file against state you re-read, not state you remember

Before opening an issue whose whole point is that something is *not* done — a PR still open, a
branch still behind, a service still stopped — read that state as you file, and quote what you
read. An issue was filed at 15:49 asserting a PR was unmerged; it merged at 15:51. The issue then
blocked, spawned a child, and the child pulled the company into work it could not do, all from a
premise that was already false.

Prefer **reopening the parent** over filing a sibling verification issue: a parent closed early is
one status change away from correct, while a sibling can drift from it and both then need closing.

## Rule six: never make a boundary depend on parsing someone else's grammar

An acceptance criterion may not require predicting how a third-party program parses its own
arguments, when that prediction decides which credential is minted or which permission is held.
Such a criterion has no finite set of tests: the other program's grammar is per-command,
version-dependent and open-ended, so every review round can produce one more valid invocation the
prediction gets wrong. Scope by the role's permission template instead — that is a property of our
own configuration, and it is checkable.

An order once required the `gh` shim to resolve the repository a command addresses before minting a
token. Four rounds, every finding real, the resolver growing per-command flag-arity tables pinned
to `AUDITED_GH_VERSION = "2.96.0"`, then cancellation with both PRs closed unmerged. What shipped
instead mints installation-wide and changes 12 lines.

**Reviewer:** a criterion of this shape is a defect of the contract. Return it and say so; do not
request changes on the head, because a head cannot be fixed into satisfying it.

## Rule seven: cancelling an issue means clearing its edges

Cancellation is not finished when the status changes. Every `blockedByIssueIds` edge pointing at the
cancelled issue must be cleared, or replaced with an actionable unblock issue, in the same action.
The platform will not tidy up for you: it raises a `harness_liveness_escalation` and asks a manager
to decide, and one was filed three minutes after a cancellation because another issue still hung
off it.

## Rule eight: a contract change is a boundary, never a drift

Changing the acceptance criteria, the Goal or the Non-goals while an issue is in flight is an
explicit boundary event. Silent continuation is how one issue accumulates several incompatible
architectures and unbounded rounds — eight of them once, each finding real against a different
contract, ending in cancellation and a replacement.

Do one of three things and never a fourth:

1. **Amend visibly.** Update the criteria in one revision and say in a comment what changed and
   why. Every decision after that is made against the updated contract; findings against the
   superseded one are void.
2. **Name what is approved.** An approval recorded near a contract change names the artifact
   identity it approves — the exact head SHA, or the document revision. "Approved" without an
   identity is what turns one changed contract into two disagreeing roles.
3. **Cancel and reopen.** When the change is large enough that the work so far is superseded,
   open the successor rather than carry the old issue across the boundary, and clear its edges as
   rule seven requires.

If nobody can say which contract revision a review round judged, the issue is already past the
boundary: stop and apply one of the three before any further remediation.

## Rule nine: criteria bind the deliverable, and only substance blocks

Acceptance criteria bind the **deliverable artifact** — the PR diff, the evidence comment, the
document revision — not the whole run transcript that produced it. The one transcript-wide
requirement a contract may impose is that no credential material is exposed. A criterion written
against "everything the run did" cannot be satisfied by an agent whose harness injects skill
reads and whose workflow includes orientation; it produces an unbounded series of real-but-empty
findings. LAB-28 spent four review rounds this way while the proven facts never changed after
round one.

Every criterion is one of two kinds, and the contract says which when it is not obvious:

- **Substance** — if this fails, the claim could be false or the change unsafe. Blocking.
- **Hygiene** — untidy but the claim still holds: extra read-only reads, surplus output lines,
  formatting. Advisory; it is recorded in the verdict and never blocks on its own.

A contract may only require what the runtime **and the pipeline** actually produce. Two instances of
the same class: a criterion demanding `PAPERCLIP_ISSUE_ID`, and a criterion demanding a counted CI
check on a branch whose workflow does not run there. Before writing a criterion that names an
artifact, confirm something produces it. The codex adapter's environment
carries `PAPERCLIP_AGENT_ID`, `PAPERCLIP_COMPANY_ID` and the API URLs — **`PAPERCLIP_ISSUE_ID`
is not guaranteed there** (it exists only on the workspace-runtime path), and LAB-32 failed
closed twice on a criterion that demanded it. Run and issue identity come from the wake payload
and the board API, never from an optional environment variable; a criterion that hinges on one
is a defect of the contract, same as rule six.

## Rule ten: three changes-requested rounds, then arbitration

The first and second changes-requested rounds on an issue are normal review. When a reviewer
would request changes a **third** time, the cycle stops instead: no further re-runs. Implementer
or reviewer posts a round summary — what each round found, what is proven, what is still
disputed — and escalates to the contract owner (the issue's author, usually the CTO) by
@mention, setting the issue `blocked`. The contract owner arbitrates: amend the contract
visibly (rule eight), void the finding with recorded rationale, or reassign. A dispute
involving the contract owner's own work goes to the CEO instead. To keep the count honest, a
changes-requested verdict names its round: "Round N".

## Rule eleven: the assignee may lawfully do what the gate demands

A task whose delivery requires writing to the repository is never assigned to a role forbidden to
write to it, and the same test covers every other capability a gate names — merging, releasing,
deciding a stage. Read the assignee's own charter against the gate you just wrote, before you file.

An assignee who cannot lawfully do the work does not fail loudly. It blocks, and a block from an
unlawful assignment looks exactly like an ordinary dependency, so nothing wakes and the issue waits
for a person to notice.

Recovery creates this state as readily as decomposition does, so check it after a reassignment and
not only when you file. LAB-104 on 2026-08-01 is the instance: the Engineer held it and was acting
lawfully under a gate reading "Engineer pushes a Conventional Commit branch… Engineer stops at
`in_review`", its three runs died on a local command that never returned, and recovery then moved
the issue to the CTO — who writes nothing into the repository at all. The unlawful assignment was
manufactured by the recovery path, and the issue has sat there since.

The remedy is reassignment. Not a permission expansion, and not the assignee doing it once as an
exception — the write boundary decides who is accountable for a diff, and one exception erases it.

Pipeline mechanics — branches, the native review and approval stages, release — live in
`kira-dev-pipeline`; the boundary around the physical host lives in `kira-host-boundary`. This
skill owns only the shape of the contract.

## Rule twelve: empty is a result only after inspection

An empty list proves absence only when the check completed. Every evidence-bearing result names
the command or procedure, timestamp, target or SHA, completion state, and observed result. Report
one of `not inspected`, `inspected, empty`, or `inspected, non-empty`; never collapse the first two.
An interrupted, ambiguous, unauthorized, or failed read is `not inspected`, even when the local
accumulator still contains `[]`. Machine-readable evidence uses
`kira-platform/inspection-evidence/v1` and must pass `python3 tools/evidence_contract.py lint`.
