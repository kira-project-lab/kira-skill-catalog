---
name: adr
description: Scaffold a new Architecture Decision Record — next number, repo-matching style, index update, supersede cross-links. Use when a decision changes runtime behavior, API contracts, data ownership, deployment model, or security/permission boundaries.
argument-hint: [decision-title]
---
<!-- vendored from werserk/dev-culture@3fc1388 — edit there and re-run scripts/vendor.sh -->

Create a new ADR for: **$ARGUMENTS** (if empty, derive the title from the decision just made in this conversation; if no decision is identifiable, ask).

## Steps

1. **Locate the ADR directory.** Check, in order: `docs/adr/`, `docs/adrs/`, `docs/decisions/`, `adr/`. If none exists, offer to create `docs/adr/` and seed its `README.md` from `references/adr-index.md` (fill in the project name).

2. **Match local style.** Read the index README and the 1–2 most recent ADRs. New ADRs must match the existing repo's structure, tone, and filename convention — the bundled template is the fallback for repos with no ADRs yet: `references/adr.md`.

3. **Pick the next number.** Highest existing number + 1, zero-padded to match (default `NNNN`). Filename: `NNNN-kebab-case-slug.md`.

4. **Write the ADR.** Sections (adapt to local style): Status, Date, Context, Decision (numbered sub-decisions if composite), Consequences, Alternatives considered, Validation.
   - Status is `Proposed — <today>` unless the decision is already implemented/agreed in this session — then `Accepted — <today>`.
   - Context must cite evidence: file paths, endpoints, audit reports, incidents. No vague "we felt".
   - Fill every section with real content from the conversation/codebase. Never leave template placeholders in the written file.

5. **Cross-link supersedes.** If this decision reverses or amends an earlier ADR: state it in this ADR's Status line, AND edit the old ADR's Status to `Superseded by NNNN` (link both ways). Never rewrite the old ADR's body.

6. **Update the index.** Add a row to the index README's table: number (linked), status, one-sentence decision summary. Keep rows in numeric order.

7. **Report.** One line: path of the new ADR + its status + any superseded ADRs touched. If the ADR should be committed, follow the repo's CONTRIBUTING conventions.
