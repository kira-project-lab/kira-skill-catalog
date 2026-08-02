---
name: kira-dev-pipeline
description: How this company ships code — decomposition, branches, the native review/approval stages, and release. Use when planning, decomposing, implementing, reviewing or releasing any engineering work. The Paperclip skill has the platform mechanics; this has only what is specific to the company.
---

# Dev pipeline

The **Paperclip skill** is the manual for the platform: heartbeat, checkout, status, delegation,
execution stages. This adds only what is ours.

A **direction** is a long-lived stream mapped to a GitHub repository; a **feature** is one
shippable unit inside it — one engineer, one branch, one worktree, one PR. Two duties recur:
**product ownership** (the outcome — spec, scope boundary, whether to keep going) and **technical
ownership** (the realisation — design, decomposition, sequencing, sanctioned operations). Your
charters name who holds each; a smaller company may give both to one role. The reviewer and the
approver are whoever the issue's own stages name.

## How work travels

Native execution stages carry a feature; nobody routes it by hand. Technical ownership creates the
feature issue, assigns the engineer, and puts the path on the issue itself
(`executionPolicy.stages`): a **review** stage, then an **approval** stage held by the role that
merges. The engineer moves the issue to `in_review` and the platform wakes the reviewer. Approve
advances to approval, request-changes returns it to the engineer, and only the active participant
can decide. The approver merges, then closes.

**The approval participant must never be the issue's implementer.** Paperclip forbids approving
your own work, so when the assignee *is* the role that would normally approve — an operator issue
the release duty runs itself, a promotion train, an infra change — give approval to a different
role with standing to judge it, by default the leadership duty that ordered the work. Getting it
wrong fails the review→approval transition with `422 no eligible approval participant` and strands
the issue; about thirty minutes went to exactly that.

Never model review as a child issue, a mention grant, or a comment asking someone to pick the work
up. Those split the audit trail from the work and loosen who may decide. The stage keeps the gate,
the authority, the return path and the wake on the work itself.

## Decomposition (technical ownership)

- Features whose file sets overlap are **sequential**, never parallel. Say which files each feature
  owns, in a table, before delegating.
- One feature → one engineer. A follow-up to in-flight work goes to the same engineer on the same
  branch.
- Branch `feat/<issue-key>-<slug>` in a fresh worktree.

## The review stage

**Judge against a fresh base.** `git fetch origin` before comparing anything, and diff against the
remote ref of the branch this PR targets — `origin/dev` for a feature, `origin/main` only for a
promotion train. Never a local ref: it goes stale in minutes and shows other people's merged
commits as this PR's scope. Never a base the PR does not target either — diffing a feature against
`main` produces the same wrong-scope finding by another route. Exam #9 lost a round to precisely
this: a blocking finding that evaporated on a fresh fetch, same head, no code changed.

**The verdict is your native stage decision** — approve or request-changes on the review stage,
never a specially formatted comment. The platform records who decided, when, and on what; there is
no parser to satisfy. Name the PR and the **head SHA you reviewed** in prose, because the approver
compares it against the live head before merging. Do not attempt a GitHub `APPROVE` review: every
agent authenticates as the same GitHub App, so PR author and reviewer are one identity and GitHub
refuses it whatever the token permits — a `COMMENT` review is fine as an audit trail.

**A verdict is grounded or it is not a verdict.** Either outcome is valid only when the relevant
checks were executed and their meaningful output is quoted, or when the decision says why they
could not run and what evidence stands in their place. Reasoning from the diff alone proves no
finding and earns no approval, and it is what feeds repeated rounds. An exit code is not evidence.

**Every finding is labelled substance or hygiene, and only substance blocks.** Substance: if this
finding stands, the claim could be false or the change unsafe. Hygiene: untidy but the claim
holds — extra read-only reads, surplus output, formatting. Hygiene findings go into the verdict
as advisories and never carry a request-changes on their own; criteria bind the deliverable
artifact, not the whole transcript that produced it (`kira-issue-contract` rule nine). LAB-28
took four rounds where the substance was proven in round one and every later block was hygiene
read as blocking. A changes-requested verdict also names its round — "Round N" — so the count
below needs no archaeology.

