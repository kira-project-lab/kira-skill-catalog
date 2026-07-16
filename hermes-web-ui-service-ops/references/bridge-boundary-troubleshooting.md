# Bridge boundary troubleshooting

Use when Hermes Web UI cannot communicate cleanly with the local Hermes Agent bridge.

## Trigger symptoms

- `Connection refused`, `ECONNREFUSED`, `Errno 111`
- `Broken pipe`
- `Agent bridge socket closed without a response`
- bridge request timeout, commonly `120000ms`
- `ENOENT` around bridge/socket/runtime calls
- bridge worker crash or traceback
- unknown/rejected run/session where UI expected an active bridge session
- suspected API/signature drift between `hermes-web-ui` and imported `hermes-agent` runtime code

## Core model

Treat bridge failures as boundary problems first:

1. Is the Web UI service alive?
2. Is the bridge process/worker alive?
3. Is the expected socket/path present and owned by the expected service?
4. Is the bridge crashing on startup or first request?
5. Is there API drift between Web UI bridge code and Hermes Agent runtime helpers?
6. Is the bridge alive but slow/blocked behind compression or another request?

Do not patch application code until runtime evidence identifies the boundary.

## Standard workflow

1. **Capture exact symptom**
   - Read newest `server.log` and `bridge.log` lines around the request.
   - Capture session id/run id/provider/model if present.
   - Classify as transport refusal, timeout, worker traceback, serialization issue, or runtime-provider mismatch.

2. **Check service and socket state**
   - Verify `hermes-web-ui.service` health.
   - Check whether multiple Web UI instances point at the same bridge socket.
   - If a socket path exists without a listener, suspect stale state or crashed worker.
   - If the socket path is missing after restart, check whether the service is still starting before declaring permanent failure.

3. **Trace the code path**
   - Web UI call site → bridge client → bridge manager/server → Python bridge runtime → imported Hermes Agent code.
   - Inspect exception handling that may hide the original traceback.

4. **Check runtime-provider/API drift**
   - Inspect callable signatures on both sides, not just call sites.
   - Known shape: Web UI passes a new kwarg such as `target_model`, but the imported Hermes Agent helper accepts only an older argument such as `requested`; the outer UI may show only a generic transport error.
   - Prefer compatibility shims/signature probing at the bridge boundary over broad rewrites.

5. **Interpret timeouts carefully**
   - A request timeout can mean the bridge is alive but slow, especially during context compression/summarization.
   - If logs later show compression/LLM completion, investigate latency/queueing before treating it as a crash.
   - If timeout appears with `Broken pipe`, `socket closed`, `ECONNREFUSED`, or `ENOENT`, treat it as deeper transport/state instability.

6. **Handle compression-stage failures**
   - `Errno 2` during compression can be a compressor/runtime path issue rather than bridge transport outage.
   - Unicode surrogate serialization failures can poison bridge payloads; JSON emission may need `ensure_ascii=True` style safety.
   - Check whether fallback kept new messages verbatim and whether the session actually recovered.

7. **Verify fix**
   - Add a focused regression test for compatibility/API drift when code changes are made.
   - Run the smallest relevant bridge/runtime test slice.
   - Restart only required services and verify `/health` + a real bridge request.

## Multi-instance socket contention

If production and preview/mirror instances share `ipc:///tmp/hermes-agent-bridge.sock`, one can break the other during restart. Verify all live Web UI services and bridge workers before code changes. The durable fix is usually a unique socket path per service/profile, then a clean restart of conflicting instances.

## Session lock overlap

`session <id> is already running` is usually a lifecycle lock, not proof the bridge crashed. Use session/runtime checks to decide whether to wait, interrupt, destroy stale run state, or reopen the browser page.

## Related references

- `bridge-timeout-analysis.md`
- `runtime-provider-compat.md`
- `multi-instance-socket-contention.md`
- `session-already-running.md`
- `context-compression-preview-enoent.md`
- `codex-context-compression-limit.md`
