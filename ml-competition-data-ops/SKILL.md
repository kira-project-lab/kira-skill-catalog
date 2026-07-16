---
name: ml-competition-data-ops
description: "Design and operate ML competition data/scoring packs: train/test artifacts, hidden answer keys, public/private splits, sample submissions, scoring contracts, validation tooling, and organizer-only safeguards."
version: 1.0.0
author: Kira
license: MIT
metadata:
  hermes:
    tags: [data-science, ml-competition, hackathon, scoring, leaderboard, validation]
    related_skills: [hackathon-program-briefing, critical-expert-judgment, codegraph-first]
---

# ML Competition Data Ops

Use this when Maxim needs to create or validate a real ML-competition/hackathon dataset, scoring flow, leaderboard split, or platform setup pack.

This skill covers the data/scoring layer, not the participant-facing program narrative. Pair with `hackathon-program-briefing` for event copy, rules, agenda, defense rubric, and participant communications.

## Core contract

Build reproducible artifacts, not hand-wavy scoring descriptions.

For every competition pack, separate:

- participant artifacts: train, test, data dictionary, starter notebook, sample submission;
- organizer-only artifacts: hidden answer key, weights, public/private split with labels, scoring key;
- derived reports: schema inventory, split balance report, validation report, manifest/checksums;
- code/tooling: deterministic split generator, submit validator, scorer, tests.

Never publish or commit organizer-only `target`, `w`, hidden labels, or private split internals into participant materials.

## Standard workflow

1. **Inventory files**
   - Record exact paths, row counts, columns, delimiter, encoding, hash.
   - Confirm participant test has no hidden target/weight columns.
   - Confirm organizer answer key has exactly the same `id` set as participant test.
   - Check train/test ID overlap is zero.

2. **Classify artifacts**
   - `train.csv`: participant-visible if it includes target.
   - `test.csv`: participant-visible if target/weights removed.
   - `*_4_org.csv`, answer key, labels, weights: organizer-only.
   - `sample_submission.csv`: participant-visible and should contain only `id,predict` or the approved equivalent.

3. **Design public/private split**
   - Prefer deterministic stratified split over raw random split.
   - For tabular regression, a strong default is stratification by time/date column plus target quantile/decile.
   - Choose public/private ratio based on event goals. For educational competitions, 50/50 is acceptable when participants need more stable public feedback; 30/70 is better when private anti-overfit protection matters more.
   - Use a fixed salt and SHA-256 hash assignment inside each stratum; save the salt hash in reports.
   - Do not expose hidden target-derived strata to participants.

4. **Validate split balance**
   Compare public/private:
   - row counts and share;
   - time/date distribution;
   - target mean, median, p95, max;
   - weight mean/median/max;
   - any known high-risk segment/category if relevant.

5. **Write scoring contract**
   Specify:
   - required submit columns;
   - delimiter and decimal policy;
   - exact ID-set requirement;
   - duplicate, missing, extra ID rejection;
   - missing/non-numeric prediction rejection;
   - metric formula;
   - which split is shown during competition and which is final.

6. **Create tooling repo when stakes justify it**
   For real events, create a separate repo/workspace for data/scoring operations. Keep raw data and hidden scoring keys ignored. Commit code, config, tests, public split metadata if safe, sample submission, and reports.

Recommended layout:

```text
hackathon-practice-data/
  .gitignore
  README.md
  pyproject.toml
  configs/split_policy.yaml
  docs/scoring-contract.md
  src/<package>/
    csv_utils.py
    split.py
    validation.py
    scoring.py
    cli.py
  tests/
  artifacts/
    splits/public_private_split.csv
    splits/sample_submission.csv
    reports/split_report.json
```

Organizer-only generated files such as `scoring_key_with_split.csv` must be ignored or stored outside git.

7. **Verify with real runs**
   - Run unit tests.
   - Generate split from real files.
   - Validate split against participant test + answer key.
   - Generate sample submission.
   - Score sample submission on public/private to exercise the full pipeline.
   - Regenerate manifests/checksums.

## Recommended defaults

For a tabular income-regression educational hackathon with `dt`, hidden `target`, and hidden `w`:

- split ratio: use Maxim's chosen ratio; if not specified, recommend 30/70 for anti-overfit or 50/50 for stable public feedback;
- stratification: `dt × target_decile`;
- assignment: SHA-256 hash of `salt:id` sorted within each stratum;
- metric: WMAE;
- submit format: `id;predict`;
- validation: exact test ID set, reject duplicate/missing/extra IDs, accept decimal comma and dot unless product requires one style.

## Pitfalls

- Do not confuse organizer answer key with “better test data.” If a file has `id,w,target` matching test IDs, treat it as hidden scoring input.
- Do not create a public/private split from participant test only when target distribution matters and organizer labels are available.
- Do not use a temporal public/private split for educational leaderboard feedback unless the event explicitly wants future-generalization stress; it may make public feedback poorly representative of private.
- Do not commit hidden scoring keys, even in a private repo, unless the repo is explicitly organizer-only and access-controlled.
- Do not stop at generating CSVs; write validation and scoring commands that prove the artifacts work.

## Reference

- `references/income-regression-hackathon-split.md` — session-derived recipe for an income-prediction hackathon using `dt × target_decile` stratification, WMAE, and organizer-only answer keys.
- `references/platform-evaluator-readiness-checks.md` — checklist for verifying whether a platform's automatic evaluator is actually safe for production ML competitions: trace queue/worker/sandbox/resource limits in code before enabling auto-scoring.
