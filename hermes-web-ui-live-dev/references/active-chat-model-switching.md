# Active chat model switching

Use this when investigating or changing model switching in the Hermes Web UI chat while a session already has history.

## Symptom

The model selector can appear to switch visually, while the next real run still uses the old session model or the profile default.

## Root cause pattern

There are two separate paths:

- UI/session list/detail projection: `activeSession.model/provider` and per-user session overlay.
- Real run execution: payload sent by the client, then server-side model resolution before `bridge.chat()`.

For regular CLI chat, do not assume a persisted overlay is enough. The model that matters is the one eventually passed in the Agent Bridge options:

```ts
bridge.chat(..., {
  ...(resolvedModel ? { model: resolvedModel } : {}),
  ...(resolvedProvider ? { provider: resolvedProvider } : {}),
})
```

## Correct contract

For an existing regular CLI session:

1. User switches model/provider in the model selector.
2. The client persists the session model (`POST /api/hermes/sessions/:id/model`).
3. The next `startRunViaSocket` payload includes the switched `model` and `provider`, even when the session already has messages.
4. Server-side `resolveBridgeRunModelConfig()` treats `requestedModel/requestedProvider` as authoritative for that run over stale `sessionRow.model/provider`.
5. The model still must be validated against available `model_groups`; if unavailable, fallback to profile default remains acceptable.

## Regression tests to add/keep

Client-store test:

- existing CLI session with `messageCount > 0`;
- `switchSessionModel('new-model', 'provider')`;
- `sendMessage(...)`;
- assert `startRunViaSocket` payload contains the new `model` and `provider`.

Server model-config test:

- `sessionModel` is old;
- `requestedModel` is new;
- both are present in `modelGroups`;
- assert the resolver returns requested/new model/provider.

## Pitfalls

- Do not limit model/provider payload to first-message initialization only. That protects session creation, but breaks live model switching.
- Do not let stale local session-store rows override explicit run payload values.
- Do not judge by the selector label or session row alone; trace to `bridge.chat()` options.
- Queued follow-up runs should carry the selected model/provider captured at send time.
