# OrangeHack source-first platform pack pattern

Use when preparing a real OrangeHack competition from an existing bundle of source materials, especially when Maxim wants to enter the competition into the platform mostly by hand.

## Core lesson

Do **not** generate a new narrative layer when the user asks for source-faithful setup. A derived pack that rewrites case/evaluation wording can drift from the canonical source and create review friction.

Preferred shape: a small `platform-ready/` staging layer that only does three things:

1. standardizes filenames;
2. separates participant-visible and organizer-only artifacts;
3. slices canonical text into copy-paste blocks for platform fields without changing meaning.

## Folder layout

```text
platform-ready/
  participant/
    train.csv
    test.csv
    sample_submission.csv
    starter_notebook.ipynb
    feature_description.csv
  organizer/
    answer_key.csv
    public_private_split.csv
    split_report.json
  copy/
    competition.md
    case.md
    evaluation.md
    submission.md
  CHECKSUMS.sha256
```

## Filename rules

Use short, universal English names for platform upload files:

- no Cyrillic filenames;
- no internal case prefix such as `income` unless it is part of participant-facing terminology;
- keep names stable across competitions: `train.csv`, `test.csv`, `sample_submission.csv`, `starter_notebook.ipynb`, `feature_description.csv`.

Organizer-only files should be equally clear but never participant-visible:

- `answer_key.csv` for hidden targets/weights;
- `public_private_split.csv` for split assignment;
- `split_report.json` for validation evidence.

## Copy block rules

Create `copy/*.md` as platform-field staging docs, not rewritten content.

Allowed edits:

- split source text into platform fields;
- remove internal/source/provenance headings;
- replace “file above/below” with final platform-ready filenames;
- lightly adjust headings so they match platform sections.

Not allowed unless the user asks:

- changing the case story;
- changing evaluation criteria;
- polishing style away from source wording;
- adding generated explanations that were not in the source.

## Participant / organizer boundary

Participant-visible:

```text
participant/train.csv
participant/test.csv
participant/sample_submission.csv
participant/starter_notebook.ipynb
participant/feature_description.csv
```

Organizer-only:

```text
organizer/answer_key.csv
organizer/public_private_split.csv
organizer/split_report.json
```

Never upload organizer-only hidden labels, weights, private split internals, or answer keys into participant case materials.

## Verification before production entry

Check before touching production:

- participant `train.csv` contains target/weight columns when intended;
- participant `test.csv` has no hidden target/weight columns;
- sample submission has only the expected submission columns;
- `answer_key.csv` contains the hidden scoring fields;
- answer-key id set equals test id set;
- split id set equals test id set;
- generate checksums after final copy/rename.

## Production setup sequence

1. Create the competition.
2. Fill competition fields from `copy/competition.md`.
3. Create the case.
4. Fill case fields from `copy/case.md`.
5. Fill evaluation/scoring fields from `copy/evaluation.md`.
6. Add submission instructions from `copy/submission.md`.
7. Upload participant files only.
8. Keep organizer-only files outside participant materials.
9. Verify participant page in browser.
10. Confirm organizer-only files are not reachable from participant routes.
