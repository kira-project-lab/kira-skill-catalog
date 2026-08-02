---
name: kira-prompt-authoring
description: What to keep and what to cut when writing an agent charter or a company skill in this estate. Use when authoring, reviewing, shortening or extending any AGENTS.md or SKILL.md here, and when judging whether a rule earns its place in the context window.
---

# Writing the text agents run on

The craft vocabulary — the no-op test, the information ladder, the leading word, and the named
text failure modes — lives in `writing-great-skills`, pinned by commit and digest in
`companies/kira-lab/PROVENANCE.md`. Its body is not stored in this estate; until it is imported
by tree URL and assigned alongside this skill, treat that vocabulary as a reference you must
fetch, not one you already hold.

This skill carries only the delta: what the model vendors ask of us, and what this estate
learned at its own cost.

## Density: what the vendors ask

Anthropic's guidance for Opus 5 and OpenAI's for GPT-5.6 agree that unnecessary instruction is not
free. OpenAI measured it on internal coding-agent evals — leaner system prompts scored 10-15%
higher while cutting tokens 41-66% — and calls those figures directional, to be re-checked on your
own tasks.

This estate runs both vendors' models, one per role, pinned in each company's `.paperclip.yaml`:
`companies/kira-lab/.paperclip.yaml` and
`companies/orangehack/.paperclip.yaml` both name `gpt-5.6-sol` for the judgement roles and a Claude
model for the ones that write. Read the pin rather than assuming, and when the pin and the live
board disagree the board is the fact and the pin is the bug: Kira Lab's engineer sat pinned to `claude-opus-4-8` while the running
company used `claude-opus-5`, because the pin was copied from a roster that no longer existed.
Neither guide is the only one that applies; where they agree, write one text.

**State each instruction once** (OpenAI). A rule in two places is one rule plus a maintenance
bug.

**Cut instructions the model already follows.** Anthropic is explicit for Opus 5: generic
verification instructions — "include a final verification step", "use a subagent to verify",
"double-check your answer" — cause over-verification, and removing them costs no quality. This
is about generic self-check prose, not about a role's own duties: the Release Engineer's
obligation to read CI, compare the approved SHA against the live head and confirm the merge is
a domain gate, and stays.

**Ask for everything and filter in a second pass.** Anthropic warns that a review prompt saying
"only report high-severity issues" is followed literally and returns less. Say what to report;
say separately who filters.

**Cap delegation rather than encourage it** (Anthropic, Opus 5): the model already delegates
readily, and a subagent is not a way to check your own work.

**Calibrate length and cadence explicitly** (Anthropic, Opus 5): by default the model writes
longer documents and narrates more than earlier ones. Silence on length is not neutrality.

**Assign only the skills a role uses** (OpenAI: expose only relevant tools, with short precise
descriptions). Every assignment is context the role pays for on every run.

**A shared skill names duties, not job titles.** `kira-dev-pipeline` is assigned to two companies
with different rosters, one of them without a CTO. Its decomposition section was headed
"Decomposition (CEO)" until the leadership split made that false in one of the two on the same
day; it now reads "Decomposition (technical ownership)" and did not need touching again. A skill
that names posts breaks on the first company shaped differently; a skill that names the duty
survives the reshuffle, and survives becoming a template.

**Give the whole specification up front.** Anthropic reports this for Opus 5; OpenAI's guide is
silent on it, so treat it as an Opus finding rather than a law.

**Remove one group at a time and re-check** (OpenAI). Bulk deletion cannot tell you which cut
was the one that hurt.

## What survives the cut

OpenAI's exception has two limbs: keep guidance that **encodes a product requirement** or
**corrects a measured gap**. Both limbs, or the test deletes the rules that exist because
someone decided they must, rather than because something broke.

