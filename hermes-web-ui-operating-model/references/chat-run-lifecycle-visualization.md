# Chat run lifecycle visualization

Use this when Hermes Web UI shows stale/idle chat UI while the agent is still running, especially after command-driven continuations such as `/goal` where refresh/resume restores `working` state.

## Symptom

- The assistant posts a continuation/status message such as `Continuing toward goal`.
- The underlying Hermes agent keeps working.
- The chat UI does not immediately show the normal working/thinking visualization: thinking GIF, stop/disabled controls, streaming/active affordances, or status dots.
- Refreshing the page or switching/resuming the session restores the working UI because `resumeSession(... data.isWorking ...)` reports the server-side state.

## Root-cause pattern

Treat this as a lifecycle synchronization bug, not a cosmetic message-rendering bug.

Likely chain to inspect:

```text
server run/command continuation starts
  -> server records session as working
  -> client does not receive or handle the real-time working/run-start event
  -> client stays visually idle until resumeSession hydrates isWorking
```

In the client, inspect the split between:

- session-level working state (`serverWorking`, queue length, abort/compression state);
- message-level streaming state (`isStreaming`, reasoning/thinking parser state);
- tool-level running state (`toolStatus: 'running'`);
- UI components that render GIF/stop controls from those states.

A refresh fixing the UI is strong evidence that the server state is correct and the live event path is incomplete.

## Fix pattern

1. Compare event traces for a normal user-message run vs the command/continuation path.
2. Identify the structured event/state update that makes normal runs enter `working`.
3. Make command continuations emit or handle the same lifecycle transition.
4. Update client state by `session_id`; never leak working state into another active session.
5. Clear state symmetrically on success, failure, stop, abort, and disconnect/reconnect recovery.
6. Keep `resumeSession(... data.isWorking ...)` as hydration/recovery, not the only way the UI becomes correct.

Prefer a structured run lifecycle event or existing run-start event. Avoid text-sniffing assistant content like `Continuing toward goal` unless no structured event exists and the PR documents why.

## Streaming/thinking bubble merge contract

When a run emits `reasoning.delta` / `thinking.delta`, then `tool.started`, then `message.delta` or `run.completed(parsed_content)`, keep one assistant bubble for that run and append the final answer text into the existing assistant/reasoning message. Do not create extra `Thinking` bubbles just because a tool event occurred between reasoning and answer text.

Fix this at the store/state merge layer, not by hiding duplicate bubbles in `MessageItem.vue` CSS/templates. `tool.started` should update tool/runtime state; it should not reset the target assistant message for subsequent deltas.

## Verification

- Trigger a normal message run and record which event/state makes the thinking UI appear.
- Trigger `/goal` continuation and verify the same effective working state appears immediately without refresh.
- Verify the thinking GIF, stop/disabled controls, and any status dots all agree.
- Verify completion, failure, stop, and abort clear working UI.
- Verify switching sessions does not show another session's working state.
- Add client-store regressions for `reasoning.delta -> tool.started -> message.delta` and `reasoning.delta -> tool.started -> run.completed(parsed_content)`: both should render as one assistant bubble.

## Pitfalls

- Do not fix only the status dots if the GIF/controls are still stale; the user-visible contract is the entire thinking/working visualization.
- Do not infer lifecycle from localized/display text; messages are presentation, not state.
- Do not set a global `isWorking` flag without session scoping.
- Do not rely on page refresh as acceptable recovery for active runs.
- Do not “solve” duplicate thinking bubbles in presentation only; duplicated run/message state will still break previews, receipts, and later merges.
