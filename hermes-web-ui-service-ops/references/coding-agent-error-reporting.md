# Coding Agent Error Reporting

Use this when a Hermes Web UI coding-agent session (Codex / Claude Code) fails with a generic UI message such as `Error: [object Object]`, `Run failed`, or only an exit code.

## Diagnostic pattern

1. Identify the Web UI state DB for the active surface:
   - live-dev: `${HERMES_WEB_UI_HOME:-~/.hermes-web-ui-dev}/hermes-web-ui.db`
   - prod: `${HERMES_WEB_UI_HOME:-~/.hermes-web-ui}/hermes-web-ui.db`
2. Inspect the session row, not just the URL:
   - `source`, `agent`, `agent_mode`, `provider`, `model`, `workspace`, `agent_session_id`, `agent_native_session_id`, `message_count`.
3. Inspect stored messages. If only the user message is persisted, the agent process likely failed before emitting assistant output.
4. Check fresh server logs around the session id / agent session id / native session id.
5. Distinguish root cause from presentation bug:
   - `codex exec exited code=1` is the process failure.
   - `Error: [object Object]` is a client normalization/serialization bug when `run.failed.error` is an object.

## Durable implementation contract

For print-runner coding agents:

- Buffer sanitized `stderr` from the child process, not only `logger.debug` it.
- On non-zero exit, put a human string in `response.failed.response.error.message`.
- Preserve useful structured fields such as `code` and sanitized `stderr` for logs/debugging.
- Client-side run failure handling must normalize unknown error shapes:
  - string → itself;
  - `Error` → `.message`;
  - object with `message` / `error` string → that field;
  - other object → compact JSON;
  - null/empty → `Run failed`.

## Regression tests to add

- Server helper formats non-zero coding-agent exits with sanitized stderr.
- Server helper falls back to `Codex exited with code N` when stderr is empty.
- Client helper renders `{ message: "..." }` as the message, never `[object Object]`.
- Client helper serializes structured objects without a message field.

## Pitfall

`node-pty unavailable` warnings can coexist with Codex print-runner failures. Do not treat them as the cause unless the selected agent path actually needs hidden PTY. Codex `exec` print runs can fail independently after native session id recording.