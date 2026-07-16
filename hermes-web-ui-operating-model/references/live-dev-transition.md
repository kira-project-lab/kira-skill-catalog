# Hermes Web UI live-dev transition note

Use this when converting `hermes.dev.ops.kiraproject.ru` from branch-preview deploys into a persistent live-reload runtime.

## Runtime modes

| Mode | Source of truth | Primary purpose | Typical update mechanism |
|---|---|---|---|
| Prod | `origin/main` + production checkout | Stable public runtime | Build + restart |
| Branch preview | pushed feature branch in dedicated preview checkout | Review a specific branch/PR | Fetch + build + restart |
| Live-dev | dedicated watch runtime on dev hostname | Fast iterative development | HMR for frontend; watch/restart for backend |

## Live-dev invariants

- Keep prod isolated from live-dev state, ports, and service identity.
- Treat live-dev as a persistent runtime, not as an ad-hoc deploy target.
- Make runtime identity explicit in health/build metadata (`runtime=live-dev`).
- Frontend changes should appear without manual rebuild when possible.
- Backend changes may use watcher-triggered restart, but the browser-visible loop must stay short and predictable.
- Do not assume a branch preview workflow still applies once live-dev is enabled.

## Migration checklist

1. Decide what is hot-reloaded and what still needs restart.
2. Define the live-dev service unit, ports, and state directory.
3. Update build/runtime metadata so the host can self-identify as live-dev.
4. Update docs and skills before changing the runtime topology.
5. Verify browser-visible refresh, websocket reconnect, and backend recovery.
6. Keep the branch-preview workflow documented separately as the fallback / alternate mode.

## Failure modes to guard against

- Confusing branch-preview deploys with live-dev reloads.
- Serving live-dev through the wrong state dir or bridge endpoint.
- HMR working locally but not through the public hostname/proxy.
- Backend watcher restarts breaking session/bridge state unexpectedly.
- Caching hiding updates in the browser and creating false negatives.
