# VM Web UI provider latency benchmark

Use this when Maxim reports that Kira/Web UI on the YC VM “feels slower” than the home-PC contour, or when deciding whether VM latency is caused by the host/bridge or by a provider/egress path.

## Principle

Benchmark at the Hermes bridge boundary with the same prompts on each contour. This isolates agent/provider latency from browser rendering, reverse proxy, and UI state. Then run a provider override on the same VM bridge to separate VM overhead from provider/egress overhead.

## Minimal prompt set

Use three requests with increasing complexity:

- `simple`: `Ответь ровно одним словом: готово`
- `hello`: `Привет, ты здесь? Ответь одной короткой фразой.`
- `medium`: `Без инструментов. В 5 коротких пунктах объясни, зачем переносить Киру и Web UI с домашнего ПК на VM.`
- `complex`: `Без инструментов. Сравни 3 варианта миграции Кира/Web UI: оставить на ПК, гибрид, полный VM cutover. Дай критерии, риски, рекомендацию и следующий шаг.`

Record for every run: surface, provider, model, elapsed seconds, TTFB/first-delta, success/failure, token counts when available, context-estimate fields, and a short output excerpt.

Reusable helpers:

- `scripts/bridge_latency_benchmark.py` runs `ping`, optional `context_estimate`, and chat prompts against an `ipc://` bridge socket and prints JSONL. Copy it to a tenant-readable path on VM if the tenant socket is private, then run it as the tenant Linux user.
- `scripts/codex_bridge_trace.py` is the focused trace helper for forced `openai-codex / gpt-5.5` comparisons. It records ping, context estimate, start ack, first event, first text delta, total time, and compact final output.

## Bridge benchmark pattern

Send JSONL requests directly to each Unix bridge socket with unique session IDs and `wait: true`. Use generous timeouts for slow provider paths, and interrupt stale runs after a timeout so they do not keep consuming the bridge session.

Typical sockets:

- PC production: `/tmp/hermes-agent-bridge-prod.sock`
- YC VM preview: `/tmp/hermes-agent-bridge-yc-preview.sock`

If the VM `openai-codex` path times out or stays running, check status and interrupt by session ID through the same bridge before continuing.

## Interpretation pattern

- If the user explicitly says the goal is to fix VM first, audit VM first and treat PC numbers only as a comparison target. Do not spend the report on PC context bloat before proving the VM tenant path.
- For VM beta tenants on OpenRouter, check the configured default model and tenant logs before blaming VM networking. Free models can fail through the bridge with `HTTP 429 Provider returned error` after retries; this appears as ~18–20s “slow response” with no useful output. Use `references/vm-beta-openrouter-model-rate-limit.md` for the focused pattern.
- PC `openai-codex` reasonably fast, VM `openai-codex` 10×+ slower, but VM OpenRouter fast ⇒ the VM and Web UI bridge are not the main bottleneck; provider/egress path is.
- HTTP `/health` fast while bridge chat is slow ⇒ exclude Caddy/browser/basic service health first; investigate bridge/provider/context instead.
- Empty-session bridge prompts taking ~10–20s already prove a provider/runtime baseline, but do not explain very slow real UX by themselves. Compare the same prompt in the user's actual heavy session.
- If `bridge.log` shows `contextTokens` around 150k–230k, `fixedContextTokens` around 38k–40k, 100+ tools, or compression runs lasting several minutes, treat context/skill/tool payload and synchronous compression as first-class suspects.
- VM OpenRouter direct succeeds in a few seconds while service-level Codex proxy is slow ⇒ use OpenRouter only as a **control** proving the VM/bridge can be fast. Do **not** present provider switching as the root-cause fix when Maxim asks to keep Codex; continue into network-path analysis.
- If OpenRouter is ever used under a service-level SOCKS proxy, ensure `NO_PROXY` includes `openrouter.ai,.openrouter.ai`; otherwise a Codex-oriented proxy can degrade or break OpenRouter.

## Evidence from 2026-06-19

A comparable three-prompt benchmark showed:

| Surface | Provider/model | simple | medium | complex |
|---|---|---:|---:|---:|
| Home PC | `openai-codex / gpt-5.5` | 13.7s | 9.0s | 16.7s |
| YC VM | `openai-codex / gpt-5.5` | 136.5s | 144.0s | >240s timeout |
| YC VM | `openrouter / google/gemini-3-flash-preview` | 2.7s | 3.2s | 6.8s |

Conclusion for that incident: the user-visible VM slowdown was mostly `openai-codex` over the VM selective egress path, not inherent VM bridge overhead.

## Evidence from 2026-06-29

A prod/Home-PC Web UI latency check after beta-10 work showed the user's “simple hello feels slow” hypothesis was valid even before browser overhead:

| Surface | Provider/model | Prompt | TTFB | Total | Context signal |
|---|---|---|---:|---:|---|
| Home PC prod bridge | `openai-codex / gpt-5.5` | `Привет, ты здесь?...` | 11.6s | 12.0s | empty benchmark session |
| Home PC prod bridge | `openai-codex / gpt-5.5` | `Ответь ровно одним словом: готово` | 12.8s | 13.4s | empty benchmark session |
| Home PC prod Web UI logs | `openai-codex / gpt-5.5` | real heavy sessions | n/a | much slower possible | `contextTokens` 154k–233k, `fixedContextTokens` ~38k–40k, `toolCount` 137 |
| Home PC prod bridge | compression workers | heavy history compression | n/a | 225–280s | synchronous/nearby compression jobs observed |

Conclusion for that incident: basic service health was fine (`/health` under ~1.5s public), and the bottleneck started at chat runtime/bridge/provider. The likely UX cause was not Caddy/browser but large prompt/context assembly plus `openai-codex/gpt-5.5` and long compression work. The next diagnostic should compare an empty session, the exact heavy user session, and the same prompt after compression settles.

## Evidence from 2026-06-29 — VM Codex auth vs PC Codex

Focused trace details are in `references/vm-beta-codex-auth-trace.md`.

When Maxim asks to compare VM and PC using the same `openai-codex / gpt-5.5` path, first verify tenant Codex auth before interpreting latency. A VM tenant may have `.codex/config.toml` but lack `.codex/auth.json`; forcing `openai-codex / gpt-5.5` then fails quickly with `HTTP 403 — HTML error page` and empty bridge output.

Observed pattern:

| Surface | Provider/model | Prompt | Start ack | First text | Total | Result |
|---|---|---|---:|---:|---:|---|
| Home PC | `openai-codex / gpt-5.5` | `готово` | 7.5s | 13.2s | 13.6s | success |
| Home PC | `openai-codex / gpt-5.5` | `Привет...` | 7.6s | 43.4s | 46.2s | success |
| YC VM tenant without Codex auth | `openai-codex / gpt-5.5` | `готово` | 7.7s | none | 8.3s | fast 403/empty output |
| YC VM tenant without Codex auth | `openai-codex / gpt-5.5` | `Привет...` | 7.7s | none | 8.3s | fast 403/empty output |

Conclusion: this is not model latency until auth is fixed; it is missing Codex/ChatGPT auth for the VM tenant.

## Reporting

Keep the user-facing report compact: table of timings, one-sentence diagnosis, and the narrow recommended next change. Do not over-explain benchmark internals unless Maxim asks.