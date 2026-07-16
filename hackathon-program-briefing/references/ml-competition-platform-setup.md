# ML competition platform setup from a case bundle

Use when Maxim asks to turn a prepared hackathon/case bundle into a real OrangeHack-style platform competition.

## Source bundle shape that worked

Keep sources and derived launch artifacts separated:

```text
source/
  attached-files/          # participant-visible raw files
  organizer-files/         # answer keys / hidden scoring files, never participant-visible
  obsidian/                # copied project notes
  web/start-brief/         # extracted web/deck source

derived/
  data-summary.json
  source-map.md
  case-readiness-check.md
  organizer-answer-key-check.md
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
  created-competition-record.md
```

## Data/scoring repo pattern

For a real ML competition, create a separate local repo for data/scoring tooling, not ad-hoc scripts in the platform repo:

```text
/home/werserk/5-work/orange-hack/hackathon-practice-data
  src/<package>/
    split.py
    scoring.py
    validation.py
    cli.py
  configs/split_policy.yaml
  docs/scoring-contract.md
  tests/
  artifacts/splits/
  artifacts/reports/
```

Keep raw data and organizer-only keys out of git:

```gitignore
data/raw/
artifacts/splits/scoring_key_with_split.csv
```

Commands used successfully:

```bash
PYTHONPATH=src python -m hack_practice_data.cli make-split \
  --participant-test <bundle>/source/attached-files/hackathon_income_test.csv \
  --answer-key <bundle>/source/organizer-files/hackathon_income_test_4_org.csv \
  --out-split artifacts/splits/public_private_split.csv \
  --out-key artifacts/splits/scoring_key_with_split.csv \
  --out-report artifacts/reports/split_report.json

PYTHONPATH=src python -m hack_practice_data.cli validate-split \
  --participant-test <bundle>/source/attached-files/hackathon_income_test.csv \
  --answer-key <bundle>/source/organizer-files/hackathon_income_test_4_org.csv \
  --split artifacts/splits/public_private_split.csv

PYTHONPATH=src python -m hack_practice_data.cli make-sample-submission \
  --participant-test <bundle>/source/attached-files/hackathon_income_test.csv \
  --answer-key <bundle>/source/organizer-files/hackathon_income_test_4_org.csv \
  --out artifacts/splits/sample_submission.csv
```

## Public/private split recommendation pattern

If user chooses otherwise, respect it. Default judgment for educational ML practice:

- Stratify by `dt × target_decile` when `dt` and hidden `target` exist.
- Use deterministic SHA-256 assignment inside each stratum.
- Validate public/private similarity on row counts, months, target mean/p50/p95/max, and weight mean/p50/max.
- Store split policy and salt hash in report/config.

For the HCK-ALFA income case Maxim chose 50/50 public/private, not the initially recommended 30/70. The useful implementation retained stratification and determinism.

## Final-submit policy pattern

When the platform allows two final submissions:

1. Team can select up to 2 valid final submissions.
2. If 1 selected, auto-fill the second with the best remaining valid public-score submission if one exists.
3. If 0 selected, auto-select up to 2 best valid public-score submissions.
4. Invalid submissions never participate.
5. If only 1 valid submission exists, use that one.
6. Recommended private result: best private WMAE among selected final candidates.

Do not use best private among all submissions: that permits unlimited hidden-set probing.

## Creating the platform record safely

Prefer official admin/API paths if they exist. If local runtime lacks admin create endpoints, a one-off seed script inside the backend container can create records directly using SQLAlchemy models, but record the limitation clearly.

Minimum created records:

- `Competition`: title, schedule, private/invite-code visibility, team size, config sections from `final-bundle`.
- `Case`: participant-facing case text, grading/scoring docs, submission docs, docs refs, team size, submission windows, rate limits.
- `InviteCode`: deterministic join code, issued status, expiry.

Verification before reporting success:

```bash
curl -sS http://localhost:<backend-port>/api/cases/competition/<competition_id>
# plus DB readback for Competition, Case, InviteCode fields
```

Record final IDs and URLs in `derived/created-competition-record.md`.

## Important pitfall

Creating the event record is not the same as a fully working scored launch. Report blockers separately:

- If S3/evaluation storage is not configured, set `evaluation_enabled=false` and say automatic scoring is not active.
- If the platform only supports one `daily_submission_limit`, store final-day override in config/docs but say backend support is still needed.
- If final-submit fallback is documented but not implemented/verified in backend, call it out as a product/backend gap.
- Do not put hidden `target`, `w`, or private split labels in participant-visible docs or storage.
