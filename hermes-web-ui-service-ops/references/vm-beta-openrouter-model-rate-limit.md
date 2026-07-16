# VM beta OpenRouter model rate-limit diagnosis

Use this when a VM beta tenant Web UI feels slower than PC and the tenant uses OpenRouter, especially a free Google/Gemma/Gemini model.

## Lesson

Do not assume a slow VM chat is VM CPU, Caddy, or network. For tenant runtimes, the fastest isolating sequence is:

1. Verify VM service/HTTP/bridge health.
2. Verify direct OpenRouter network/API timing from the tenant Linux user.
3. Run the same prompt through the tenant bridge socket.
4. Inspect tenant `hermes-root/logs/agent.log` and `errors.log` for `HTTP 429`, upstream provider names, and retry messages.
5. Only then compare with PC baseline or context-heavy sessions.

A free OpenRouter model can pass direct API probes sometimes but still fail through Hermes bridge runs because Hermes performs full agent calls, retries, and can hit upstream free-model rate limits. The symptom is user-visible slowness of ~18–20s with no useful output because the user is waiting for retry backoff, not model generation.

## VM audit command pattern

Run from the operator host, but execute probes as the tenant user when touching tenant sockets or secrets:

```bash
ssh kira-main-ops '
  systemctl is-active kira-beta-webui-usr-polina.service || true
  curl -sS -o /dev/null -w "local_health http=%{http_code} total=%{time_total}s starttransfer=%{time_starttransfer}s\n" http://172.17.0.1:28650/health
  curl -sS -o /dev/null -w "api_health http=%{http_code} total=%{time_total}s starttransfer=%{time_starttransfer}s\n" http://172.17.0.1:28650/api/health
  sudo -u kira-u-polina python3 - <<"PY"
import json, socket, time, os
sock="/data/kira/users/usr_polina/assistants/kira/web-ui-state/agent-bridge.sock"
print("sock_exists", os.path.exists(sock))
s=socket.socket(socket.AF_UNIX); t=time.perf_counter(); s.connect(sock)
s.sendall((json.dumps({"action":"ping"})+"\n").encode())
raw=b""
while b"\n" not in raw: raw+=s.recv(65536)
d=json.loads(raw.split(b"\n",1)[0])
print("bridge_ping_s", round(time.perf_counter()-t,4))
print({"active": d.get("active_sessions"), "running": d.get("running_sessions"), "workers": d.get("workers")})
PY
'
```

For direct OpenRouter timing, avoid printing secrets. Read `OPENROUTER_API_KEY` inside the tenant user process and print only key presence/length plus timings/content/error summaries.

## Bridge probe expectations

For each tenant bridge run record:

- model/provider actually used;
- `start_ack_s`;
- first delta (`ttfb_s`) if any;
- `total_s`;
- whether useful output came through `output` or only final `result.final_response`;
- final error text.

Hermes bridge may report `status: complete` even when the final response is an API failure message. Treat `API call failed after 3 retries: HTTP 429` as a failed model path, not a successful chat.

## Evidence from 2026-06-29

Tenant: `usr_polina` on `kira-main-ops-01`.

Service and transport were healthy:

| Check | Result |
|---|---:|
| tenant `/health` | `200`, `0.008s` |
| tenant `/api/health` | `401`, `0.002s` |
| public VM `/health` | `302`, `0.044s` |
| bridge ping | `0.0007s` |
| bridge running sessions | `0` |

Direct VM → OpenRouter was fast:

| Probe | Timing |
|---|---:|
| `GET /models` | `0.19–0.59s` |
| direct chat `google/gemma-4-26b-a4b-it:free` | `3.08s`, `6.08s` |

But the tenant default model was:

```yaml
model:
  provider: openrouter
  default: google/gemma-4-26b-a4b-it:free
```

Tenant bridge runs failed after retries:

| Bridge model | Result | Total |
|---|---|---:|
| default `google/gemma-4-26b-a4b-it:free` | `HTTP 429 Provider returned error` after 3 retries | ~18–19s |
| explicit same Gemma free model | same `HTTP 429` after 3 retries | ~19.8s |
| `google/gemini-3-flash-preview` | success | `10.7s` |
| `openai/gpt-4.1-mini` | success | `11.8s` |

Log signature:

```text
google/gemma-4-26b-a4b-it:free is temporarily rate-limited upstream
provider_name: Google AI Studio
is_byok: False
API call failed after 3 retries. HTTP 429: Provider returned error
```

## Recommended fix shape

If the product goal is “VM feels comparable to PC” rather than “keep this exact model,” the narrow fix is to change only the tenant default model to a model that passed the tenant bridge probe, then restart only that tenant service and rerun latency smoke.

For this incident the first candidate was:

```yaml
model:
  provider: openrouter
  default: google/gemini-3-flash-preview
```

Alternative that also passed:

```yaml
model:
  provider: openrouter
  default: openai/gpt-4.1-mini
```

Ask before applying live tenant config changes because they affect user-visible runtime and budget, even if the key is capped.

## Reporting pitfall

If the user says they want to fix VM first, do not lead with PC context bloat. PC context analysis can be useful baseline, but the VM tenant should be audited first: service health → bridge → direct provider → tenant bridge model → logs → model override control.