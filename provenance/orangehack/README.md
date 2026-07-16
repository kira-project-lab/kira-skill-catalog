# orangehack package — provenance

The **orangehack** package publishes three OrangeHack executor skills plus their
supporting project and roadmap context into `kira-skill-catalog` so they live
outside the cognitive profile (`kira-project-lab/kira-profile`) while staying
independently reviewable and byte-verifiable against their source.

This directory is provenance metadata only. It contains no `SKILL.md`, so the
native importer does not treat it as a skill; the three skills themselves are
published as top-level `<slug>/` directories per the catalog layout
([root README → Layout](../../README.md#layout)).

## Source

| Field | Value |
| --- | --- |
| Source repo | `kira-project-lab/kira-profile` |
| Source ref | `dev` |
| Source commit | `c75d4631030011f4c7c9915dae4233e21a24a7f9` |
| Ownership boundary | Kira Lab owns these skills. Publishing here does **not** move ownership out of Kira Lab; the catalog is the reviewable distribution surface, `kira-profile` remains the editing origin. The OrangeHack materials are executive/operational content that Kira proposes changes to and the OrangeHack owner confirms. |

## Skills in this package

| Slug (catalog top-level) | Source path in `kira-profile` |
| --- | --- |
| [`orangehack`](../../orangehack/SKILL.md) | `skills/orangehack/**` (routing skill; also carries the relocated context groups below) |
| [`hackathon-program-briefing`](../../hackathon-program-briefing/SKILL.md) | `skills/productivity/hackathon-program-briefing/**` |
| [`ml-competition-data-ops`](../../ml-competition-data-ops/SKILL.md) | `skills/data-science/ml-competition-data-ops/**` |

## Normalization

The default transformation is **path-only**: source skills live under
`skills/<category>/<slug>/**` in `kira-profile`; they are published here as
top-level `<slug>/**` to match the catalog's flat, importer-discovered layout.
Of the 22 published files, **21 are byte-equivalent** to source and **1** (the
`orangehack` routing skill's `SKILL.md`) carries a documented content
normalization (is not byte-equivalent). Every file's `sha256` and its
`source_path → target_path` mapping is recorded in
[`manifest.json`](manifest.json). Every deviating file — content or path-only —
carries a per-file `normalization` reason **plus both hashes**: `source_sha256`
(before, resolved at the source commit) and `sha256` (after, the published
bytes). For path-only relocations the two hashes are equal; for the content
normalization they differ.

### Content normalization (1 file, not byte-equivalent)

1. **Routing-link integration delta** — `orangehack/SKILL.md` gains one appended
   `## Bundled context` section that links both relocated context groups by
   valid relative paths (`references/projects/orangehack/` and
   `references/roadmaps/orangehack.md`) so the context travels with, and is
   discoverable from, its owning routing skill. The entire source body above the
   appended section is byte-identical, so `source_sha256` (before) and `sha256`
   (after) differ only by that trailing section.

### Path-only relocations (byte-equivalent, `source_sha256 == sha256`)

2. **Context groups travel with the owning skill** — the two OrangeHack context
   groups do not live under a `skills/<slug>/` tree in source; they are published
   under the `orangehack` routing skill's `references/` so they import as
   reference material bound to that skill instead of as loose top-level content:
   - `projects/orangehack/**` (4 files: `_sphere.md`, `hackathon.md`,
     `landing.md`, `platform.md`) → `orangehack/references/projects/orangehack/**`;
   - `roadmaps/orangehack.md` → `orangehack/references/roadmaps/orangehack.md`.

   The relocation changes only the `target_path`; the file bytes are identical to
   source (`source_sha256 == sha256`).

### No credentials, organizer-only data, or runtime state

No credential value, organizer-only data, or runtime state is published.
`hackathon-program-briefing/references/orangehack-local-validation-accounts.md`
is guidance that describes **how** to create local-only public validation
fixtures (participant/admin test accounts) for browser QA; it contains no
literal account names, passwords, invite codes, or database rows. The canonical
fixtures runbook it points at is **not** migrated. A credential/secret scan over
all 22 published files is clean.

The package ships no `scripts/**` or bare-executable files, so — unlike the
platform-engineering package — no script relocation is required for the
external-catalog import gate; all three skills classify as reference/skill
content.

## Conformance check (structural)

The authoritative `skills check` runs server-side against a live company (it
imports into and mutates that company), so it is the Release-Engineer
post-merge certification gate ([KIR-225](https://github.com/kira-project-lab/kira-skill-catalog)),
not an offline pre-merge step. The **offline-verifiable** layer of that
contract — top-level `<slug>/SKILL.md` only, required `name`/`description`
frontmatter, unique skill names, no nested `SKILL.md` — is re-runnable here:

```sh
python3 - <<'PY'
import os, re, glob
skills = sorted(d for d in os.listdir(".")
                if os.path.isfile(os.path.join(d, "SKILL.md")))
nested = [p for p in glob.glob("**/SKILL.md", recursive=True)
          if p.count("/") > 1]
names, bad = {}, []
for slug in skills:
    fm = open(os.path.join(slug, "SKILL.md")).read().split("---")
    meta = fm[1] if len(fm) > 2 else ""
    name = (re.search(r'(?m)^name:\s*(.+)$', meta) or [None, None])[1]
    desc = re.search(r'(?m)^description:\s*', meta)
    if not name or not desc: bad.append(slug)
    names.setdefault((name or "").strip(), []).append(slug)
dupes = {k: v for k, v in names.items() if len(v) > 1}
print("top-level skills:", len(skills))
print("nested SKILL.md :", nested or "none")
print("missing name/desc:", bad or "none")
print("duplicate names :", dupes or "none")
print("RESULT:", "PASS" if not nested and not bad and not dupes else "FAIL")
PY
```

The three skills added here (`orangehack`, `hackathon-program-briefing`,
`ml-competition-data-ops`) register as top-level skills with unique names and no
nested `SKILL.md`.

## Verify

Re-checksum the published tree and compare against the manifest:

```sh
python3 - <<'PY'
import hashlib, json
m = json.load(open("provenance/orangehack/manifest.json"))
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(65536), b""): h.update(b)
    return h.hexdigest()
bad = 0
for s in m["skills"]:
    for e in s["files"]:
        if sha256(e["target_path"]) != e["sha256"]:
            print("MISMATCH", e["target_path"]); bad += 1
print("OK" if bad == 0 else f"{bad} mismatches")
PY
```

To confirm the source side, resolve the same files at
`kira-project-lab/kira-profile@c75d4631030011f4c7c9915dae4233e21a24a7f9` using
each entry's `source_path` and compare against the recorded `source_sha256`
(before). For the one content-normalized file this proves the exact before→after
pair: `source_sha256` matches the source bytes and `sha256` matches the
published bytes; byte-equivalent files simply have `source_sha256 == sha256`.

## Import path

These skills are imported with the rest of the catalog through the native
importer; provenance is pinned to the resolved catalog commit / SemVer tag:

```sh
pnpm paperclipai skills import https://github.com/kira-project-lab/kira-skill-catalog \
  --company-id "$PAPERCLIP_COMPANY_ID" --json
pnpm paperclipai skills check --company-id "$PAPERCLIP_COMPANY_ID" --json
```
