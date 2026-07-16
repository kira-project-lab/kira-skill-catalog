# Hermes Web UI bridge timeout tuning

Session note: a request can fail with `Error: Agent bridge request timed out after 120000ms` even when the service is healthy. In the observed incident the live service was active, `dist/server/index.js` had been rebuilt, and the issue was caused by long-running bridge/compression work exceeding the default timeout.

## What the 120s timeout actually covers
- `packages/server/src/services/hermes/agent-bridge/client.ts`
  - default request timeout: `DEFAULT_AGENT_BRIDGE_TIMEOUT_MS = 120000`
  - also overridable via `HERMES_AGENT_BRIDGE_TIMEOUT_MS`
- `packages/server/src/lib/context-compressor/index.ts`
  - summarization timeout: `summarizationTimeoutMs = 120_000`

## Practical interpretation
- `timed out after 120000ms` is usually a *slow-response* symptom, not a full service crash.
- If you also see `Broken pipe` or `socket closed without a response`, treat it as bridge instability under load, not just a missing timeout.
- Raising the timeout can reduce false positives, but it does not fix the slow path itself.

## Safe tuning workflow
1. Change the timeout in source or via env var.
2. Rebuild the production bundle (`npm run build`).
3. Restart `hermes-web-ui.service`.
4. Verify the live service is using the rebuilt artifacts.
5. Re-test the affected session and watch `server.log` for the next timeout point.

## Verification clues
- The rebuilt server bundle should contain the new timeout value in `dist/server/index.js.map`.
- `systemctl --user show hermes-web-ui.service -p MainPID -p ExecStart` should point at the expected live binary.
- If the timeout still fires after a large increase, the bottleneck is likely bridge work or queue contention, not the timeout constant.