> A rule stays if either:
> 1. it names a recorded failure with a date, **and the fix for that failure belongs to text** —
>    class P or S in the taxonomy; or
> 2. it states a requirement of safety, authority or product, **or a binding fact of the
>    platform that an agent would otherwise rediscover by failing** — citing the decision,
>    contract or observed API behaviour that establishes it.
>
> If a rule's cause is real but unwritten, write the cause down — do not delete the rule.
> If a rule's cause was fixed on another surface, the rule is due for removal.
> If the record gives two classes, the rule stays until the lower-level surface is fixed.

Limb one's qualifier is what stops a date from being enough. A run killed by `MemoryMax` is a
real dated failure, and no sentence in a charter repairs it — class R belongs to the isolation
layer. The date proves something happened; the class decides whether text is the thing that
answers it.

Limb two is what stops the test from absorbing everything, and its guard is that a decision
exists — not that the text names it. "No secret value in plaintext in git" rests on the decision
that keeps repo config encrypted with SOPS/age and runtime secrets in Lockbox; "CI is read-only,
`actions: write` withheld" rests on the one that withheld it. Neither waited for an incident and
neither rests on preference.

A rule that can name no decision behind it is not a product requirement — it is a habit. The
difference is checked by whoever audits the corpus against `docs/decisions/`, not by the agent
reading the rule, so the burden is on the author: if you cannot point at the decision when asked,
the rule does not qualify under this limb.

The second half of that limb covers a species the first draft of this test deleted by accident:
facts of the platform. "Do not attempt a GitHub `APPROVE` — every agent authenticates as the
same App, so author and reviewer are one identity and GitHub refuses" is neither an incident
nor a requirement anyone imposed. It is true, and an agent without it spends a review round
learning it from a rejection. The citation for such a rule is the behaviour itself: the API
response, or the contract that produces it.

The dual-class clause exists because the estate has one. The Reviewer's "fetch before you
compare" is recorded as class H/P, and the rule lives in `kira-dev-pipeline`, not in a charter:
the check itself was wrong, and the rule is the interim guard. Deleting it before the harness
side is fixed reopens the failure.

The repair clause covers the third case. The Release Engineer's "exactly one current `dev-ci`
run" is argued from counting alone — zero means the gate never ran, two or more means you
cannot tell which run decided — and names no incident. But the cause exists: commit `2193b8f`
records that kira-platform produced zero check runs and PR #198 could not clear the gate. The
defect is an unwritten provenance, not an unearned rule, and the fix is a citation.

## Accuracy outranks density

The failures this estate records are of two kinds: text that was missing, and text that
described something that does not exist. Neither is excess detail. Commit `5ff98be` names the
second kind as the week's recurring class — "inherited or invented text described a system that
did not exist" — and it keeps recurring: fourteen one-line stubs standing in for a skill layer,
charters that never named the platform manual, a coach writing to a surface the next converge
overwrites, twelve cross-references into a namespace this estate does not have.

So the first pass over any text asks whether it is true here, not whether it is long:

- Every path, tool, flag and skill name resolves where the agent runs. A reference that does not
  is a defect, not a stale comment.
- **A rule carries its reason and never its citation.** Write the rule so it is true and complete
  on its own, with the reason in one sentence inside it: *what failed*, not *where that is
  recorded*. The record stays in `docs/decisions/` and `docs/incidents/ledger.md` for whoever
  audits the corpus; the agent reading the rule at runtime cannot open either, so a reference in
  the text buys the reader nothing and costs every reader something.

  This replaced a marked-tail notation on 2026-07-28. The cost of the change is real and worth
  stating: a rule that looks arbitrary can no longer be traced to the failure that bought it from
  inside the text. Before deleting one, assume it was expensive.
- Every claim about the platform comes from the platform's own manual or its API. An agent's
  account of what happened to it is a hypothesis about the platform, not evidence.
- Every claim attributed to a vendor stays inside what that vendor said. A finding about one
  model is a finding about one model.

Shortening a false sentence produces a shorter false sentence.

## When a text change is licensed

`kira-learning-loop` owns that question — read it there. This skill governs what a licensed
change may keep and what it must cut, not whether the change may happen.
