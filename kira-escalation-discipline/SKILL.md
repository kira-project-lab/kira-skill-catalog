---
name: kira-escalation-discipline
description: Which decisions leave the company for the owner — the eight owner classes — and how every other question is answered in-company through the board. Use when a missing decision or a protected action blocks delivery, and before opening any gate.
---

# Escalation discipline

Escalation is for a decision or a protected action that cannot be resolved from the assigned scope
and the available evidence. It is not a status-reporting path.

## Decisions live inside the company

Four duties answer almost everything that once left. Your charters name who holds each; a smaller
company may give two of them to one role.

- **Product ownership** — what is being built and whether it is still worth building: the spec, the
  scope boundary, acceptance-criteria statements, whether a result meets its goal, whether to
  change approach, cancelling an order.
- **Technical ownership** — how it is realised: design and contracts, decomposition, sequencing
  across streams, criterion proofs, and the sanctioned operational decisions — promotion trains,
  prodgate and converges, certifications, governance exceptions, sanctioned live provisioning.
- **Implementation** — the issue's assignee, inside the assigned slice.
- **The stage decision** — whoever the issue's own review and approval stages name.

Ask the duty-holder through the board's native surfaces: a comment on an issue you share, a child
issue assigned to them, or the stage's return path. Bring options and one recommendation.

## The eight owner classes

Only these leave the company. Four are confirmation gates:

1. **Outbound communication** to real people on the owner's behalf. Drafts are free; sending is
   gated.
2. **Money** — payments, purchases, subscriptions, billing changes.
3. **Production and infrastructure outside the sanctioned pipeline.** The delegated production
   path — the promotion-train merge and `prodgate` — is in `kira-dev-pipeline` and is not a gate.
4. **Irreversible data**: delete, overwrite, publish, account actions.

Two further decisions are standing confirmations rather than classes — routing an order to a
resumable project, and creating a new company. Four classes are reserved beyond the gates:

5. **Secrets, and expanding credentials or access** beyond the standing grants.
6. **Changing the standing roster** — a new standing agent or person.
7. **Changing a direction's own scope.**
8. **Accepting a material risk against a hard infrastructure invariant** — the VPN address, a
   destructive operation on the production brain, keygate or selfheal.

No company role may take these, at any level. **If you cannot tell which class an action falls in,
treat it as the owner's and say why you were unsure.** A wrong guess towards him costs a message; a
wrong guess away from him can cost the thing itself.

## A user-facing gate is an owner gate

`request_confirmation` and `ask_user_questions` carry no topic in their kind, so nothing can route
them in-company — they reach the owner. Open one only for a decision in the eight classes.

A question a colleague can answer — is this criterion provable, should this be decomposed
differently, which approach, a product call missing from the brief — goes to the duty-holder
instead. Each user gate costs a human round-trip, measured at about seven hours outside the owner's
online window.

**Approving your own technical plan is never an owner class.** Design, decomposition and sequencing
are the technical-ownership duty itself, so a plan carrying no action from the eight classes needs no
approval from anyone: publish it and create the children. Want a second opinion on the decomposition?
Ask the CEO on the board. Open a gate only when the plan itself carries one of the eight — a runtime
patch, an access change, spend beyond the funded budget — which is exactly how a proposed patch to the
Paperclip build was caught in July. Three consecutive orders opened a plan-approval gate; by the third
it carried nothing that needed the owner and it held six issues while it waited. If a rule you are
following is not written in your equipment, you are following a precedent, not an instruction — say so
and act on the written rule.

The gate lands on the company's responsible user, who is a channel and not a decider: the platform
holds a single `defaultResponsibleUserId`, so she receives every gate and forwards it, and the
decision is recorded naming who actually decided before the gate closes — the journal must not
credit the mailbox with the judgement.

Bind the gate to the exact resource and action, include the exact diff or command, and continue on
its continuation event. Two rules follow from that binding:

- Finish the bound document **before** opening the gate. Every later revision expires it and burns
  a decision round; two gates were lost to exactly that.
- One escalation per decision. Do not poll, do not open a second gate while the first is pending,
  and do not duplicate an interaction on silence.

## Staging autonomy is currently dormant

The policy intent remains that staging actions do not need an owner gate. There is currently no
sanctioned staging mutation path: guarded `TARGET=staging` commands fail closed
until a separate safe non-production guard exists. The standing keygate identity does not override
that decision.
The former `make … TARGET=staging` mutation path is now fail-closed, not a capability to request.

Do not turn the missing path into an owner gate, and do not ask the operator for host-level Incus,
systemd, Ansible, or a hand-run `make` workaround. Record the blocked delivery and wait for the
separate guard. The machine boundary remains in `kira-host-boundary`.

## Missing capability

Access is meant to be standing — the company's `grants.yaml`. If a capability is genuinely missing,
raise a missing-capability escalation naming the concrete ask, rather than minting access, fanning
out a workaround, or sitting `blocked` in silence. Expansion beyond the standing grants is owner
class 5.

**One refused verb is not proof that no path exists.** Before reporting that the platform cannot do
something, enumerate the operations the resource actually offers and try the one that fits. A stale
pending confirmation returned 422 on `cancel` and was carried as unclearable — until `reject`, a
sibling route on the same resource, closed it on the first attempt. The wrong belief cost an issue and
an owner confirmation.

The same applies when an operation is denied outright: a permission error (a 403, a refused
config write on another agent, anything requiring the container host) means the operation is
outside the rights of the **whole team** — rights here are scoped per role, not held by any one
role in full, so no colleague can do it for you and retrying or working around it only burns
runs. Record the exact denied operation and its error on the issue and escalate it to the owner;
platform-level surgery is his surface by design.

Handing a refused action to the colleague who does hold the right is correct — but a refusal on their
side ends the delegation. If they are denied the mirror action, the two denials together prove the
operation is outside the team's rights, and what looks like a dependency is a deadlock: escalate at
once, naming both. In July two roles each correctly refused to work around a `403` and each waited for
the other; the order would not have closed without the owner. A comment that cannot reach the other
issue raises no wake on it either, so nothing is coming to end the wait.

## Platform facts worth carrying

- Setting `assigneeUserId` to the board user is not a handoff, and an @mention of the owner is not a
  request. A decision for him travels as a gate bound to its resource; nothing else reaches him and
  nothing else leaves an auditable record.
- `blocked` alerts nobody. It is a planning state, so set it freely with the reason: the dependency,
  the missing input, and who clears it.
- Killing an issue follows one order — cancel, verify terminal, then hide. A hidden non-terminal
  issue is an invisible zombie that keeps running.

## Never escalate at all

Anything the pipeline rules or the roster already decide. Status, progress, FYI — the board shows
them. Anything answerable from the repository, the issue history, the authoritative docs, or a
bounded research task you can run yourself.
