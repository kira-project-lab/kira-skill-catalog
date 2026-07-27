---
name: kira-dev-pipeline
description: How this company ships code — decomposition, branches, the native review/approval stages, and release. Use when planning, decomposing, implementing, reviewing or releasing any engineering work. The Paperclip skill has the platform mechanics; this has only what is specific to the company.
---

# Dev pipeline

The **Paperclip skill** is the manual for the platform: heartbeat, checkout, status,
delegation, execution stages. Read it there. This skill adds only what is ours.

Vocabulary: a **direction** is a long-lived stream mapped to a GitHub repository. A
**feature** is one shippable unit inside it: one engineer, one branch, one worktree, one
PR. Two duties recur below — **product ownership** (the outcome: the spec, the scope
boundary, whether to keep going) and **technical ownership** (the realisation: design,
decomposition, sequencing, sanctioned operations). Your company's charters name the role
holding each; a smaller company may give both to one role. The reviewer and
the approver are whoever the issue's own stages name.

## How work travels

Native execution stages carry a feature — nobody routes it by hand:

- Technical ownership decomposes the direction, creates the feature issue, assigns the
  engineer, and puts the review path on the issue itself (`executionPolicy.stages`): a
  **review** stage, then an **approval** stage held by the role that merges and releases.
- **The approval participant must never be the issue's implementer.** Paperclip forbids
  approving your own work, so when the assignee is the role that would normally approve —
  an operator issue the release duty runs itself: a staging/prod converge, a promotion
  train, an infra change — give the approval stage to a different role with standing to
  judge it, by default the leadership duty that ordered the work. A self-approval stage
  fails the review→approval transition with HTTP 422 "no eligible approval participant"
  and strands the issue (KIR-120 lost ~30m to exactly this; the same trap waits on every
  issue the release role executes itself, e.g. the promotion train).
- The engineer finishes and moves the issue to `in_review`. Paperclip reassigns it to the
  stage participant and wakes them.
- The reviewer decides. Approve advances the issue to the approval stage; request-changes
  returns it to the engineer. Only the active participant can decide.
- The approver merges, then closes the feature.

Never model review as a child issue, a mention grant, or a comment asking someone to pick
the work up. Those split the audit trail away from the issue being reviewed and loosen
who may decide. The stage keeps the gate, the authority, the return path and the wake on
the work.

## Decomposition (technical ownership)

- Features whose file sets overlap are **sequential**, never parallel. Say which files
  each feature owns, in a table, before delegating.
- One feature → one engineer. A follow-up to in-flight work goes to the same engineer on
  the same branch.
- Branch `feat/<issue-key>-<slug>` in a fresh worktree.

## Judge against a fresh base (review stage)

`git fetch origin` before you compare anything, and diff against `origin/main` — never a
local ref. Merges land while you review: a local `main` goes stale in minutes, and a
three-dot diff taken against it will show you other people's merged commits as if they
were this PR's scope. Exam #9 lost a review round to exactly that — a blocking finding
that evaporated on a fresh fetch, same head, no code changed.

## The verdict (review stage)

The verdict is your **native stage decision** — approve or request-changes on the review
stage itself, never a specially-formatted comment. The platform records who decided,
when, and on which issue; there is no parser and no verdict format to get wrong. In the
decision comment, name the PR and the **head SHA you reviewed** in prose: the approver
compares it against the live head before merging.

## A verdict is grounded or it is not a verdict

Either outcome is valid only when the relevant checks were **executed** and their meaningful
output is quoted in the decision — or when the decision states why they could not run and what
evidence stands in their place. Reasoning about the diff alone is not review: it neither proves
a finding nor earns an approval, and it is what feeds repeated rounds. An exit code is not
evidence; quote the output that matters.

## Three rounds, then doubt the contract

A review round is evidence about the head. Three rounds are evidence about the issue.

**At the review stage.** From the third request-changes on one issue, your decision comment must say
whether the new findings are the **same class** as the earlier ones. Same class means the
previous fix was correct and the criterion simply reaches further than the fix did. Say
so plainly — that sentence is a fact about the contract, and nobody else is positioned to
observe it.

**Engineer.** After a third request-changes, do not push a fourth head. Post a
scope-doubt comment carrying three things and nothing else:

- how many rounds have happened;
- the line count of the artifact you are changing at round one and now;
- whether the acceptance criterion has a **finite** set of tests that can satisfy it,
  and why.

Then stop and wait. You are not conceding the findings are wrong; you are reporting that
fixing each one has not been converging.

**Leadership.** A scope-doubt comment is a contract question for product ownership,
answered inside the company on the board — not through a user gate. The
decision is one of two — bound the contract, or change the approach — with a
recommendation attached. Never re-delegate the same contract. If the resolution would
change the direction's own scope, that is an owner class: `kira-escalation-discipline`.

### Why this rule fights your instincts

On 2026-07-26 a token-scoping shim went four review rounds in under three hours. Every
finding was real and reproduced; every fix was correct and pinned by a regression that was
red first. Twelve runs and 183 minutes shipped nothing, and two pull requests closed
unmerged. The owner changed the approach instead, and the replacement merged 57 minutes
later as twelve changed lines in one template.

