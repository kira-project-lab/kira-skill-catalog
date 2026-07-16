# Context compression / preview ENOENT triage

Session note: Hermes Web UI session `mpk4zhafocfup3` hit a large-context compression path and logged two different internal failures before falling back:

- `incremental-llm failed: 'utf-8' codec can't encode character '\udcbb' in position ...: surrogates not allowed`
- later: `incremental-llm failed: [Errno 2] No such file or directory — keeping new messages verbatim`

## What this usually means

- The user-facing session is not necessarily broken; the compressor often falls back to `keeping new messages verbatim` and the chat run continues.
- `Errno 2` here is an internal backend/file-path/socke­t-style failure somewhere in the compression/bridge path, not a UI rendering bug.
- The preview/dev-mode branch-build runtime can be involved in the request path, but a successful preview registry entry does **not** prove the preview build itself is the root cause.

## Triage order

1. Read the newest `server.log` around the `context-compress` / `context-compressor` entries.
2. Read `bridge.log` for the paired `chat` / `destroy` / `request rejected` lines and the runtime payload (`profile`, `cwd`, `profile_dir`, `config_path`).
3. Capture the *exact* `Errno 2` line and the immediately preceding log line; do not stop at the generic error string.
4. Check whether a bad Unicode surrogate appears earlier in the same compression attempt; that can be the first failure and may be the real trigger for the follow-up retry.
5. If the compressor falls back successfully, report the backend bug as degraded-but-recovered, not as a total outage.

## Good reporting shape

- `Symptom: internal context compression failed twice; chat recovered via fallback`
- `Likely layer: context-compressor / agent-bridge boundary`
- `User impact: raw backend error surfaced instead of a domain error`
- `Preview relation: possible runtime contributor, not proven root cause`

## Follow-up coding clue

When fixing this class of issue, prefer a domain error around compression/bridge state and preserve the fallback path. Do not replace fallback with a hard crash unless the session truly cannot continue.