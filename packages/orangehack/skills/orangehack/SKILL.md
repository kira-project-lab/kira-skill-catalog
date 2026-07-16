---
name: orangehack
description: Use for any OrangeHack task involving the platform, landing page, hackathon operations, competitions, participant or organizer UX, APIs, data lifecycle, environments, deployments, monitoring, or production/stage verification. Supplies Maxim's durable OrangeHack constraints and routes work to project-local sources and focused engineering skills.
version: 1.0.0
author: Kira
license: MIT
metadata:
  hermes:
    tags: [orangehack, product, platform, hackathon, deployment, qa]
    related_skills: [codegraph-first, production-webapp-diagnostics, product-demo-fixtures]
---

# OrangeHack

## Authority

Project-local version-controlled documentation, the canonical GitHub repository/ref, live environment state, APIs, databases, and original event documents own OrangeHack truth. This skill owns stable cross-project constraints and routing only.

When similarly named checkouts, events, or documents exist, verify identity before acting. Do not substitute adjacent hackathon materials for the named event.

## Product and engineering stance

Prefer product-level fixes across domain, API, lifecycle, and UX over narrow visual patches that preserve a broken rule underneath.

Before CI/CD troubleshooting, reproduce manually at the failing layer. For code work, inspect the canonical repo/ref, project instructions, actual runtime, and affected tests. Preserve unrelated changes and use merge-based branch synchronization unless the project explicitly specifies another flow.

## Hard constraints

- Create or configure competitions on `app.orangehack.ru` only when Maxim explicitly asks.
- Keep internal identifiers and labels such as `HCK-ALFA` out of participant-facing and Git-visible surfaces unless the named project source explicitly requires them.
- Historical identity for deleted entities belongs in payload or aggregate identity fields; nullable foreign keys reference only currently live rows and become `NULL` when the entity is gone.
- A private competition or event can legitimately be absent from anonymous public endpoints; verify through the authenticated/admin path before diagnosing data loss.
- Stage work must use the branch and environment named in the latest instruction. Do not sync or pull secondary machines such as `werserk-laptop` unless asked.

## Delivery workflow

1. Identify the product surface, user role, environment, canonical repo, branch/ref, and source document.
2. Reproduce the exact user scenario in the same auth and environment context.
3. Trace the rule across frontend, API/schema, application/domain, persistence, and audit/lifecycle boundaries as needed.
4. Add the smallest test that expresses the real product contract before changing behavior.
5. Implement a scoped product-level fix and run focused plus relevant broader gates.
6. Verify locally with the real runtime/API/UI on a clean pull or reproducible checkout when relevant.
7. For stage or production, verify the live commit/version, frontend, API/health, monitoring, and key flows with a real browser and representative users or teams.
8. Update project documentation or explicitly record that the actual diff needs no durable documentation change.

## Completion standard

Do not claim deployment or launch success from CI, a container restart, or a single HTTP 200. Evidence should cover the applicable public URL, frontend render, API/health/version, live commit, authentication/roles, and the named participant/organizer flow.

For hackathon program or participant materials, keep internal commercial/legal context separate from participant instructions, verify dates and source precedence, and prefer concise operational outputs over generic event prose.

## Routing

Use only the focused skills needed:

- code relationships and blast radius → `codegraph-first`;
- root-cause bug work → `systematic-debugging`;
- contract-first behavior changes → `test-driven-development`;
- production symptom/API diagnosis → `production-webapp-diagnostics`;
- safe local users/teams/competitions → `product-demo-fixtures`;
- hackathon briefs/rubrics/materials → `hackathon-program-briefing`;
- browser QA → the project's browser/testing skill and real browser tools;
- repository documentation closure → `project-culture`.
