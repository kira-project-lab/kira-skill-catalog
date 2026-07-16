# Upstream sync certification matrix

Use when a Hermes Web UI upstream integration feels broadly broken after deploy/preview: session order changes, features disappear, commands stop working, or UI/runtime behavior regresses despite build/tests passing.

## Core lesson

Treat this as a **failed certification process**, not only as individual bugs. A long-lived downstream fork needs an explicit integration risk report and product-contract certification before promotion.

A green `npm run build` or even a partially green test suite is not enough for broad upstream adoption. Certification must prove that Kira's downstream product contracts still hold on the integrated branch.

## Integration Risk Report

Before repairing or promoting a large upstream sync, produce a compact report with:

| Area | Upstream changed | Kira downstream layer | Conflict/risk | Existing gate | Missing gate | Decision |
|---|---|---|---|---|---|---|
| Sessions/prefs | ... | ... | ... | ... | ... | keep upstream / reapply Kira / redesign |

Classify at least these areas:

- session order, pinned sessions, tags/badges, cross-device prefs;
- new chat flow and durable session creation;
- Hermes / Claude Code / Codex conversation start;
- slash commands, `/yolo`, approvals, run lifecycle;
- profile/env isolation and bridge broker routing;
- Paperclip entrypoint and BFF/API routes;
- Skills/static public assets fetched at runtime;
- model/provider selectors and auxiliary model routing;
- auth/login/refresh and stale-token recovery;
- voice/STT/TTS if touched;
- mobile parity and key navigation surfaces;
- deploy/topology/health metadata.

## Certification Matrix

For each protected contract, define evidence at the smallest useful level:

- **source contract**: DOM/API strings, route names, public asset paths, i18n keys, removed/added selectors;
- **server integration**: DB schema, API behavior, profile scoping, migration/merge semantics;
- **client store/component**: state projection, sorting, filtering, UI fallback behavior;
- **Playwright/browser**: real route renders, user action works, console clean;
- **live-dev/preview**: `/health` reports the exact branch/commit being certified;
- **real-data smoke** where relevant: session list/prefs should be checked against a copy or read-only snapshot of realistic Hermes/Web UI DB state, not only synthetic empty fixtures.

Minimum certification rows for broad upstream sync:

| Contract | Required evidence |
|---|---|
| Session chronology | server/client comparator tests + live list smoke with old roots and recent activity |
| Pinned/tags | prefs DB tests + localStorage backfill test + browser smoke |
| Runtime commands | `/yolo`, fork/reload/approval command tests + bridge routing tests |
| Coding agents | Claude Code/Codex start tests + browser start smoke |
| Profile isolation | HERMES_HOME/profile env tests + profile-specific model/provider smoke |
| Static assets | `packages/client/public` diff review + curl/browser fetch for runtime assets |
| Paperclip | route/API test + browser entrypoint smoke |
| Auth | login + refresh + `/api/auth/me` smoke |

## Recommended response to a bad integration

1. Freeze `origin/main` on the last stable version.
2. Keep broken integration in `integration/upstream-<version>` / `origin/dev`; do not delete it until inspected.
3. Produce the Integration Risk Report before writing more fixes.
4. Decide whether to repair current branch or rebuild from `upstream/main` in layer commits.
5. If rebuilding, apply layers in small commits and run targeted gates after each layer.
6. Promote only after the certification matrix is fully PASS or explicitly waived by Maxim.

## Pitfalls

- Do not describe the problem as “a few regressions” when multiple unrelated product contracts failed; that hides the real process failure.
- Do not use live browser QA to discover basic known-red contract failures. Stabilize local/source/server tests first, then use browser QA as final evidence.
- Do not rely only on synthetic fixtures for session-list correctness. The high-risk bugs appear with old sessions, child chains, pins/tags, claims, and migrated browser prefs.
- Do not merge to `main` because the version bump is desirable. Version metadata is last; product-contract certification comes first.