## Three rounds, then doubt the contract

A review round is evidence about the head. Three rounds are evidence about the issue.

**At the review stage,** from the third request-changes on one issue your decision comment must say
whether the new findings are the **same class** as the earlier ones — meaning the previous fix was
correct and the criterion simply reaches further than the fix did. Nobody else is positioned to
observe that.

**Implementer — whichever role holds the issue:** after a third request-changes, do not push a
fourth head. Post a scope-doubt comment carrying three things and nothing else — how many rounds
have happened; the line count of the artifact at round one and now; whether the acceptance
criterion has a **finite** set of tests that can satisfy it, and why. Then stop, @mention the
contract owner (the issue's author, usually the CTO) and set the issue `blocked`. You are not
conceding the findings; you are reporting that fixing them one by one has not converged.

**Contract owner:** a scope-doubt comment is a contract question, answered inside the company on
the board and never through a user gate. Arbitrate one of three ways: amend the contract visibly
(`kira-issue-contract` rule eight), void the finding with recorded rationale, or change the
approach — with a recommendation attached, and never re-delegate the same contract unchanged. A
dispute involving the contract owner's own work goes to the CEO. If the resolution would move
the direction's own scope, that is an owner class — `kira-escalation-discipline`.

The rule is a counted round rather than a judgement call because the failure looks like progress
from inside: on 2026-07-26 a token-scoping shim took four rounds in under three hours, every
finding real and every fix correct, and twelve runs and 183 minutes shipped nothing while two pull
requests closed unmerged. The approach changed instead, and the replacement merged 57 minutes later
as twelve changed lines in one template.

## The GitHub App reaches four accounts, and roles differ per account

`kira-platform-app` is installed on `kira-project-lab`, `werserk`, `team-4u-projects` and
`Orange-Hack`. Mint against whichever owns the repository:

```sh
GH_TOKEN=$(gh-app-token --org werserk --role engineer)
```

The minter matches installations by account login, so the account name is the whole configuration —
there is nothing to set up first. What differs is the **role**: permissions are per role, not per
account, and the table is checked in at `ansible/roles/paperclip_team/files/gh-app-token`. Read your
row before assuming an operation is available; `reviewer` cannot push and `release` cannot write
issues, by design.

Git over HTTPS is a separate path from the `gh` API and does **not** yet resolve the account from the
repository — the credential helper defaults to `kira-project-lab`. Until that ships, clone and push
outside that organisation will fail even though `gh` works.

**A token you mint is a secret for the rest of the run.** Your run transcript is durable and is read
by other agents and by the owner, so anything printed there is exposed for as long as the log lives.
The rules are mechanical, not judgement calls:

- **Anything that reads a place where credentials live may return one. Use forms that count or
  locate, never forms that print.** Environments (`env`, `printenv`, `set`, `export -p`), process
  tables and their command lines (`ps`, `/proc/*/cmdline`, `/proc/*/environ`), service definitions,
  connection strings, and other agents' logs are all such places — the list is illustrative and you
  are expected to recognise the next one yourself. Two runs breached this on 2026-07-30 within three
  hours: the first dumped an environment, the second inspected the process table, and the rule at the
  time named only the first because it listed commands instead of the class.
- Never echo, `cat` or interpolate a secret into output. To search for one, use `grep -c` for a count
  or `grep -l` for paths; never a form that prints the matching line.
- **Never put a secret on a command line, even as `$VAR`.** The shell expands before `exec`, so the
  literal sits in `/proc/<pid>/cmdline` for the whole request and any concurrent process can read it —
  which is exactly how a reviewer caught one on 2026-07-30. Your transcript looks clean because it
  stores the unexpanded text; the process table does not. Pass it out of band instead:

  ```sh
  # not this
  curl -H "Authorization: Bearer $PAPERCLIP_API_KEY" "$PAPERCLIP_API_URL/api/issues/$ID"
  # this
  printf 'header = "Authorization: Bearer %s"\n' "$PAPERCLIP_API_KEY" > "$cfg"   # umask 077
  curl --config "$cfg" "$PAPERCLIP_API_URL/api/issues/$ID"; rm -f "$cfg"
  ```

  It happened to be harmless because that token lives one hour and is bound to its own run. The next
  credential in your hand may be neither.
- Auditing whether credentials leak somewhere is the sharpest case of this rule, not an exception to
  it. Answer "does this log contain a connection string" with `grep -c`; the moment you print the
  match to prove it, you have added one more copy to a durable transcript and destroyed your own
  slice.

## What you print is resent on every later turn

Your transcript is not a scrollback — it is the prompt. Every character a tool returns is resent with
each subsequent turn of the run, so a single careless read is paid dozens of times. Measured across
one day of this company: tool output was 64% of the technical owner's transcript, and 80% of that
volume sat in the 10–50 KB band — ordinary file reads and API responses, not exotic mistakes.

Two habits carry almost all of it:

- **Bound every command at the source.** `grep -c` for a count and `grep -l` for paths instead of
  printing matches; `--max-count`; `jq` projecting the two fields you need rather than the object;
  `head -c` on anything whose size you have not checked. Ask for the answer, not the haystack.
- **Never read a run-log with a line-based tool.** `/data/kira-paperclip/instances/default/data/run-logs/**`
  is NDJSON whose lines reach 131 145 characters. On a real 64 MB log, `tail -n 12` returns 46 295
  characters — twelve lines. Use `tools/paperclip/logread.py`, which is bounded by construction:

  ```sh
  python3 tools/paperclip/logread.py summary  <log>                 # shape only, ~300 chars
  python3 tools/paperclip/logread.py grep     <pattern> <log>       # line numbers + capped excerpts
  python3 tools/paperclip/logread.py fields   ts,seq,stream <log>   # named fields, truncated values
  ```

  `summary` on that same 64 MB log returns 311 characters — 149 times less than the twelve-line tail,
  and it answers the orientation question the tail was reaching for.
- Diagnosing a credential means printing its **name and length**, never its value:
  `echo "GH_TOKEN len=${#GH_TOKEN}"`.
- A secret that has reached a transcript is an incident you **report**, naming the run and the
  location and nothing else. Do not edit, delete or truncate the log to clean it up — that destroys
  evidence and is not yours to do.

## Ask across an assignment boundary with `agent://`

To ask something of an agent that is not the issue's assignee, mention it as `agent://<agentId>`.
Without the mention its reply is a `403` and the answer lands wherever it can — an owner's question
was once answered on a different issue than the one he asked it on. This is the platform's own
grant (`commentAuthorCanGrantIssueMention`), not a workaround, and it is for a question, never for
handing over work: review stays a native stage. The same boundary holds for state: a `PATCH` on an
issue assigned to someone else returns `403` — to change it, create a child issue assigned to its
owner naming the exact edit.

## dev is always green

Every configured CI job must be green before any merge, in every repository. For a `kira-platform`
PR targeting `dev` **or `main`** the baseline tightens: **exactly one** current GitHub check named
`dev-ci`, with status `completed` and conclusion `success`, whose tested head SHA equals both the
reviewer's approved SHA and the PR's live head. Promotion trains are included deliberately: the
workflow triggers on both branches, so a train showing zero checks is a fault to investigate, never
the expected state.

Count that check rather than eyeballing it: list the check runs for the live head, keep the latest
per name — superseded runs are history, not evidence — and count the rows named `dev-ci`. Any count
other than one fails closed, because zero means the gate never ran and two means no single run can
be named as the one that decided. A missing check, a stale one, or any non-success state fails
closed the same way. Return the feature with the observed evidence; never infer green from absence.

In a repository with no configured pre-merge checks, the issue contract must name exact
verification commands and expected results against the live head, and the approver runs and records
them. Neither a check nor a verification contract also fails closed.

A CI timer sweeps every `tools/test_*.py` and `tools/selftest_*.py` after each merge to `dev` and
files an **urgent** hotfix issue when anything is red: branch from fresh `origin/dev`, fix whichever
is wrong — the test or the code — and PR to `dev`. Never let a promotion train be the thing that
discovers red tests; one lost about an hour and a half that way. Corollary: if your change alters a
contract a selftest asserts, update the selftest in the same PR, because the sweep treats your merge
as the offending HEAD.

## Staging and prod (release duty)

Staging autonomy remains the policy intent: a staging-only action does not become an owner gate.
There is currently no sanctioned staging mutation path. Guarded
`TARGET=staging` commands fail closed until a separate safe non-production guard exists. The
standing keygate identity may remain
installed (`--standing`, tag `kg-standing-re`, targets `staging-hop` and `staging-core`), but it
does not authorize a deploy, converge, restart, or key reinstall while the path is unavailable.
`keygate check` remains read-only inspection, not permission to reinstall. Record the blocked
release and wait; do not open an owner gate and do not ask for a direct host, Ansible, Incus, or
hand-run `make` workaround.

The decision about prod is the train merge into `main` — a technical-ownership decision along this
sanctioned path, not the owner's. The converge after it is mechanics you run yourself through
**prodgate**, never by asking the owner and never by inventing a path:

```sh
prodgate converge --target snapshot     # rollback point first
prodgate converge --target cognition    # or: deploy, hermes-studio, paperclip-team
```

The reply's `main_sha` is your deployed-SHA evidence. Refusals are terminal answers — unknown
target, converge in flight, 15-minute cooldown — so wait rather than work around. The allowlist is
exactly `cognition`, `deploy`, `hermes-studio`, `paperclip-team` and `snapshot`; infra roles as a
whole stay with the operator. `paperclip-team` is the one narrow exception (owner approval
44ae0010): a fixed `--tags paperclip_team_kira_mcp` converging the managed Kira MCP block only,
never the whole `paperclip_team` role.

**Reference a standing capability, never reinvent access.** Issues and plans name the capability
they use and nothing more: prodgate and dev-CI are active; staging mutation is explicitly
unavailable pending its separate guard. An issue describing an access mechanism of its own — an
ephemeral key ritual, an owner gate for staging, a direct host workaround, a manual prod path — is
stale by definition; fixing the text is part of picking the issue up, and at the review stage a
stale access description is a blocking finding.

## The merge (release duty)

- Merge **only while you hold the approval stage** and it is decided approve. The stage decision is
  the gate; there is no separate merge-gate parser.
- **The merge happens in the issue that carries that approval stage — never in a new one.** If the
  approved work is not merged when its gate issue completes, reopen or return that issue; creating a
  successor issue to press the button splits the audit trail and costs a full cycle. Five issues across
  two orders existed for no other reason.
- Before merging, compare the PR's live head against the SHA named in the review decision. A push
  after review invalidates the review: send it back through the review stage rather than merge a
  head nobody read.
- Merge with a merge commit (`gh pr merge --merge`), never squash: this repository's history is the
  audit trail, and a promotion train squashed into one commit loses which change carried what.
- Never force-push, never push to `main`. Hooks enforce this; they are not obstacles.
- Release when everything claimed is merged, `main` is green, and changelog, README and versions
  agree — tag, GitHub release, report the URL on the direction issue.
- A broken `main` is yours: revert first through a hotfix PR, and fix forward only for a proven
  one-liner.

## When a decision is not yours

`blocked` pages nobody — it is a planning status, not a pager. Which decisions leave the company and
how they travel is `kira-escalation-discipline`. A user-facing gate is never opened for a question a
colleague can answer, whatever your role: those gates carry no topic, so nothing can route them and
they land on the owner.
