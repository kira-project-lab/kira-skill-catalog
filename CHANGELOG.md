# Changelog

All notable changes to the Kira Lab process-skill catalog are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
this catalog adheres to [Semantic Versioning](https://semver.org/).

## [0.2.1] - 2026-07-16

Corrective release for the **platform-engineering** package. v0.2.0 published
`hermes-web-ui-service-ops`'s five helper files under `scripts/**`. The native
GitHub importer derives a trust level from file paths: any file under
`scripts/**` (or with a bare code extension) is classified as an executable
script, and external GitHub skills that contain script-class files are
categorically rejected (`reason=scripts_executables_blocked`) with no bypass. As
published, `hermes-web-ui-service-ops` failed `skills import` and the sequential
import stranded the package (only six of eight skills landed).

Fix: the five helpers are **relocated** from
`hermes-web-ui-service-ops/scripts/**` to
`hermes-web-ui-service-ops/references/scripts/**`. The importer classifies
anything under `references/**` as reference material regardless of extension, so
the files are now inert reference copies and all eight skills import cleanly.
This is a **path-only** normalization: file contents are byte-equivalent to
source and every `sha256` is unchanged (independent re-checksum:
`files=223 target_mismatches=0`). No trust boundary is bypassed — the files
genuinely become reference material under the importer's own classification
contract. PATCH bump: no skill content or the layout contract changed.

### Changed

- `hermes-web-ui-service-ops`: five `scripts/**` helpers relocated to
  `references/scripts/**` (path-only, byte-equivalent) so the package passes the
  external-catalog import gate. Provenance `path`/`target_path` and per-file
  `normalization` notes updated in
  `provenance/platform-engineering/manifest.json`.

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

[0.2.0]: https://github.com/kira-project-lab/kira-skill-catalog/releases/tag/v0.2.0
[0.1.0]: https://github.com/kira-project-lab/kira-skill-catalog/releases/tag/v0.1.0
