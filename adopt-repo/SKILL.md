---
name: adopt-repo
description: Staged adoption of docs culture in an existing repo — survey first, "architecture as found" ADR 0001, a few retroactive ADRs for load-bearing decisions, as-is CLAUDE.md with forward-only rules. Use for inherited codebases with weak or absent documentation culture.
---
<!-- vendored from werserk/dev-culture@3fc1388 — edit there and re-run scripts/vendor.sh -->

Adopt this repo into a documentation culture — **staged, ratchet not gate**. The failure mode to avoid: dumping an idealized ruleset on a repo that contradicts it, then watching it get ignored. Rules apply forward, to new work; there is no retrofitting sweep.

Templates live in this skill's `references/`.

## Stage 1 — Survey (no writes to repo docs yet)

Map the repo as it actually is: stack and real run/test/lint commands (verify against manifests/CI, not README claims — note where README lies), directory layout and ownership boundaries, undocumented conventions the code actually follows, environments/deploy reality, and **where decisions are currently buried** (commit messages, PR threads, config archaeology). Use `git log` to find the load-bearing decisions people keep re-litigating.

Output: an adoption report at `docs/audit/<today>-adoption-survey.md` (create dirs as needed) — evidence-backed findings, no fixes yet. Present it to the user before Stage 2.

## Stage 2 — ADR 0001: "Architecture as found"

Create `docs/adr/` + index (`references/adr-index.md` template), then write `docs/adr/0001-architecture-as-found.md`:

- Status: `Accepted — <today>` with the explicit line: **"Descriptive, not endorsed: this records the status quo so future ADRs have something to supersede."**
- Context: how the repo got here, as far as discoverable.
- Decision: the de-facto architecture, stated plainly, warts included.
- Consequences: the known pain points from the survey.

This legitimizes the ADR log without pretending the past was deliberate.

## Stage 3 — Retroactive ADRs (max 5, confirmed only)

From the survey, propose up to 5 retroactive ADRs for load-bearing decisions — the ones that keep getting re-litigated or would burn a newcomer. Ask the user which to write (one batch). Write only the confirmed ones, numbered 0002+, status noting they are retroactive records.

## Stage 4 — Forward-only contract

- `CLAUDE.md` from `references/CLAUDE.md.tmpl` — describing the repo **as it is** (real commands, real quirks, known lies in old docs) plus the documentation contract, framed forward-only: *"from now on, every substantial change states its docs decision."* If a `CLAUDE.md` exists, merge the contract in; don't clobber working instructions.
- `AGENTS.md` / `CONTRIBUTING.md` from templates only if missing and the user wants them.
- If the owner wants batch review instead of per-PR review, propose the dev/main train flow (`git-workflow` skill) as part of the contract.
- Explicitly list what is NOT required: no doc backfill for old code, no gate on existing debt.

## Report

Summarize: survey path, ADRs written, contract location. Daily workflow from here: the `adr` and `wrap-up` skills. Offer to commit per repo conventions.
