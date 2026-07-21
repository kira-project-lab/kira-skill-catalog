---
name: kira-dev-pipeline
description: How Kira Lab ships code — decomposition, branches, the native review/approval stages, and release. Use when planning, decomposing, implementing, reviewing or releasing any engineering work. The Paperclip skill has the platform mechanics; this has only what is specific to this company.
---

# Kira Lab dev pipeline

The **Paperclip skill** is the manual for the platform: heartbeat, checkout, status,
delegation, execution stages. Read it there. This skill adds only what is ours.

Vocabulary: a **direction** is a long-lived stream owned by the CEO and mapped to a GitHub
repository. A **feature** is one shippable unit inside it: one engineer, one branch, one
worktree, one PR.

## How work travels

Native execution stages carry a feature — nobody routes it by hand:

- The CEO creates the feature issue, assigns the engineer, and puts the review path on the
  issue itself (`executionPolicy.stages`): a **review** stage with the Reviewer, then an
  **approval** stage with the Release Engineer.
- **The approval participant must never be the issue's implementer.** Paperclip forbids
  approving your own work, so if the assignee *is* the Release Engineer — an operator issue he
  runs himself: a staging/prod converge, a promotion train, an infra change — the approval
  stage goes to the **CEO** instead. A self-approval stage fails the review→approval transition
  with HTTP 422 "no eligible approval participant" and strands the issue (KIR-120 lost ~30m to
  exactly this; the same trap waits on every RE-executed issue, e.g. the promotion train).
- The engineer finishes and moves the issue to `in_review`. Paperclip reassigns it to the
  stage participant and wakes them.
- The Reviewer decides. Approve advances the issue to the next stage — the Release Engineer.
  Request-changes returns it to the engineer. Only the active participant can decide.
- The Release Engineer merges, then closes the feature.

Never model review as a child issue, a mention grant, or a comment asking someone to pick the
work up. Those split the audit trail away from the issue being reviewed and loosen who may
decide. The stage keeps the gate, the authority, the return path and the wake on the work.

## Decomposition (CEO)

- Features whose file sets overlap are **sequential**, never parallel. Say which files each
  feature owns, in a table, before delegating.
- One feature → one engineer. A follow-up to in-flight work goes to the same engineer on the
  same branch.
- Branch `feat/<KIR-N>-<slug>` in a fresh worktree.

## Judge against a fresh base (Reviewer)

`git fetch origin` before you compare anything, and diff against `origin/main` — never a
local ref. Merges land while you review: a local `main` goes stale in minutes, and a
three-dot diff taken against it will show you other people's merged commits as if they were
this PR's scope. Exam #9 lost a review round to exactly that — a blocking finding that
evaporated on a fresh fetch, same head, no code changed.

## The verdict (Reviewer)

The verdict is your **native stage decision** — approve or request-changes on the review
stage itself, never a specially-formatted comment. The platform records who decided, when,
and on which issue; there is no parser and no verdict format to get wrong. In the decision
comment, name the PR and the **head SHA you reviewed** in prose: the Release Engineer
compares it against the live head before merging.

## Grounded verdicts

A verdict — either outcome — is valid only when the relevant checks were **executed** and
their meaningful output is quoted in the decision, or the decision states the precise
reason they could not run plus the substitute evidence relied on. Reasoning about the diff
alone is not review: ungrounded critique neither proves a finding nor earns an approval,
and it is the fuel of repeated-round loops. Exit codes alone are not evidence; quote the
output that matters.

## Anti-loop review rule

A finding is the same finding when the same acceptance criterion or invariant remains
unproved, even if the symptoms or attempted patches change. Give each repeated finding a
stable finding key and state its occurrence number in the review decision. One occurrence
is one native review decision in which that finding key remains unproved; remediation
attempts and diagnosis or advisory children do not increment the count.

1. **First occurrence → normal remediation.** Request changes through the native review
   stage and return the same feature, Engineer, branch and PR for correction.
