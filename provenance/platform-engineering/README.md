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

## Normalization

The default transformation is **path-only**: source skills live under
`skills/<category>/<slug>/**` in `kira-profile`; they are published here as
top-level `<slug>/**` to match the catalog's flat, importer-discovered layout.
For all but three files, **contents are byte-equivalent** to source. Every
file's `sha256` and its `source_path → target_path` mapping is recorded in
[`manifest.json`](manifest.json); per-file `normalization` notes flag any file
that is not byte-equivalent.

Three files carry a documented, safety-driven deviation (each also carries a
per-file `normalization` note in the manifest):

1. **Credential redaction** — `hermes-web-ui-service-ops/references/session-url-inspection.md`:
   the terminal-fallback example previously posted literal `admin` / `123456`
   values to `/api/auth/login`. Those literals are replaced with
   `<username>` / `<password>` placeholders so the catalog carries no
   operational credential. The example still shows the login mechanism, and the
   change aligns the snippet with that file's own rule ("Do not hard-code or
   invent credentials"). This satisfies the *no credentials or runtime state*
   acceptance criterion.
2. **Nested-skill de-registration** — the source folds an archived package into
   `hermes-token-economy/references/package-hermes-token-observability/` and that
   folder shipped a nested `SKILL.md` with valid skill frontmatter. A published
   nested `SKILL.md` could be mis-imported as a ninth skill and breaks the
   "published skills are top-level `<slug>/SKILL.md`" contract, so the file is
   renamed to `OVERVIEW.md`. Contents are unchanged (`sha256` identical); only
   the filename changes so no name-based skill discovery can register it.
3. **Citation follow-through** — `hermes-token-economy/SKILL.md` had one
   reference-list line pointing at the nested `.../SKILL.md`; it now points at
   `.../OVERVIEW.md` to match the rename. No other content changed.

Additionally, one **path-only relocation** (contents byte-equivalent, `sha256`
unchanged — not a content deviation):

4. **Script relocation for import compatibility** — `hermes-web-ui-service-ops`
   ships five helper files that live under `scripts/**` in source. The native
   catalog importer classifies files by path: anything under `scripts/**` (or
   with a bare `.py`/`.mjs`/`.sh`/… extension) is `kind=script`, and an external
   GitHub skill that contains any script-class file is categorically rejected
   (`reason=scripts_executables_blocked`) with no force/approval bypass. Files
   under `references/**` are classified `kind=reference` regardless of
   extension. So the five helpers are published under
   `references/scripts/**` instead of `scripts/**`. This changes only the
   `target_path` (source keeps `scripts/<name>`); file **contents are
   byte-identical** and every `sha256` is unchanged. The helpers become inert
   reference material — this uses the importer's own classification contract and
   bypasses no trust boundary. Each relocated file carries a per-file
   `normalization` note in the manifest.

The eight source skill trees are otherwise byte-equivalent; independent
re-checksumming (below) reports `files=223 target_mismatches=0`. With the
relocation, every one of the eight published skills classifies below the script
trust level, so all eight pass the external-catalog import gate.

## Conformance check (structural)

The authoritative `skills check` runs server-side against a live company (it
imports into and mutates that company), so it is the Release-Engineer
post-merge gate, not an offline step. The **offline-verifiable** layer of that
contract — top-level `<slug>/SKILL.md` only, required `name`/`description`
frontmatter, unique skill names, no nested `SKILL.md` — is re-runnable here:

```sh
python3 - <<'PY'
import os, re, glob
skills = sorted(d for d in os.listdir(".")
                if os.path.isfile(os.path.join(d, "SKILL.md")))
nested = [p for p in glob.glob("**/SKILL.md", recursive=True)
          if p.count("/") > 1]
names, dupes, bad = {}, [], []
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
