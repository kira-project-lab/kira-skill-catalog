# 2026-06-22 Kira token-audit activation and tokenjuice hook note

Use this as a concrete worked example when finishing a Hermes token-economy baseline after the profile has enough disk space.

## Baseline decision

A strong low-noise baseline used only three enabled plugins:

- `agentmemory` — memory backend;
- `tokenjuice` — terminal-output compaction;
- `token-audit` — metadata-only local JSONL telemetry.

Do not add broad plugin bundles just because they exist. Add one plugin only when it closes a measured gap.

## Disk preflight

Tracing and logs fail badly when `/home` is full. Before running smoke sessions or broad reports, check `df -h /home` and clear enough space for logs/reports. If JSONL becomes malformed during ENOSPC, repair/rotate the partial line, then verify by parsing every line with `json.loads`.

## Token-audit verification

Good checks after enabling a profile-local tracing plugin:

```bash
python -m py_compile ~/.hermes/profiles/kira/plugins/token-audit/__init__.py
python -m py_compile ~/.hermes/profiles/kira/token-audit/analyze.py
HERMES_HOME=~/.hermes/profiles/kira hermes plugins list --enabled --json
HERMES_HOME=~/.hermes/profiles/kira hermes chat -q 'Token audit smoke test. Reply exactly: pong' --source token-audit-smoke
python ~/.hermes/profiles/kira/token-audit/analyze.py --days 1 --output ~/.hermes/profiles/kira/token-audit/reports/$(date +%F)-trace.md
python - <<'PY'
import json, pathlib
p=pathlib.Path.home()/'.hermes/profiles/kira/token-audit/events.jsonl'
for i,line in enumerate(p.open(), 1):
    json.loads(line)
print('events_jsonl_ok', i)
PY
```

Also search the JSONL serialization for smoke prompt/response fragments to confirm metadata-only capture did not leak raw prompt text.

## tokenjuice `transform_terminal_output` compatibility

Hermes v0.17.0 called the hook like this from `tools/terminal_tool.py`:

```python
invoke_hook(
    "transform_terminal_output",
    command=command,
    output=output,
    returncode=returncode,
    task_id=effective_task_id or "",
    env_type=env_type,
)
```

A plugin that expects only `exit_code` and `cwd` raises:

```text
_transform_terminal_output() missing 2 required positional arguments: 'exit_code' and 'cwd'
```

Make the plugin accept both old and current shapes:

```python
def _transform_terminal_output(
    command: str,
    output: str,
    exit_code: int | None = None,
    cwd: str | None = None,
    task_id: str | None = None,
    returncode: int | None = None,
    env_type: str | None = None,
    **kwargs,
):
    del task_id, env_type, kwargs
    normalized_exit_code = returncode if returncode is not None else exit_code
    return _compact_terminal_output(
        command=command,
        output=output,
        exit_code=normalized_exit_code if normalized_exit_code is not None else 0,
        cwd=cwd or os.getcwd(),
    )
```

Verify with both a direct import call and a real `hermes chat -q` smoke run. Count old warning lines before and after the smoke run; the count should not increase.

## Interpretation from the first useful report

Early Kira report showed:

- `skill_view` results can dominate tool-result bytes;
- compression sessions can have very high input tokens;
- reasoning tokens were not the main pressure;
- loaded tools/schema breadth and mandatory skill payloads should be tuned only after a normal workday trace.

Do not tune compression, toolsets, or skill policy from a single one-line smoke session. Use the smoke only to prove the telemetry path.
