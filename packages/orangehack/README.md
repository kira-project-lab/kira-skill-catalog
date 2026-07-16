# OrangeHack package

Executable OrangeHack materials — three skill trees and two planning-context
groups — published out of the Kira cognitive profile so they live in a
reviewable, independently verifiable Git source with pinned provenance.

/ **Ownership:** OrangeHack. These materials describe how to run the OrangeHack
hackathon / ML-competition program; they are executive/operational content, not
part of the Kira cognitive core. Kira proposes changes → the OrangeHack owner
confirms.

## Provenance

| Field | Value |
| --- | --- |
| Source repo | [`kira-project-lab/kira-profile`](https://github.com/kira-project-lab/kira-profile) |
| Source branch | `dev` |
| Source commit (SHA) | `c75d4631030011f4c7c9915dae4233e21a24a7f9` |
| Files | 22 (byte-equivalent to source) |
| Machine-checkable manifest | [`provenance.json`](provenance.json), [`CHECKSUMS.sha256`](CHECKSUMS.sha256) |

Every file below was copied **verbatim** from the source commit. The only
change is the path prefix — see [Normalization](#normalization). Verify at any
time from this directory:

```sh
sha256sum -c CHECKSUMS.sha256
```

## Contents

Three skill trees:

| Skill (slug) | Path | Support files |
| --- | --- | --- |
| `orangehack` | [`skills/orangehack/SKILL.md`](skills/orangehack/SKILL.md) | — |
| `hackathon-program-briefing` | [`skills/productivity/hackathon-program-briefing/SKILL.md`](skills/productivity/hackathon-program-briefing/SKILL.md) | `references/**` (12) |
| `ml-competition-data-ops` | [`skills/data-science/ml-competition-data-ops/SKILL.md`](skills/data-science/ml-competition-data-ops/SKILL.md) | `references/**` (2) |

Two planning-context groups:

| Group | Path | Files |
| --- | --- | --- |
| OrangeHack projects | [`projects/orangehack/`](projects/orangehack/) | `_sphere.md`, `hackathon.md`, `landing.md`, `platform.md` |
| OrangeHack roadmap | [`roadmaps/orangehack.md`](roadmaps/orangehack.md) | 1 |

## Layout & import path

The seeded catalog convention (v0.1.0) discovers a skill **wherever it finds a
`<slug>/SKILL.md`**, taking the immediate parent directory name as the slug.
This package keeps its own self-contained subtree under `packages/orangehack/`
so it stays disjoint from the top-level process skills and from the sibling
`packages/platform-engineering/**` package. Each skill's immediate parent
directory still equals its slug, so native discovery resolves the three skills
as `orangehack`, `hackathon-program-briefing`, and `ml-competition-data-ops`:

```
packages/orangehack/
  README.md
  provenance.json          # machine-checkable source ref + per-file sha256
  CHECKSUMS.sha256         # sha256sum -c manifest
  skills/
    orangehack/SKILL.md
    productivity/hackathon-program-briefing/{SKILL.md,references/**}
    data-science/ml-competition-data-ops/{SKILL.md,references/**}
  projects/orangehack/{_sphere,hackathon,landing,platform}.md
  roadmaps/orangehack.md
```

Import (provenance pins to the resolved commit; run by the release owner):

```sh
pnpm paperclipai skills import https://github.com/kira-project-lab/kira-skill-catalog \
  --company-id "$PAPERCLIP_COMPANY_ID" --json
```

## Normalization

**Path-only.** Every file was moved verbatim to `packages/orangehack/<original
relative path>` (e.g. profile `skills/orangehack/SKILL.md` →
`packages/orangehack/skills/orangehack/SKILL.md`). No content byte was changed;
`provenance.json` records the source-relative path and sha256 of each file, and
`CHECKSUMS.sha256` proves byte-equivalence. This is the only normalization — it
is documented here so a reviewer can distinguish it from data loss.

## Not included (no leakage)

The package contains **exactly** the 22 scoped source files and nothing else —
no credentials, organizer-only data, or runtime state. Notably, the
`orangehack-local-validation-accounts.md` reference is *methodology* (how to
create local validation accounts and an RBAC pitfall); it embeds no credential
values, and the fixtures runbook it points to
(`docs/runbooks/local-validation-accounts.md`) is **not** part of the profile
source and is **not** migrated.