2. **Second occurrence → focused diagnosis.** Record `request-changes` on the native review
   stage, create an analysis-only diagnosis child and block the feature on it. The child
   cannot approve or reject the feature and does not replace or advance its native review
   stage. Do not write implementation code in that child: establish the root cause, trace
   the real execution path, produce a failing proof and record one binding fix contract.
   Use planning mode only when resolving the finding requires a new architecture decision.
   After the diagnosis is incorporated, unblock the feature, remediate on the same PR and
   submit the corrected head to the native review stage again.
3. **Third occurrence → Kira operational escalation.** When the same finding key remains
   unproved in the third native review decision, record `request-changes`, keep the feature
   blocked and create an advisory child for Kira following `kira-ask-kira`. Ask one concrete
   disposition question with full context and explicit stop, split, reassign or re-plan
   options. Kira advises; the accountable pipeline owner records the disposition. A fourth
   tactical remediation is forbidden until that disposition is recorded.

## dev is always green (ADR 0043)

A CI timer sweeps every `tools/test_*.py` + `tools/selftest_*.py` after each merge to
`dev` and files an **urgent** hotfix issue when anything is red. That issue is a
drop-everything lane: branch from fresh `origin/dev`, fix the actual defect (the test OR
the code — whichever is wrong), PR to `dev`. Never let a promotion train be the thing
that discovers red tests (KIR-147/148 cost the KIR-122 train ~1.5h exactly this way).
Corollary for every PR: if your change alters a contract a selftest asserts, update the
selftest in the same PR — the sweep treats your merge as the offending HEAD.

## Staging (Release Engineer)

Staging is an autonomous zone (ADR 0043): no owner gate for anything confined to it.
The deploy identity is the **standing** keygate key (`--standing`, tag `kg-standing-re`,
targets `staging-hop`/`staging-core`) — install once, reuse across issues, no per-task
keygen/install/remove ceremony. If `keygate check` shows it missing, reinstall and carry on.

## Prod converge (Release Engineer)

The decision about prod is the train merge into `main`; the converge after it is mechanics
you run yourself through **prodgate** (ADR 0044) — never by asking the owner, never by
inventing a path:

```sh
prodgate converge --target snapshot     # rollback point first
prodgate converge --target cognition    # or: deploy
```

The reply's `main_sha` is your deployed-SHA evidence. Refusals are terminal answers
(unknown target, converge in flight, 15-min cooldown) — wait, don't work around. The
allowlist is exactly `cognition`/`deploy`/`snapshot`; infra roles stay with the operator.

## Standing capabilities — reference them, never reinvent access

Issues and plans name the capability they use and NOTHING more: **standing staging key**
(keygate), **prodgate** (prod converge), **dev-CI** (red dev files its own hotfix issue).
An issue that describes an access mechanism of its own — an ephemeral key ritual, an owner
gate for staging, a manual prod path — is stale by definition: fixing the text is part of
picking the issue up, and for the Reviewer a stale access description is a **blocking
finding**.

## The merge (Release Engineer)

- Merge **only while you hold the approval stage** and it is decided approve — the stage
  decision is the gate; there is no separate merge-gate parser.
- Before `gh pr merge --squash`, compare the PR's live head against the SHA the Reviewer
  named in the review decision. A push after review invalidates the review: send the issue
  back through the review stage, never merge a head nobody reviewed.
- Never force-push, never push to `main`. Hooks enforce this; they are not obstacles.
- Release: everything claimed is merged, `main` is green, changelog/README/versions agree →
  tag → GitHub release → report the URL on the direction issue.
- A broken `main` is yours: revert first via a hotfix PR; fix forward only for a proven
  one-liner.

## Owner escalation

`blocked` pages nobody — it is a planning status, not a pager. What may reach the owner, and
how, is `kira-escalation-discipline`. Engineers and the Reviewer never open owner gates.
