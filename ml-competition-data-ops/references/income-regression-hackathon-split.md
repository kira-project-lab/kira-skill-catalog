# Income-regression hackathon split recipe

Session-derived pattern from OrangeHack `Хакатон-практика`.

## Situation

Files:

- participant train: contains `id`, features, `target`, `w`;
- participant test: contains `id`, `dt`, features; no `target`, no `w`;
- organizer answer key: `id;w;target`, same ID set as participant test;
- metric: WMAE, lower is better;
- event: educational ML competition with public leaderboard and final private scoring.

## Answer-key classification

If a new file has only `id`, `w`, `target` and its ID set exactly matches participant test, classify it as organizer-only scoring answer key, not as a replacement participant test file.

Verify:

- row count equals participant test;
- `id` set equals participant test;
- `id` overlap with train is zero;
- no missing `id`, `w`, `target`;
- delimiter/decimal format recorded;
- SHA256 recorded.

## Public/private split

Recommended procedure:

1. Join participant test with organizer answer key by `id`.
2. Create strata as `dt × target_decile`.
3. Compute deterministic hash score: `sha256(f"{salt}:{id}")`.
4. Within each stratum, sort by hash and assign the chosen public ratio to `public`, rest to `private`.
5. Save participant-safe split as `id;split`.
6. Save organizer-only scoring key as `id;split;w;target`; keep ignored or outside git.

Ratio choice:

- 30/70: stronger private guardrail, less leaderboard overfit.
- 50/50: more stable public feedback; acceptable for educational practice if the user chooses it.

For the OrangeHack session, Maxim chose 50/50.

## Balance report

Always report at least:

- public/private row counts and shares;
- target mean, p50, p95, max;
- weight mean, p50, max;
- distribution by `dt`.

Example acceptable balance from the session:

```text
public:  36 607 rows, 50%
private: 36 607 rows, 50%

public target mean:  99 557.59
private target mean: 98 565.60

public target p50:  65 707.08
private target p50: 65 737.99

public w mean:  0.572504
private w mean: 0.572314
```

## Scoring contract

Participant submit:

```text
id;predict
0;12345,67
1;89012,34
```

Validator should:

- require exact test ID set;
- reject duplicates;
- reject missing IDs;
- reject extra IDs;
- reject empty/non-numeric predictions;
- accept decimal comma and dot unless the product policy says otherwise.

Metric:

```text
WMAE = sum(w_i * abs(target_i - predict_i)) / sum(w_i)
```

## Tooling repo pattern

For a real event, create a separate repo/workspace rather than ad-hoc scripts. Useful layout:

```text
<event>-data/
  .gitignore                         # ignore raw/hidden scoring keys
  README.md
  pyproject.toml
  configs/split_policy.yaml
  docs/scoring-contract.md
  src/<package>/csv_utils.py
  src/<package>/split.py
  src/<package>/validation.py
  src/<package>/scoring.py
  src/<package>/cli.py
  tests/
  artifacts/splits/public_private_split.csv
  artifacts/splits/sample_submission.csv
  artifacts/reports/split_report.json
```

Run real verification:

```bash
python -m pytest -q
PYTHONPATH=src python -m <package>.cli make-split ...
PYTHONPATH=src python -m <package>.cli validate-split ...
PYTHONPATH=src python -m <package>.cli make-sample-submission ...
PYTHONPATH=src python -m <package>.cli score ...
```
