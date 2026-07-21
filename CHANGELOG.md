# Changelog

All notable changes to the Kira Lab process-skill catalog are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
this catalog adheres to [Semantic Versioning](https://semver.org/).

## [0.5.0] - 2026-07-21

Adds the two remaining review-quality guards from the Kira Lab cycle audit (kira-platform
ADR 0052). MINOR bump: backward-compatible additions to two existing process skills.

### Changed

- `kira-dev-pipeline`: new **Grounded verdicts** rule — a native review decision (either
  outcome) is valid only with executed checks and quoted meaningful output, or a stated
  reason plus substitute evidence; diff-only reasoning is not review.
- `kira-issue-contract`: new **Rule five — a contract change is a boundary, never a
  drift** — mid-flight acceptance-criteria changes require a visible amendment with
  post-change reviews judged only against the updated contract, approvals that name the
  exact artifact (PR head SHA or document revision), or cancel-and-reopen when the
  approach itself is invalidated (KIR-299 retrospective).

## [0.4.1] - 2026-07-20

Corrective clarification for the anti-loop review rule added in v0.4.0. PATCH bump: no
threshold or capability changes; this makes the existing review authority, occurrence
counting and advisory accountability explicit.

### Changed

- `kira-dev-pipeline`: define an occurrence as a native review decision, keep focused
  diagnosis children analysis-only and subordinate to the native review stage, and align
  third-occurrence Kira consultation with `kira-ask-kira` by leaving the recorded
  disposition with the accountable pipeline owner.

## [0.4.0] - 2026-07-20

Extends the existing Kira Lab development pipeline with a bounded anti-loop rule for
repeated review findings. MINOR bump: this adds backward-compatible review and escalation
behavior to an existing process skill without changing the catalog layout or removing any
capability.

### Changed

- `kira-dev-pipeline`: identify repeated findings by the unmet acceptance criterion or
  invariant, use normal remediation for the first occurrence, require a blocking focused
  diagnosis for the second, and route the third to Kira for an operational disposition
  before any further tactical remediation.

## [0.3.0] - 2026-07-16

Adds the **orangehack** package: three OrangeHack executor skills published so
they live outside the cognitive profile. Skills are copied from
`kira-project-lab/kira-profile` `dev` @
`c75d4631030011f4c7c9915dae4233e21a24a7f9` with **path-only** normalization
(source `skills/<category>/<slug>/**` → top-level `<slug>/**`); contents are
**byte-equivalent** except one documented content change: the `orangehack`
routing skill's `SKILL.md` gains an appended `## Bundled context` section that
links its two relocated context groups by valid relative paths. Those two
context groups — the OrangeHack project sources and roadmap — are published under
the owning routing skill's `references/` (path-only, byte-equivalent) so the
context travels with, and is discoverable from, the skill. Per-file `sha256`
checksums (with `source_sha256` before / `sha256` after for the deviating file),
the source→target mapping, and per-file normalization notes are recorded in
`provenance/orangehack/manifest.json`; ownership stays with Kira Lab. No
credentials, organizer-only data, or runtime state are included. MINOR bump:
additive only, no existing skill or the layout contract changed.

### Added

- `orangehack` — routing skill for OrangeHack platform / hackathon / competition
  work; carries the OrangeHack project sources and roadmap under `references/`.
- `hackathon-program-briefing` — design and prepare hackathon / ML-competition
  program and participant-facing materials.
- `ml-competition-data-ops` — design and operate ML competition data/scoring
  packs with organizer-only safeguards.
- `provenance/orangehack/` — package README and machine-checkable checksum manifest.

## [0.2.1] - 2026-07-16

Corrective release for the **platform-engineering** package published in v0.2.0.

1. **Import compatibility.** v0.2.0 published `hermes-web-ui-service-ops`'s five
   helper files under `scripts/**`. The native GitHub importer derives a trust
   level from file paths: any file under `scripts/**` (or with a bare code
   extension) is classified as an executable script, and external GitHub skills
   that contain script-class files are categorically rejected
   (`reason=scripts_executables_blocked`). The five helpers are **relocated** to
   `hermes-web-ui-service-ops/references/scripts/**`, which the importer
   classifies as reference material, so all eight skills import cleanly.
2. **Broken helper commands.** After the relocation the documented invocation
   commands still pointed at the absent `scripts/<name>` paths. The six affected
   references (`hermes-web-ui-service-ops/SKILL.md`, three reference docs, and
   the example usage headers inside `bridge_latency_benchmark.py` and
   `codex_bridge_trace.py`) are repointed to `references/scripts/<name>` so the
   commands resolve in the catalog.
3. **Credential redaction.** The Hermes Web UI built-in bootstrap default login
   pair (default admin user / numeric default password) still appeared as a
   literal in four references. It is replaced with `<username>` / `<password>`
   placeholders so **no credential value appears anywhere in the catalog**,
   including the provenance subtree.
4. **Provenance before/after hashes.** Every deviating file's manifest entry now
   records both `source_sha256` (before, resolved at the source commit) and
   `sha256` (after, published bytes) with a per-file `normalization` reason.

Independent re-checksum: `files=223 target_mismatches=0`. PATCH bump: no skill
was added or removed and the layout contract is unchanged.

### Changed

- `hermes-web-ui-service-ops`: five `scripts/**` helpers relocated to
  `references/scripts/**` (path-only, byte-equivalent) so the package passes the
  external-catalog import gate.
- Repointed six documented `scripts/<name>` helper references to
  `references/scripts/<name>` (`hermes-web-ui-service-ops/SKILL.md`,
  `references/webui-chat-latency-context-split.md`,
  `references/vm-webui-provider-latency-benchmark.md`,
  `references/prod-to-dev-state-snapshot-mirror.md`, and the usage headers in
  `references/scripts/bridge_latency_benchmark.py` and
  `references/scripts/codex_bridge_trace.py`).

### Security

- Redacted the Hermes Web UI built-in bootstrap default login pair to
  `<username>` / `<password>` placeholders in
  `hermes-web-ui-service-ops/references/session-url-inspection.md`,
  `hermes-web-ui-service-ops/references/beta-10-vm-acceptance-execution.md`,
  `hermes-web-ui-service-ops/references/isolated-user-profile-webui.md`, and
  `hermes-web-ui-operating-model/references/kira-beta-10-vm-acceptance.md`. No
  credential value remains anywhere in the catalog.

### Provenance

- `provenance/platform-engineering/manifest.json`: added `source_sha256`
  (before) alongside `sha256` (after) for every deviating file, updated target
  hashes and `normalization` reasons for the content changes above, and refreshed
  the top-level normalization summary. `provenance/platform-engineering/README.md`
  documents the full before/after set and the two intentionally-unchanged
  upstream-package-relative references.

## [0.2.0] - 2026-07-16

Adds the **platform-engineering** package: eight Hermes / platform executor
skills published so they live outside the cognitive profile. Skills are copied
from `kira-project-lab/kira-profile` `dev` @
`c75d4631030011f4c7c9915dae4233e21a24a7f9` with **path-only** normalization
(source `skills/<category>/<slug>/**` → top-level `<slug>/**`); contents are
**byte-equivalent** except three documented, safety-driven changes: an
operational login literal redacted to placeholders, a nested `SKILL.md` renamed
to `OVERVIEW.md` so it cannot be mis-imported as a ninth skill, and the one
citation of that file updated to match. Per-file `sha256` checksums, the
source→target mapping, and per-file normalization notes are recorded in
`provenance/platform-engineering/manifest.json`; ownership stays with Kira Lab.
No credentials or runtime state are included. MINOR bump: additive only, no
existing skill or the layout contract changed.

### Added

- `debugging-hermes-tui-commands` — debug Hermes TUI slash commands.
- `hermes-codex-debugging` — debug Kira's own Hermes Agent / Codex stack.
- `hermes-provider-troubleshooting` — Hermes Agent provider/auth/routing/billing failures.
- `hermes-token-economy` — analyze and reduce Kira agent token usage.
- `hermes-web-ui-live-dev` — operate Hermes Web UI live-dev runtime.
- `hermes-web-ui-operating-model` — entrypoint for Hermes Web UI planned work.
- `hermes-web-ui-service-ops` — runtime/live-service companion for Hermes Web UI.
- `hermes-web-ui-upstream-sync` — update Kira's Hermes Web UI fork from upstream.
- `provenance/platform-engineering/` — package README and machine-checkable checksum manifest.

## [0.1.0] - 2026-07-15

Seed release: publishes the ten canonical Kira Lab process skills as a
versioned catalog. Skills are copied semantic-preserving from the company skill
library; support files (`references/**`, templates) travel with each `SKILL.md`.

### Added

- `adopt-repo` — staged adoption of docs culture in an existing repo.
- `adr` — scaffold a new Architecture Decision Record.
- `bootstrap-docs` — bootstrap engineering-culture docs in a new project.
- `git-workflow` — dev/main branching with promotion trains.
- `kira-ask-kira` — conditional Kira consultation discipline.
- `kira-dev-pipeline` — how Kira Lab ships code (stages, branches, release).
- `kira-escalation-discipline` — Kira Lab escalation boundaries.
- `kira-issue-contract` — the executable Kira Lab issue template.
- `kira-learning-loop` — how Kira Lab learns from its own failures.
- `wrap-up` — end-of-task closure and docs decision.

[0.4.1]: https://github.com/kira-project-lab/kira-skill-catalog/releases/tag/v0.4.1
[0.4.0]: https://github.com/kira-project-lab/kira-skill-catalog/releases/tag/v0.4.0
[0.3.0]: https://github.com/kira-project-lab/kira-skill-catalog/releases/tag/v0.3.0
[0.2.1]: https://github.com/kira-project-lab/kira-skill-catalog/releases/tag/v0.2.1
[0.2.0]: https://github.com/kira-project-lab/kira-skill-catalog/releases/tag/v0.2.0
[0.1.0]: https://github.com/kira-project-lab/kira-skill-catalog/releases/tag/v0.1.0
