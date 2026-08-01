---
name: kira-escalation-discipline
description: Which decisions leave the company for the owner — the eight owner classes — and how every other question is answered in-company through the board. Use when a missing decision or a protected action blocks delivery, and before opening any gate.
---

# Escalation discipline

Escalation is for a decision or a protected action that cannot be resolved from the assigned
scope and the available evidence. It is not a status-reporting path.

## Decisions live inside the company

Four duties answer almost everything that once left the company. Your company's charters name
the role holding each; a smaller company may give two of them to one role.

- **Product ownership** — what is being built and whether it is still worth building: the spec,
  the scope boundary, acceptance-criteria statements, whether a result meets its goal, whether
  to change approach, cancelling an order.
- **Technical ownership** — how it is realised: design and contracts, decomposition, sequencing
  across streams, criterion proofs, and the sanctioned operational decisions — promotion trains,
  prodgate and converges, certifications, governance exceptions, sanctioned live provisioning.
- **Implementation** — the issue's assignee, inside the assigned slice.
- **The stage decision** — whoever the issue's own review and approval stages name.

Ask the duty-holder through the board's native surfaces: a comment on an issue you share, a
child issue assigned to them, or the stage's return path. Bring options and one recommendation
when you have them.

## The eight owner classes

Only these leave the company. Four are confirmation gates:

1. **Outbound communication** to real people on the owner's behalf. Drafts are free; sending is
   gated.
2. **Money** — payments, purchases, subscriptions, billing changes.
3. **Production and infrastructure outside the sanctioned pipeline.** The delegated path — the
   promotion-train merge, `prodgate`, staging — is in `kira-dev-pipeline` and is not a gate.
4. **Irreversible data**: delete, overwrite, publish, account actions.

Two more are standing confirmations — routing an order to a resumable project, and creating a
new company. And two are reserved beyond all of these:

5. **Secrets, and expanding credentials or access** beyond the standing grants.
6. **Changing the standing roster** — a new standing agent or person.
7. **Changing a direction's own scope.**
8. **Accepting a material risk against a hard infrastructure invariant** — the VPN address, a
   destructive operation on the production brain, keygate or selfheal.

No company role may take these, at any level. **If you cannot tell which class an action falls
in, treat it as the owner's and say why you were unsure.** A wrong guess towards him costs a
message; a wrong guess away from him can cost the thing itself.

## A user-facing gate is an owner gate

`request_confirmation` and `ask_user_questions` carry no topic in their kind, so nothing can
route them in-company — they reach the owner. Open one only for a decision in the eight classes
above.

A question a colleague can answer — is this criterion provable, should this be decomposed
differently, which approach, a product call missing from the brief — goes to the duty-holder
instead. Each user gate costs a human round-trip, measured at about seven hours outside the owner's
online window.

The gate lands on the company's responsible user, who is a channel and not a decider: the
platform holds a single `defaultResponsibleUserId`, so she receives every gate and forwards it,
and the decision is recorded naming who actually decided before the gate is closed, so the
journal cannot credit the mailbox with the judgement. Your own mechanics are unchanged — bind the gate to the exact resource and action,
include the exact diff or command, and continue on its continuation event.

- Finish the bound document **before** opening the gate. Every later revision expires it and
  burns a decision round — KIR-194 lost two gates to exactly that.
- One escalation per decision. Wait for its continuation event: do not poll, do not open a
  second gate while the first is pending, and do not duplicate an interaction on silence.

## Staging is an autonomous zone

Never open an owner gate for an action confined to staging — deploys, converges, restarts, the
standing keygate identity. "It touches infrastructure" is not a gate when the infrastructure is
staging. KIR-132 spent hours of the CEO-1 rollout waiting on a confirmation this rule now
answers.

That autonomy covers the sanctioned path (`make … TARGET=staging`), not the machine underneath
it. Host-level Incus, systemd or Ansible action is neither yours to take nor yours to ask the
operator for — see `kira-host-boundary`.

## Missing capability

Access is meant to be standing — the company's `grants.yaml`. If a capability is
genuinely missing, raise a missing-capability escalation naming the concrete ask, rather than
minting access, fanning out a workaround, or sitting `blocked` in silence. Expansion beyond the
standing grants is owner class 5.

## Consulting Kira

She holds context and memory and decides nothing. Consult her only when the task
explicitly asks for her or needs knowledge that is hers — follow `kira-ask-kira`. Ordinary
questions, research, planning and prioritisation do not route through her.

## Platform facts worth carrying

- Setting `assigneeUserId` to the board user is not a handoff, and an @mention of the owner is
  not a request. A decision for him travels as a gate bound to its resource; nothing else
  reaches him, and nothing else leaves an auditable record.
- `blocked` alerts nobody. It is a planning state, so set it freely with the reason: the
  dependency, the missing input, and who clears it.
- Killing an issue follows one order — cancel, verify terminal, then hide. A hidden non-terminal
  issue is an invisible zombie that keeps running.

## Never escalate at all

Anything the pipeline rules or the roster already decide. Status, progress, FYI — the board
shows them. Anything answerable from the repository, the issue history, the authoritative docs,
or a bounded research task you can run yourself.
