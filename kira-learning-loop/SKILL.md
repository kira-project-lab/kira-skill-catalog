---
name: kira-learning-loop
description: How Kira Lab learns from its own failures without learning from noise. Use when reviewing agent trajectories, classifying a defect, or proposing any change to a prompt, skill, or runtime. Required reading before any coaching proposal.
---

# The learning loop

Your job is not to find things to change. It is to tell an **improvement** from a
**coincidence** — and most weeks, to conclude there is nothing to change.

A team that learns from noise is worse than one that never learned: it accumulates
superstition, and every rule it adds makes the next real fix harder to find.

## Classify before you propose

Every finding gets a class. Get this wrong and you fix the wrong surface.

| Class | What it looks like | Who owns the fix |
|---|---|---|
| **P** prompt logic | the agent did exactly what it was told, and that was wrong or impossible; consistent across agents | the prompt or a company skill |
| **S** skill gap | the agent improvised a procedure it did not have; different agents improvise differently | assign the missing skill |
| **A** authority | a 4xx naming a permission; every agent hits it identically | the App / token roles — **not** the prompt |
| **R** runtime | contained, throttled, OOM-killed or timed out; the work was sound but cut short | the isolation layer |
| **M** model variance | same prompt, same context, different answer; does not reproduce | **nobody — write nothing** |
| **H** harness defect | the check was wrong, not the team | the harness |
| **T** transport | nobody reasoned badly; the work simply stopped — a wake was lost | the relay / platform |

**Only P and S may become a prompt or skill change on the evidence of a defect.** A permission
cannot be fixed by rewording an instruction, and a lost wake is not laziness. A, R, T and H stay
barred from text whatever else is true; M is barred absolutely.

A defect is not the only thing that licenses text. Two further bases exist, both
narrower than they look: **a vendor instruction**, cited to the guide that gives it — temporary,
expiring with the rewrite exception it was created for — and **an owner decision recorded as an
ADR**, accepted, or proposed with the owner's decision dated and sourced in the text. Without
that qualifier an author could write a proposal licensing their own change.

## The rules that keep this honest

1. **An agent's inference about the platform is not evidence about the platform.** Read the
   platform. Exam #8 deadlocked twice because an honest report of an API rejection was written
   into the canon as a rule — and the rule was false.
2. **If it does not reproduce, it did not happen.** One unlucky run is class M. A rule written
   to suppress it is superstition with a commit message.
3. **If two classes fit, take the lower-level one.** A permission hole that produces confused
   prompting is A, not P: fixing the prompt only teaches the agent to work around a hole you
   left open.
4. **Evidence is links, not prose.** Issue and comment references, an API response, a process
   tree. "The agent seemed confused" is not a finding.
5. **A cycle with no proposal is a successful cycle.** Say so and stop.

## Before you propose

- The diff is minimal and touches exactly one surface (D-21).
- It names the scenario that must replay green, and the holdout that must not regress.
- You never apply your own diff. It goes to independent review — an agent that rewrites its own
  instructions unreviewed is not learning, it is drifting.

## After it is applied

**Verify the bytes.** `POST /skills/:id/versions` records a revision while the content agents
actually read stays stale — a silent no-op that once voided an accepted apply and cost half a
day. Run `provision_company.py --verify`: git package == live bytes, or the change did not
happen.

Then replay the failing scenario **twice** (a fix that works once may have been the same luck
that caused the failure), and run the **holdout** — a scenario you have never seen. If your fix
only helps the cases it came from, it did not improve anything; it memorised. That proposal is
rejected, not tuned.

Full runbook: `docs/product/kira-lab-autonomy/LEARNING-LOOP.md`.
Taxonomy with evidence signatures: `docs/product/kira-lab-autonomy/DEFECT-TAXONOMY.md`.
