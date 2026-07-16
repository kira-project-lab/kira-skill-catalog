# Chat model switching: visual state vs real run routing

Use this when auditing or fixing Hermes Web UI model switching inside an existing chat.

## Key distinction

Do not accept the model badge changing as proof that the next assistant run uses that model. Verify the path all the way to the Agent Bridge / run executor.

## Code path to inspect

Client/UI:

- `packages/client/src/components/layout/ModelSelector.vue`
  - `handleSelect()` calls `chatStore.switchSessionModel(model, provider, sessionId)` when a session id is present.
- `packages/client/src/stores/hermes/chat.ts`
  - `switchSessionModel()` updates the server via `setSessionModel()` and mutates local `target.model/provider`.
  - `sendMessage()` builds `StartRunRequest` and decides whether `model/provider` are included.

Server/session overlay:

- `packages/server/src/controllers/hermes/sessions.ts`
  - `setModel()` may store a per-user overlay via `setSessionOverlay(... { model, provider })` for Hermes-sourced sessions.
  - That overlay is sufficient for list/detail display, but not automatically proof that active runtime/session mirror uses the new model.

Server/run routing:

- `packages/server/src/services/hermes/run-chat/index.ts`
  - queues preserve `data.model/provider` if the client sent them.
- `packages/server/src/services/hermes/run-chat/handle-bridge-run.ts`
  - resolves the actual `resolvedModel/resolvedProvider`.
  - calls `bridge.chat(..., { model: resolvedModel, provider: resolvedProvider })`; this is the critical real-routing point.
- `packages/server/src/services/hermes/run-chat/model-config.ts`
  - check precedence between `sessionModel/sessionProvider` and `requestedModel/requestedProvider`.

## Regression to test

A good regression test should prove:

1. Existing CLI chat/session already has model A.
2. User switches the session to model B.
3. User sends the next message in the same session.
4. The bridge/run executor receives model B in the actual run options, not just the UI/session row.

For queued messages, repeat the same assertion while the session is already working: the queued item must carry model B if the user switched before sending the queued message.

## Common bug pattern

A bug exists if:

- UI/session detail shows the new model from overlay/local store;
- but `sendMessage()` omits `model/provider` after the first message;
- and server-side `handle-bridge-run` falls back to stale local `sessionRow.model/provider` or profile default.

## Preferred fix shape

Make the run payload or server resolver authoritative for the next run. Minimal options:

- client sends `activeSession.model/provider` for every normal CLI run, not only initial session config; or
- server `setModel()` also updates the runtime/session mirror that `handle-bridge-run` reads; or
- server resolver reads the same overlay/detail source used by UI before starting the bridge run.

Whichever path is chosen, verify at the `bridge.chat()`/executor boundary, not only through component state.
