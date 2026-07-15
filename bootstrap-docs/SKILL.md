---
name: bootstrap-docs
description: Bootstrap engineering-culture docs in a new project — CLAUDE.md, AGENTS.md, CONTRIBUTING.md, docs/adr with a real ADR 0001 recording the initial architecture. Use for greenfield repos with no docs conventions yet.
---
<!-- vendored from werserk/dev-culture@3fc1388 — edit there and re-run scripts/vendor.sh -->

Bootstrap the documentation culture in this repo. Templates live in this skill's `references/`.

## Ground rule

Every file you write must describe this repo **as it actually is**. Never leave `<PLACEHOLDER>` text in a written file — discover the facts from the repo, and interview the user for what you cannot discover.

## Steps

1. **Guard.** Check what already exists (`CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, any ADR dir). If the repo already has substantial docs culture, stop and suggest the `adopt-repo` skill instead. Never overwrite an existing file without showing the user what would be lost.

2. **Discover facts.** From the repo: stack, package manager, run/test/lint commands (manifests, lockfiles, Makefile, CI config), directory layout, default branch. From the user (ask in ONE batch, only what's undiscoverable): project one-liner and audience, environments (dev/stage/prod) and what's off-limits, supported locales, delivery flow preference, and the *why* behind the initial stack choices.

3. **Scaffold** from templates, filled with the discovered facts:
   - `CLAUDE.md` ← `references/CLAUDE.md.tmpl` — project facts, working rules, and the **documentation contract** section (keep it verbatim in spirit: trigger table + "task not complete until the docs decision is stated").
   - `AGENTS.md` ← `references/AGENTS.md.tmpl` — one-page operating map.
   - `CONTRIBUTING.md` ← `references/CONTRIBUTING.md.tmpl` — branch flow, conventional commits, definition of done. If the project wants batch owner review, set up the dev/main train flow with the `git-workflow` skill (`scripts/git-workflow-init.sh` in this repo scaffolds it).
   - `docs/adr/README.md` ← `references/adr-index.md` — index + rules.

4. **Write ADR 0001 — a real one.** `docs/adr/0001-<stack-slug>.md` from `references/adr.md`: the initial stack/architecture choices with the user's actual reasons (from step 2), alternatives they considered, status `Accepted — <today>`. The culture starts with a genuine artifact, not empty folders. Add it to the index.

5. **Report.** List created files, then remind: daily workflow is the `adr` skill for decisions and the `wrap-up` skill to close tasks. Offer to commit (`docs: bootstrap engineering docs and ADR 0001`).
