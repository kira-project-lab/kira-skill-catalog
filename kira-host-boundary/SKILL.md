---
name: kira-host-boundary
description: The physical host is outside the company's reach — Incus, host systemd and Ansible converges are operator work, and asking the operator to run them by hand is not a workaround. Use when an acceptance criterion or a recovery step needs control of the machine the agents run on.
---

# The host is not yours

Everything the company does happens *inside* a container on `werserk-pc2-arch`. The machine
itself — its Incus instances, its systemd units, its Ansible converges — belongs to the
operator. This is not a permission that has yet to be granted. It is the shape of the system.

## What you cannot do, and why it will never work

- **Incus** — start, stop, restart or inspect any instance, including your own. There is no
  `incus` binary and no Incus socket on the agent host.
- **Host systemd** — no unit on the physical host is yours to start, stop or read.
- **Ansible converge against a live host** — the playbooks and the secrets they read are
  operator-side.
- **Anything needing root on `werserk-pc2-arch`.**

The standing hop key exists only to forward a port: it is pinned to
`command="/usr/bin/true"` with `permitopen="10.152.10.200:22"`. It is a
forwarder by construction, so no retry, no alternate invocation and no escalation converts it
into a shell. If a step needs the host, it needs a human, always.

## Staging autonomy does not create a delivery path

Staging autonomy remains a policy intent, not current authority to mutate it. There is currently
no sanctioned staging mutation path: guarded `TARGET=staging` commands fail closed
until a separate safe non-production guard exists. Do not open an owner gate to bypass that absence
and do not ask the operator to run the same mutation directly.

**Never run or request `incus start kira-staging`.** It brings up a second `hermes-gateway`
holding the *same* Telegram bot token as
production. On 2026-07-26 that is exactly what happened: the two instances fought over
`getUpdates` for 38 minutes, production logged 52 conflicts, and inbound owner messages in
that window may have been delivered to the staging instance instead. The board could not see
any of it. Cost paid; do not pay it again.
The generic `incus start` action against `kira-staging` is the same forbidden mutation.

## What to do instead

When a step, an acceptance criterion or a recovery path needs the host — or any operation the
platform denies you outright, such as editing another agent's configuration (rights are scoped
per role; no teammate holds them in full, so a 403 for you is a 403 for the company):

1. **Stop.** Do not design around it, do not fan out, do not retry the hop key.
2. **Hand it back as an out-of-scope finding** — a comment on the issue naming the exact
   command, why the company cannot run it, and what it would unblock.
3. **Set `blocked` with that reason**, or split the host-dependent part into its own issue
   marked operator-work. `blocked` pages nobody; that is fine and correct here.
4. **Continue with everything that does not depend on it.** A host dependency in one
   criterion does not stall the other five.

For a staging mutation, the exact blocked reason is the missing non-production guard. Wait for
that guard; do not recast the work as an operator hand-off or an owner confirmation.

## What you must not turn it into

Do not convert a host dependency into instructions for the operator to execute — not through
`ask_user_questions`, not through `request_confirmation`, not through a comment that reads
like a runbook. A structured question asking someone to run `incus`, `systemctl` or
`ansible-playbook` on their machine, then paste the output back, makes the owner the hands of
the board. That is the failure this skill exists to prevent, and it is how the 2026-07-26
incident began.

Asking the operator to **paste evidence they already have** is fine — a status line, a log
excerpt, a screenshot. Asking them to **change the machine** is not.

## The line, in one sentence

Inside the container and inside the repositories: yours. The machine underneath: theirs — and
a criterion that depends on it is an operator hand-off, not a task.
