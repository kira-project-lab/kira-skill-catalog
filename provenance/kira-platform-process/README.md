# kira-platform-process package — provenance

The **kira-platform-process** package records the nine process skills in this
catalog whose source of truth is `kira-project-lab/kira-platform`. It does not
claim the catalog's other process skills share that source.

This directory is provenance metadata only. It contains no `SKILL.md`; the
published skills remain top-level catalog directories.

## Source

| Field | Value |
| --- | --- |
| Source repo | `kira-project-lab/kira-platform` |
| Source ref | `dev` |
| Source commit | `f43fd3b504f6c25fe29d3971da866947b0e4d4cc` |
| Ownership boundary | Kira Lab owns these skills. `kira-platform` remains the editing origin; this catalog is the reviewable distribution surface. |

## Skills and files

The package contains **9 skills and 11 exported files**:

| Slug | Source path | Exported files |
| --- | --- | ---: |
| [`adr`](../../adr/SKILL.md) | `tools/paperclip/skills/adr/**` | 3 |
| [`git-workflow`](../../git-workflow/SKILL.md) | `tools/paperclip/skills/git-workflow/**` | 1 |
| [`kira-dev-pipeline`](../../kira-dev-pipeline/SKILL.md) | `tools/paperclip/skills/kira-dev-pipeline/**` | 1 |
| [`kira-escalation-discipline`](../../kira-escalation-discipline/SKILL.md) | `tools/paperclip/skills/kira-escalation-discipline/**` | 1 |
| [`kira-host-boundary`](../../kira-host-boundary/SKILL.md) | `tools/paperclip/skills/kira-host-boundary/**` | 1 |
| [`kira-issue-contract`](../../kira-issue-contract/SKILL.md) | `tools/paperclip/skills/kira-issue-contract/**` | 1 |
| [`kira-learning-loop`](../../kira-learning-loop/SKILL.md) | `tools/paperclip/skills/kira-learning-loop/**` | 1 |
| [`kira-prompt-authoring`](../../kira-prompt-authoring/SKILL.md) | `tools/paperclip/skills/kira-prompt-authoring/**` | 1 |
| [`wrap-up`](../../wrap-up/SKILL.md) | `tools/paperclip/skills/wrap-up/**` | 1 |

## Export normalization

Every file is produced with the source repository's exporter:

```sh
python3 tools/paperclip/export_text.py export \
  tools/paperclip/skills/<slug> <catalog>/<slug>
```

The exporter removes authored provenance tails such as `[per: ADR 0043]` and
`[per: TES-32]`. Those references resolve only in `kira-platform`; the operative
rule bodies are authored to remain complete after removal. Four of the 11 files
change bytes for that reason: the `SKILL.md` files for `kira-dev-pipeline`,
`kira-escalation-discipline`, `kira-host-boundary`, and `kira-issue-contract`.
The other seven files are byte-identical to source. Exact source and target
digests are recorded in [`manifest.json`](manifest.json).

## Offline importer check

The offline-verifiable part of the catalog import contract is that every skill
has a top-level `<slug>/SKILL.md` with `name` and `description` frontmatter,
skill names are unique, and no nested `SKILL.md` can be mis-imported. Run:

```sh
python3 - <<'PY'
import glob, os, re
skills = sorted(d for d in os.listdir(".")
                if os.path.isfile(os.path.join(d, "SKILL.md")))
nested = [p for p in glob.glob("**/SKILL.md", recursive=True)
          if p.count("/") > 1]
names, bad = {}, []
for slug in skills:
    text = open(os.path.join(slug, "SKILL.md")).read()
    parts = text.split("---")
    meta = parts[1] if len(parts) > 2 else ""
    match = re.search(r"(?m)^name:\\s*(.+)$", meta)
    name = match.group(1).strip() if match else ""
    if not name or not re.search(r"(?m)^description:\\s*", meta):
        bad.append(slug)
    names.setdefault(name, []).append(slug)
dupes = {name: slugs for name, slugs in names.items() if len(slugs) > 1}
print("top-level skills:", len(skills))
print("nested SKILL.md:", nested or "none")
print("missing name/desc:", bad or "none")
print("duplicate names:", dupes or "none")
raise SystemExit(1 if nested or bad or dupes else 0)
PY
```

The authoritative server-side import/check remains a post-merge certification
because it mutates a live company; it is not run during this offline refresh.

## Verify provenance

For every manifest entry, compare `sha256` with the catalog target. Resolve
`source_path` at the exact `source_commit`; for byte-identical entries it must
match `sha256`, while normalized entries must match their `source_sha256`.
Re-exporting all nine source directories into an empty temporary directory and
comparing it with the 11 manifest targets proves that no authored provenance
tail or hand-copied body entered this package.
