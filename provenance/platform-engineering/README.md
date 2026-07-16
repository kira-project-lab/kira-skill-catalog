# platform-engineering package — provenance

The **platform-engineering** package publishes eight Hermes / platform executor
skills into `kira-skill-catalog` so they live outside the cognitive profile
(`kira-project-lab/kira-profile`) while staying independently reviewable and
byte-verifiable against their source.

This directory is provenance metadata only. It contains no `SKILL.md`, so the
native importer does not treat it as a skill; the eight skills themselves are
published as top-level `<slug>/` directories per the catalog layout
([root README → Layout](../../README.md#layout)).

## Source

| Field | Value |
| --- | --- |
| Source repo | `kira-project-lab/kira-profile` |
| Source ref | `dev` |
| Source commit | `c75d4631030011f4c7c9915dae4233e21a24a7f9` |
| Ownership boundary | Kira Lab owns these skills. Publishing here does **not** move ownership out of Kira Lab; the catalog is the reviewable distribution surface, `kira-profile` remains the editing origin. |

## Skills in this package

| Slug (catalog top-level) | Source path in `kira-profile` |
| --- | --- |
| [`debugging-hermes-tui-commands`](../../debugging-hermes-tui-commands/SKILL.md) | `skills/software-development/debugging-hermes-tui-commands/**` |
| [`hermes-codex-debugging`](../../hermes-codex-debugging/SKILL.md) | `skills/software-development/hermes-codex-debugging/**` |
| [`hermes-provider-troubleshooting`](../../hermes-provider-troubleshooting/SKILL.md) | `skills/devops/hermes-provider-troubleshooting/**` |
| [`hermes-token-economy`](../../hermes-token-economy/SKILL.md) | `skills/devops/hermes-token-economy/**` |
| [`hermes-web-ui-live-dev`](../../hermes-web-ui-live-dev/SKILL.md) | `skills/devops/hermes-web-ui-live-dev/**` |
| [`hermes-web-ui-operating-model`](../../hermes-web-ui-operating-model/SKILL.md) | `skills/software-development/hermes-web-ui-operating-model/**` |
| [`hermes-web-ui-service-ops`](../../hermes-web-ui-service-ops/SKILL.md) | `skills/devops/hermes-web-ui-service-ops/**` |
| [`hermes-web-ui-upstream-sync`](../../hermes-web-ui-upstream-sync/SKILL.md) | `skills/software-development/hermes-web-ui-upstream-sync/**` |

## Normalization (path-only)

The only transformation applied is **path**: source skills live under
`skills/<category>/<slug>/**` in `kira-profile`; they are published here as
top-level `<slug>/**` to match the catalog's flat, importer-discovered layout.
**File contents are byte-equivalent** — no edits to `SKILL.md`, `references/**`,
or `scripts/**`. Every file's `sha256` and its `source_path → target_path`
mapping is recorded in [`manifest.json`](manifest.json).

## Verify

Re-checksum the published tree and compare against the manifest:

```sh
python3 - <<'PY'
import hashlib, json, os
m = json.load(open("provenance/platform-engineering/manifest.json"))
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
each entry's `source_path` and compare `sha256`.

## Import path

These skills are imported with the rest of the catalog through the native
importer; provenance is pinned to the resolved catalog commit / SemVer tag:

```sh
pnpm paperclipai skills import https://github.com/kira-project-lab/kira-skill-catalog \
  --company-id "$PAPERCLIP_COMPANY_ID" --json
pnpm paperclipai skills check --company-id "$PAPERCLIP_COMPANY_ID" --json
```
