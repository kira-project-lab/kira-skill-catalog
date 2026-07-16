# ML competition case bundle pattern

Use when Maxim asks to collect scattered hackathon/practice materials into a single bundle before creating a real event on a platform.

## Bundle shape

Prefer a deterministic folder outside the app repo when the task is source collation rather than implementation, for example:

```text
<project-root>/hackathon-practice-bundle/
  README.md
  MANIFEST.sha256
  source/
    attached-files/          # participant-visible source attachments
    organizer-files/         # hidden scoring/admin files, never publish
    obsidian/
    web/<source-name>/
  derived/
    data-summary.json
    source-map.md
    case-readiness-check.md
    organizer-answer-key-check.md
```

Keep raw/source materials separate from derived interpretation. Also separate participant artifacts from organizer-only/scoring artifacts in the folder layout; hidden labels/weights must not sit next to participant downloads without an explicit `organizer-files/` boundary.

## Data inventory

For CSV competition files, record:

- path, size, SHA256;
- encoding and delimiter;
- row/column counts;
- train-only/test-only columns;
- target/weight/id/date columns;
- key missingness and sample values;
- starter notebook cells/imports and generated submission format.

Do not depend on pandas being installed. A stdlib `csv` parser with encoding fallback (`utf-8-sig`, `utf-8`, `cp1251`, `latin1`) is enough for first-pass inventory.

## Readiness checklist

Separate:

- **present/enough for v1 case draft**: case text, train/test files, data dictionary, metric formula, starter notebook, assessment draft;
- **blocking for platform scoring**: hidden test `target`, hidden test `w`, public/private split, scoring validation contract, official sample submission;
- **important before participant publication**: final naming, exact schedule, team rules, submit limits, external data/AI policy, confidentiality text, baseline quality, dependency versions, assessment thresholds.

When a later organizer file appears, verify whether it is an answer key rather than “better test data”. A typical answer-key file has exactly the participant test `id` set plus hidden `target`/`w`, no train overlap, and few columns such as `id,w,target`. If so:

- classify it as **organizer-only scoring answer key**;
- copy it under `source/organizer-files/`, not `source/attached-files/`;
- add `derived/organizer-answer-key-check.md` with row count, schema, missingness, SHA256, id-set equality with participant test, and role verdict;
- move hidden labels/weights out of the scoring blockers, but keep public/private split and scoring contract as blockers;
- call out secrecy: this file is for backend/admin scoring only and must not be participant-visible.

When a web kickoff deck is found later, update the readiness checklist by moving only confirmed items out of gaps. Common facts such decks may close: team size, join/freeze rules, submit limits, deadlines, defense window, final deliverables, access path, and communication channels. They usually do **not** close hidden labels/weights or public/private split.

## Source-map discipline

For each source, state how it should be used:

- participant-facing case copy;
- organizer-only policy;
- scoring/admin implementation;
- provenance only;
- template/background only.

Do not treat Obsidian draft status, slide text, and platform-ready configuration as the same authority level. If sources conflict, name the conflict and ask for the one decision that blocks setup.
