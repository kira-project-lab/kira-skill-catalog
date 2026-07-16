# Model/API latency attribution in Hermes token-audit

Session learning from a Hermes/Codex latency investigation.

## What `api_request.duration_ms` currently means

In the live Hermes agent loop, the API timer starts after the request context has been built and the agent is about to prepare/execute the provider call. It ends after the provider transport returns a complete response or an error.

For Codex (`api_mode='codex_responses'`), this is best described as:

> wall-clock time spent waiting for the model/provider call to complete.

It includes:

- final local API kwargs/preflight/middleware after `api_start_time`;
- `pre_api_request` hook overhead;
- provider transport/client call;
- network/DNS/TLS/request-send time;
- provider queueing/server-side processing;
- model generation;
- stream reading until completion;
- SDK/provider internal retries/timeouts if they happen inside the client call;
- time to return an error for `api_request_error` events.

It does **not** include:

- tool execution after the model response (`tool_call.duration_ms` covers that);
- user typing time;
- most UI/Desktop/TUI rendering time;
- browser/terminal/patch/read_file time except as separate tool spans.

## Important reporting rule

Do not claim that `api_request.duration_ms` proves “the model was thinking” for the whole interval. It only proves that Hermes was waiting for the provider/model call boundary to return.

Use precise language:

- Good: “Hermes waited 880s for the Codex/provider call to complete.”
- Good: “Current tracing does not split model generation from provider queue/connect/stream gaps.”
- Bad: “Codex thought for 880s.”
- Bad: “This is definitely a connect gap/provider idle time.”

## What current traces can answer

Current token-audit traces can reliably split high-level wait into:

- model/provider API wait (`api_request` + `api_request_error`);
- tool wait (`tool_call`);
- per-session totals, counts, max single API/tool call;
- rough token/request size correlation.

Current traces cannot reliably split model/API wait into:

- request preparation;
- DNS/connect/TLS;
- request sent;
- provider queue time;
- time to first byte/token;
- streaming gap between first and last delta;
- local postprocessing;
- UI delivery/rendering.

## Next tracing improvement

If Maxim asks why model/API wait is long, add or recommend finer spans:

- `api_prepare_ms`
- `request_sent_at`
- `first_delta_at` / `time_to_first_token_ms`
- `last_delta_at`
- `stream_finish_at`
- `sdk_retry_count`
- `provider_status`
- `ui_received_at` for Desktop/TUI/Web bridge handoff

Then report at least:

```text
prepare → request_sent → first_delta → last_delta → normalized_response → ui_received
```

This distinguishes slow generation from first-byte latency, stream stalls, provider retries, bridge/Desktop lag, and local tool/runtime delays.

## Compact 12h report shape

For latency reports, prefer a table with:

- session id/title/source/start;
- total traced wait;
- API wait seconds + percent;
- tool wait seconds + percent;
- API/tool call counts;
- max single API/tool call;
- top tool wait contributors.

Always state the trace window and whether the report is based on token-audit events or only SQLite session aggregates.