Nobody was wrong in any single round. That is exactly the shape that does not stop on its
own, which is why the stop is a counted round rather than a judgement call.

## Ask across an assignment boundary with `agent://`

An agent may comment on an issue assigned to somebody else when a prior comment on that
issue mentions it as `agent://<agentId>`, and that comment's author is either the issue's
assignee or an active board user. That is the platform's own grant
(`commentAuthorCanGrantIssueMention`), not a workaround.

So: **if your comment asks something of an agent that is not the assignee, mention it.**
Without the mention its reply is a `403` and the answer lands wherever it can — TES-34
exists for no other reason, and the owner's question on TES-32 was answered on a
different issue than the one he asked it on. Across the board's whole history the mention
appears in exactly one comment.

This does not loosen the review path. Review stays a native stage (see above); a mention
is for a question, never for handing over work.

## dev is always green

Every configured CI job must be green before any merge, in every repository. For a
`kira-platform` PR targeting `dev`, that baseline tightens: pre-merge **dev-CI** evidence
is **exactly one** current GitHub check named `dev-ci` with status `completed` and
conclusion `success`. Its tested head SHA, the reviewer's approved SHA, and the PR's
current live head SHA must be identical.

Count that check rather than eyeballing it. List the check runs for the PR's live head,
keep the current (latest-per-name) results — superseded runs of an earlier attempt are
history, not evidence — and count the rows named `dev-ci`. Any count other than one fails
closed: zero means the gate never ran, two or more means no single run can be named as
the one that decided. A missing `dev-ci`, a stale check, or any non-success state fails
closed the same way. Return the feature to the engineer with the observed evidence;
never infer green from absence.

For a repository without configured pre-merge checks, the executable issue contract must
name exact verification commands and expected results against the live head. The
approver runs and records that contract; absence of both a configured check and an
explicit verification contract also fails closed.

A CI timer sweeps every `tools/test_*.py` + `tools/selftest_*.py` after each merge to
`dev` and files an **urgent** hotfix issue when anything is red. That issue is a
drop-everything lane: branch from fresh `origin/dev`, fix the actual defect (the test OR
the code — whichever is wrong), PR to `dev`. Never let a promotion train be the thing
that discovers red tests (KIR-147/148 cost the KIR-122 train ~1.5h exactly this way).
Corollary for every PR: if your change alters a contract a selftest asserts, update the
selftest in the same PR — the sweep treats your merge as the offending HEAD.

## Staging (release duty)

Staging is an autonomous zone: no owner gate for anything confined to it.
The deploy identity is the **standing** keygate key (`--standing`, tag `kg-standing-re`,
targets `staging-hop`/`staging-core`) — install once, reuse across issues, no per-task
keygen/install/remove ceremony. If `keygate check` shows it missing, reinstall and carry
on.

## Prod converge (release duty)

The decision about prod is the train merge into `main` — a technical-ownership decision
along this sanctioned path, and not the owner's. The
converge after it is mechanics you run yourself through **prodgate** — never
by asking the owner, never by inventing a path:


```sh
prodgate converge --target snapshot     # rollback point first
prodgate converge --target cognition    # or: deploy, hermes-studio, paperclip-team
```

The reply's `main_sha` is your deployed-SHA evidence. Refusals are terminal answers (unknown
target, converge in flight, 15-min cooldown) — wait, don't work around. The allowlist is exactly
`cognition`/`deploy`/`hermes-studio`/`paperclip-team`/`snapshot`;
infra roles as a whole stay with the operator. `paperclip-team` is the one narrow exception
(owner approval 44ae0010): a fixed `--tags paperclip_team_kira_mcp` that converges the
managed Kira MCP block only — the two tagged tasks, never the whole `paperclip_team` role.

## Standing capabilities — reference them, never reinvent access

Issues and plans name the capability they use and NOTHING more: **standing staging key**
(keygate), **prodgate** (prod converge), **dev-CI** (red dev files its own hotfix issue). An
issue that describes an access mechanism of its own — an ephemeral key ritual, an owner gate for
staging, a manual prod path — is stale by definition: fixing the text is part of picking the
issue up, and at the review stage a stale access description is a **blocking finding**.

## The merge (release duty)

- Merge **only while you hold the approval stage** and it is decided approve — the stage
  decision is the gate; there is no separate merge-gate parser.
- Before `gh pr merge --squash`, compare the PR's live head against the SHA named in the review
  decision. A push after review invalidates the review: send the issue back through the review
  stage, never merge a head nobody reviewed.
- Never force-push, never push to `main`. Hooks enforce this; they are not obstacles.
- Release: everything claimed is merged, `main` is green, changelog/README/versions agree → tag
  → GitHub release → report the URL on the direction issue.
- A broken `main` is yours: revert first via a hotfix PR; fix forward only for a proven
  one-liner.

## When a decision is not yours

`blocked` pages nobody — it is a planning status, not a pager. Which decisions leave the company
and how they travel is `kira-escalation-discipline`. A user-facing gate is never opened for a
question a colleague can answer, whatever your role: those gates carry no topic, so nothing can
route them, and they land on the owner.
