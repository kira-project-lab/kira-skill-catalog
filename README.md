# kira-skill-catalog

A reviewable, versioned Git source for Kira Lab's canonical process skills. Each
release is tagged with [SemVer](https://semver.org/) so a company can import the
catalog and pin its provenance to an exact commit.

Release `v0.1.0` seeds the catalog with the ten canonical Kira Lab process
skills, copied semantic-preserving from the company skill library.

## Inventory

The catalog ships two groups of skills. Each group is byte-verifiable against
its documented source; the importer discovers every top-level `<slug>/SKILL.md`
regardless of group.

### Process skills (v0.1.0)

Ten canonical Kira Lab process skills, copied semantic-preserving from the
company skill library:

| Skill | Support files | Description |
| --- | --- | --- |
| [`adopt-repo`](adopt-repo/SKILL.md) | `references/**` (2) | Staged adoption of docs culture in an existing repo — survey first, "architecture as found" ADR 0001, a few retroactive ADRs for load-bearing decisions, as-is CLAUDE.md with forward-only rules. Use for inherited codebases with weak or absent documentation culture. |
| [`adr`](adr/SKILL.md) | `references/**` (2) | Scaffold a new Architecture Decision Record — next number, repo-matching style, index update, supersede cross-links. Use when a decision changes runtime behavior, API contracts, data ownership, deployment model, or security/permission boundaries. |
| [`bootstrap-docs`](bootstrap-docs/SKILL.md) | `references/**` (5) | Bootstrap engineering-culture docs in a new project — CLAUDE.md, AGENTS.md, CONTRIBUTING.md, docs/adr with a real ADR 0001 recording the initial architecture. Use for greenfield repos with no docs conventions yet. |
| [`git-workflow`](git-workflow/SKILL.md) | — | Dev/main branching with promotion trains — batch owner review of a cumulative diff instead of per-PR review, no-squash promotion, hotfix path, layered rollback. Use when working in a repo that has a dev branch, or when setting up the delivery flow for a project whose owner wants to review results, not every PR. |
| [`kira-ask-kira`](kira-ask-kira/SKILL.md) | — | Consult Kira only when the task explicitly asks for her or requires Kira-owned knowledge or memory. Kira advises; she does not implement or replace repository research. |
| [`kira-dev-pipeline`](kira-dev-pipeline/SKILL.md) | — | How Kira Lab ships code — decomposition, branches, the native review/approval stages, and release. Use when planning, decomposing, implementing, reviewing or releasing any engineering work. The Paperclip skill has the platform mechanics; this has only what is specific to this company. |
| [`kira-escalation-discipline`](kira-escalation-discipline/SKILL.md) | — | Kira Lab escalation boundaries for owner confirmations, structured product questions, and conditional Kira consultation. Use when a missing decision or protected action blocks delivery. |
| [`kira-issue-contract`](kira-issue-contract/SKILL.md) | — | The issue template every executable Kira Lab issue follows — outcome title, checkbox acceptance criteria, hard delivery gate, and the three rules that make an issue a contract. Use when creating, decomposing, or auditing any issue for agent execution. |
| [`kira-learning-loop`](kira-learning-loop/SKILL.md) | — | How Kira Lab learns from its own failures without learning from noise. Use when reviewing agent trajectories, classifying a defect, or proposing any change to a prompt, skill, or runtime. Required reading before any coaching proposal. |
| [`wrap-up`](wrap-up/SKILL.md) | — | End-of-task closure — review the diff, decide and state the docs decision (new ADR / update docs / none), verify doc consistency and commit hygiene. Use before declaring any substantial coding task complete. |

### Platform-engineering package (v0.2.0)

Eight Hermes / platform executor skills, published from
`kira-project-lab/kira-profile@c75d4631` so they live outside the cognitive
profile. Byte-equivalent to source apart from three documented, safety-driven
normalizations (one credential redaction, one nested-`SKILL.md` de-registration,
and its citation follow-through); per-file checksums, the source→target mapping,
and per-file normalization notes are in
[`provenance/platform-engineering/`](provenance/platform-engineering/README.md).

| Skill | Support files | Description |
| --- | --- | --- |
| [`debugging-hermes-tui-commands`](debugging-hermes-tui-commands/SKILL.md) | — | Debug Hermes TUI slash commands: Python, gateway, Ink UI. |
| [`hermes-codex-debugging`](hermes-codex-debugging/SKILL.md) | — | Debug Kira's own stack — Hermes Agent / Hermes Desktop connection or latency, Codex CLI/version errors, cross-machine backend reachability. Kira-specific companion to the universal systematic-debugging skill. |
| [`hermes-provider-troubleshooting`](hermes-provider-troubleshooting/SKILL.md) | `references/**` (1) | Troubleshoot Hermes Agent model provider, auth, routing, and billing failures — 400/401/429, provider path existence, and whether community PRs/issues already solve a Hermes backend problem. |
| [`hermes-token-economy`](hermes-token-economy/SKILL.md) | `references/**` (11) | Analyze and reduce Kira agent token usage: inspect live usage stores, separate input/output/cache/reasoning buckets, design lightweight tracing plugins, and find high-leverage savings without logging sensitive prompts. |
| [`hermes-web-ui-live-dev`](hermes-web-ui-live-dev/SKILL.md) | `references/**` (17) | Operate Hermes Web UI live-dev: persistent watch-based runtime, HMR, backend restart loop, runtime identity, and verification. |
| [`hermes-web-ui-operating-model`](hermes-web-ui-operating-model/SKILL.md) | `references/**` (90) | Mandatory entrypoint for Hermes Web UI planned work: branches, builds, previews, production deploys, runtime topology, and release/export decisions. |
| [`hermes-web-ui-service-ops`](hermes-web-ui-service-ops/SKILL.md) | `references/**` (82), `scripts/**` (5) | Mandatory runtime/live-service companion for Hermes Web UI work. Load for any task that touches, verifies, updates, restarts, diagnoses, or depends on a running dev/preview/prod service. |
| [`hermes-web-ui-upstream-sync`](hermes-web-ui-upstream-sync/SKILL.md) | `references/**` (9) | Update Kira's Hermes Web UI fork from upstream — compare fork vs upstream, plan/execute a version bump, reconcile `origin/dev` with `upstream/main`, maintain a long-lived downstream fork. |

## Layout

Each skill is a top-level directory whose name is the skill slug:

```
<slug>/
  SKILL.md          # required — frontmatter (name, description, …) + skill body
  references/**     # optional — templates and reference docs the SKILL.md cites
```

- `SKILL.md` is required in every skill directory and carries the YAML
  frontmatter (`name`, `description`, and any skill-specific hints) plus the
  skill body.
- `references/` holds the support files a skill depends on (index templates,
  ADR templates, `*.md.tmpl` scaffolds). Support files always travel with their
  `SKILL.md`; a skill is incomplete without them.
- The importer discovers a skill wherever it finds a `<slug>/SKILL.md`, so the
  set of top-level directories containing a `SKILL.md` is exactly the set of
  published skills.

## Versioning (SemVer)

The catalog is versioned as a whole under `MAJOR.MINOR.PATCH`:

- **MAJOR** — an incompatible change: removing or renaming a skill, or changing
  the directory/layout contract in a way that breaks existing imports.
- **MINOR** — a backward-compatible addition: a new skill, or a new support
  file / capability extension to an existing skill.
- **PATCH** — a backward-compatible content fix: wording, typo, or reference
  correction that does not change a skill's contract or layout.

Every published version corresponds to a Git tag `vMAJOR.MINOR.PATCH` on `main`.

## Contribution / update flow

1. Branch from a fresh `origin/main` (`feat/<KIR-id>-<slug>`).
2. Add or edit skills under their `<slug>/` directory, keeping `SKILL.md` and
   `references/**` together.
3. Add a new section to [`CHANGELOG.md`](CHANGELOG.md) for the release,
   choosing the version bump per the SemVer rules above.
4. Open one PR to `main`. A reviewer diffs against fresh `origin/main` and
   records the reviewed head SHA; the release owner confirms the live head
   matches that SHA before squash-merging.
5. After merge, tag the merge commit `vMAJOR.MINOR.PATCH` and publish the
   GitHub release. The tag is the pinned provenance an import resolves to.

## Native import / update

Import every skill in the catalog into a company from the merged GitHub source
(provenance is pinned to the resolved commit):

```sh
pnpm paperclipai skills import https://github.com/kira-project-lab/kira-skill-catalog \
  --company-id "$PAPERCLIP_COMPANY_ID" --json
```

Check whether imported skills are up to date against the source:

```sh
pnpm paperclipai skills check --company-id "$PAPERCLIP_COMPANY_ID" --json
```

When a new catalog version is tagged, re-running `skills check` reports the
available update and the per-skill `install-update` flow pulls it in. Because
provenance is pinned to the source ref, a re-import or update resolves to the
exact tagged commit rather than a moving branch head.
