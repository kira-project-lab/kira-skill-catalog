# ML competition data bundle and scoring workflow

Use this reference when preparing a real hackathon/practice event with train/test files, hidden answer keys, public/private leaderboard split, and participant-facing case materials.

## Bundle structure

Create a durable bundle with clear separation:

```text
source/
  attached-files/        # participant-visible source files
  organizer-files/       # hidden labels/weights/answer keys; never publish
  obsidian/              # copied planning notes/source docs
  web/                   # extracted live brief/pages, if any
derived/
  data-summary.json
  source-map.md
  case-readiness-check.md
  platform-setup/
    public_private_split.csv
    sample_submission.csv
    split_report.json
  final-bundle/
    event-metadata.md
    participant-case-page.md
    participant-rules.md
    submission-format.md
    scoring-contract.md
    platform-upload-checklist.md
    organizer-secrets-checklist.md
MANIFEST.sha256
```

Keep `source/organizer-files/` and any scoring key with `target`, `w`, or private labels out of participant-visible storage.

## Source inventory checklist

For each CSV, record:

- absolute source path;
- SHA256;
- delimiter and decimal convention;
- encoding;
- row count and column count;
- key columns present/missing;
- train/test schema differences;
- missing-value hotspots;
- sample rows without exposing secrets unnecessarily.

For notebooks, record imports, cell count, metric functions, and submit-generation behavior.

## Answer key recognition

A file like `id;w;target` matching the participant test `id` set is an organizer answer key, not a better participant test file. Verify:

- row count equals participant test;
- `id` set exactly matches participant test;
- no `id` overlap with train if train/test are disjoint;
- no missing `id`, `w`, `target`;
- hidden columns are never copied into participant materials.

## Public/private split recommendation

Default for educational ML competitions: deterministic stratified random split.

For tabular regression with time/month field and heavy target skew:

1. join participant test to organizer answer key by `id`;
2. create strata from `dt × target_decile`;
3. sort rows inside each stratum by SHA-256 hash of `salt:id`;
4. allocate requested ratio inside each stratum;
5. save `id;split` as setup metadata;
6. save `id;split;w;target` only as organizer/scoring key;
7. write a split report comparing rows, target mean/p50/p95/max, weight mean/p50/max, and by-date counts.

Use 30/70 when leaderboard-overfitting risk matters most. Use 50/50 if the user explicitly wants a larger public signal or if the educational feedback value is more important.

## Scoring contract

For WMAE competitions:

```text
WMAE = sum(w_i * abs(target_i - predict_i)) / sum(w_i)
```

Recommended validation:

- submit columns: `id`, `predict`;
- exact test `id` set required;
- duplicate IDs rejected;
- missing IDs rejected;
- extra IDs rejected;
- decimal comma and decimal dot accepted;
- invalid submissions do not get leaderboard score and do not participate in final-submit fallback.

## Final submit selection pattern

If teams may choose up to 2 final submissions:

1. use the selected valid submissions if two are selected;
2. if one is selected, auto-fill the second candidate with the best remaining valid public-score submission;
3. if none are selected, auto-select up to two best valid public-score submissions;
4. ignore invalid submissions completely;
5. if only one valid submission exists, use only that one;
6. if zero valid submissions exist, the team has no private score;
7. compute final private result as the best private score among the selected final candidates, unless the event explicitly specifies another aggregation rule.

This gives participants a controlled hedge without allowing unlimited private probing.

## Final platform setup pack

After decisions are closed, produce `derived/final-bundle/` with:

- `event-metadata.md`;
- `participant-case-page.md`;
- `participant-rules.md`;
- `submission-format.md`;
- `scoring-contract.md`;
- `platform-upload-checklist.md`;
- `organizer-secrets-checklist.md`.

Treat starter notebooks separately: a random prediction notebook is acceptable as a format demo, but before publication prefer a fixed-seed reproducible baseline.
