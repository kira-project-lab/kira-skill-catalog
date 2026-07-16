# Platform evaluator readiness checks

Use when deciding whether to enable automatic scoring/evaluation for a real ML competition on OrangeHack or a similar platform.

## Core lesson

Do not infer evaluator safety from docs, field names, or comments. Inspect the actual execution path before enabling production auto-evaluation.

A platform may expose fields such as `evaluation_timeout_seconds`, `evaluation_memory_limit_mb`, `evaluation_enabled`, Celery workers, or queue env vars while the actual submission path still runs inside the web backend process.

## Inspection checklist

Trace these facts in code:

1. Submission creation path: where `POST /submissions` registers a pending submission.
2. Task dispatch: whether scoring uses FastAPI `BackgroundTasks`, `asyncio.create_task`, Celery, a durable queue, or external compute.
3. Execution runtime: subprocess in backend container, Celery worker, per-submit Docker sandbox, VM, serverless job, or managed queue worker.
4. Isolation: whether user/evaluation code can install packages or run Python in the service runtime.
5. Resource enforcement: whether timeout, CPU, and memory limits are actually enforced, not just stored in DB.
6. Load control: whether failed submissions count toward rate limits and whether retries/retests have concurrency caps.
7. Storage boundary: which S3 buckets hold participant submissions, evaluation scripts, public datasets, private datasets, logs, and answer keys.
8. Visibility boundary: public score vs private metrics; ensure private keys are filtered from participant APIs.

## OrangeHack-specific findings pattern

For OrangeHack Platform, the current code path found in the July 2026 review was:

- leaderboard is derived from `submissions`, grouped by team, using best public `score`;
- normal submission evaluation is started through FastAPI background task, not Celery;
- admin retest starts with `asyncio.create_task`, not Celery;
- evaluator downloads `evaluate.py`, public/private datasets, and submission from S3-compatible storage;
- evaluator writes them to a temp directory and runs `python3 run_evaluation.py` as a subprocess;
- `requirements.txt` can be installed with `pip install` in the service runtime;
- timeout is enforced with `asyncio.wait_for`;
- memory limit is stored/passed but not enforced in that path;
- comments/docstrings may mention Docker, but actual code did not run a per-submission Docker container;
- Yandex Cloud was used as S3-compatible Object Storage, not as a separate compute/queue scoring layer;
- `YMQ_*` env variables existed, but source usage for scoring was not found.

Treat this as a pattern to re-verify, not as permanent truth. Code may change.

## Safe recommendation rule

If scoring runs in the web backend process or a non-isolated worker, recommend one of these before a real public ML competition:

1. keep `evaluation_enabled=false` and seed/compute scores through a controlled organizer-side script; or
2. implement a durable evaluator worker with queue-backed jobs and sandboxed execution before enabling participant auto-scoring.

Minimum robust architecture:

```text
submission uploaded to S3
  -> DB row pending
  -> durable queue job
  -> dedicated evaluator worker pool
  -> per-job sandbox/container with CPU/memory/time limits
  -> scoring logs/artifacts to private storage
  -> DB update scored/failed
  -> leaderboard reads DB only
```

## Reporting shape

When answering Maxim, separate:

- verified code facts;
- documentation intent;
- current production risk;
- safe next option for the competition.

Do not say “it uses Docker/Celery/Yandex Queue” unless the traced submission path actually calls that mechanism.
