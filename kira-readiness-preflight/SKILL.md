---
name: kira-readiness-preflight
description: The readiness gate every Kira Lab direction passes before it spawns implementation — a six-category base check (access, naming, secrets, infra, decisions, substrate) that is fail-closed on access and secret references. Use when decomposing a [direction], before marking any implementation issue actionable. Enforces ADR 0057.
---

# Readiness preflight (ADR 0057)

A direction must prove its **base** is resolvable before anyone writes code. The failure this
prevents: building a large amount of implementation and only then hitting a fact that was knowable
up front — an action no principal can run, a secret that never existed, a name that collides, a
decision still open. Discover the base by *checking* it, not by hitting it mid-build.

You (CEO / director) file one **Readiness Manifest** as a document on the `[direction]` issue
before marking any implementation issue actionable.

## The manifest — six categories

Every line is marked one of: `self-serviceable` · `owner-gated` · `deferred(reason)`.

1. **Access / capability** *(hard gate)* — for every **terminal action** the plan will perform
   (host converge, prod mutation, external API call, secret read, control-plane mutation), resolve
   a concrete `(principal, grant, key/route)` triple against the live roster, grants, and keygate
   registry. If an action has **no authorized holder**, it is `owner-gated` — escalate now, do not
   plan around it silently.
2. **Naming** — canonical names/slugs the work creates or references: domains, repos, branches,
   env-keys, **ADR numbers**, service names. Derivable from existing config → `self-serviceable`;
   otherwise → `owner-gated`.
3. **Secret references** *(hard gate)* — every required secret exists as a **reference** in the
   target scope (never a value). Missing → `owner-gated` provision request.
4. **Infra / endpoints** — hosts, ports, DNS, certs that must pre-exist.
5. **Decisions / interview** — open owner decisions (rights posture, topology, scope) closed up
   front, not litigated mid-build.
6. **Acceptance substrate** — the environment the acceptance criteria actually run on is reachable,
   or a mock is explicitly owner-signed-off.

## The gate

- **Fail-closed on #1 and #3.** No implementation issue leaves `todo`, and no implementation run
  starts, while any **access** or **secret-reference** line is unresolved and not
  `deferred(reason)`. These are the two classes that cost real wall-clock when discovered mid-build.
- **Advisory on #2/#4/#5/#6.** Recorded and surfaced, never blocking — planning must not drown in
  the base check.

## One owner intake

Batch **every** `owner-gated` line into a single packet routed through Kira / `kira-gate-sweep`:
context, real options, your recommendation, and exactly what is blocked. One intake per direction —
not a page per discovery. Implementation stays blocked on that intake; it is not restarted per line.

## The capability preflight (the load-bearing check)

For category 1, prose is not enough. Walk each terminal action to its authorized holder:

- Does a roster principal hold the required grant? Check the grants, not the title.
- Can that principal actually execute it? A forced-command / `permitopen` keygate line that can
  forward but not run a shell is **not** authorization for a host converge.
- No holder → record "dead-ends at an unauthorized action → escalate" as an `owner-gated` line
  **at planning time**.

## Boundaries

- The preflight resolves the base; it does not grant, name, or decide owner-gated lines — that is
  the owner's answer through the intake.
- Forward-only: do not retrofit manifests onto in-flight directions.
- The board-side backstop is the `kira-readiness-watchdog` routine (blocks implementation that
  started with an unresolved hard-gate line); this skill is the author-time contract.

## Worked failure (why this exists)

The KIR-298 production line terminated in a physical-host `kira_hosts` converge of
`ansible/stagegate.yml` that **no principal in the roster was authorized to run** — the standing
key was forced-command, no grant covered a host converge. That was derivable from the roster before
any code. Instead it surfaced only when an agent hit `incus: command not found`, after a stagegate
harness had been built, reviewed three times, cancelled, and re-architected — and the owner escalation
(authorize a bounded host-bootstrap capability) landed ~6 h and one abandoned build-line late. A
category-1 line on the manifest would have escalated it at planning time.
