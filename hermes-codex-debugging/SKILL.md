---
name: hermes-codex-debugging
description: "Use when debugging Kira's own stack — Hermes Agent / Hermes Desktop connection or latency issues, Codex CLI/version errors, cross-machine backend reachability, or when you must keep investigating despite limited tool access. Kira-specific companion to the universal systematic-debugging skill (which owns the general root-cause method)."
version: 1.0.0
author: Kira
metadata:
  hermes:
    tags: [debugging, hermes, codex, desktop, latency, connection, environment]
    related_skills: [systematic-debugging, hermes-provider-troubleshooting, hermes-desktop-operations]
    provenance: "Distilled from real session-history mining (SE2, 2026-07-04); see kira-platform ADR 0011."
---

# Hermes / Codex Debugging (Kira environment)

Apply the general method from **systematic-debugging** (root-cause first, tight red-capable
feedback loop, ranked hypotheses). This skill adds the **Kira-specific domain knowledge** that
generic debugging lacks — keep it OUT of the universal skill.

## When you lack tool access or cannot run verification

Limited access is NOT a reason to disengage. It changes *what* you deliver, not *whether* you
engage. When you cannot execute:

1. **Examine what you can** — described file paths, config contents, error text. Infer intended
   behavior from filenames/context (a cursor-theme config ⇒ a theme-application check; a
   window-manager config ⇒ window-behavior).
2. **Draft the verification** — write the exact script/command the user should run, with
   expected output. For a temporary check, draft it fully (safe `tempfile` path, designated
   prefix) even if you can't run it, and label it **ad-hoc verification, not suite-green**.
3. **Propose the observable success signal** — state precisely what a passing check would show.
4. **State the concrete, specific blocker** — not "I lack tools", but exactly what is
   unreadable/unrunnable, what user action or signal unblocks it, and whether a workaround exists.

A concise refusal that skips investigation is a liability. Brevity must reflect focused
diagnosis, not capitulation.

## Environment facts to retain

- **Hermes Agent / Hermes Desktop** — an agent system with a desktop client; users connect to
  the backend through Desktop, sometimes across machines (laptop → remote backend). Connection
  issues are multi-layered: client version mismatch, auth/token mismatch, transport/config,
  service discovery/endpoint resolution, or local network/proxy/firewall/DNS.
- **Codex** — CLI/app coding tool with model versioning. A `400 invalid_request_error` saying a
  model "requires a newer version of Codex" is a **client/version compatibility** issue, not a
  server/account problem. Likely fix: upgrade Codex — then confirm the client points at the
  correct backend/model; don't assume the upgrade alone was THE fix.
- **In-workspace tools** (use in Phase 1 when available): `search_files` (find error strings /
  trace calls), `read_file` (source with line numbers), `terminal` (tests, git history, repro),
  `web_search`/`web_extract` (research errors/docs), `delegate_task` (subagents for
  multi-component debugging).
- **Config/UI verification examples:** cursor-theme changes may need reload/logout, checkable via
  `gsettings get org.gnome.desktop.interface cursor-theme`; window-manager (Hypr) config changes
  are verified by observing the described symptom.

## Diagnosing Hermes ↔ Codex latency / connection issues

1. Establish reproducibility (every request vs. intermittent) and what structured logs/tracing
   already exist, at what log level — don't make the user fish blindly.
2. Ask: **local Codex instance or remote Codex service?** — this reshapes the root-cause search.
3. For latency, propose per-stage timestamp tracing on real sessions before any full
   instrumentation schema: request start → sent to Codex → first response byte → full response →
   Hermes post-processing/render.
4. Map deltas to hypotheses:
   - **(send → first response) slow** → Codex generation or network
   - **(first response → full response) slow** → Codex streaming or network
   - **(full response → Hermes processing) slow** → Hermes overhead
5. For connection failures, preview the decision tree from log signals: **401/403** → auth;
   **timeout** → network/firewall; **"model not found"** → config.
6. Request specific diagnostics, not vague back-and-forth: `codex --version`, desktop app version,
   exact failing command/action, full logs around the failure from both sides, whether it works
   on another machine.
7. **Defer** a permanent instrumentation/tracing schema until after analyzing one real
   problematic session — schema-first skips the investigation.
