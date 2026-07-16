# Chat model switching QA

Use this when verifying that Hermes Web UI chat model switching is real, not only visual.

## What to prove

A valid check must prove all three layers:

1. **UI state**: the chat header/model chip changes to the selected model.
2. **Socket payload**: the next `chat-run` Socket.IO `run` event includes the selected `model` and `provider`.
3. **Backend bridge resolution**: `bridge.log` for the same `sessionId` records the selected `model`/`provider` in `[chat-run-socket] fixed/local/final context estimate` entries.

UI-only evidence is insufficient.

## Agent-browser probe

In a logged-in browser page, patch outbound WebSocket sends before sending messages:

```js
window.__qaSentWs = []
const origSend = WebSocket.prototype.send
if (!WebSocket.prototype.__qaPatched) {
  WebSocket.prototype.send = function(data) {
    try {
      if (typeof data === 'string' && data.includes('"run"')) window.__qaSentWs.push(data)
    } catch {}
    return origSend.apply(this, arguments)
  }
  WebSocket.prototype.__qaPatched = true
}
```

Then run this sequence:

1. Create a new chat on model A.
2. Send a first message and confirm `window.__qaSentWs` contains `"model":"<A>"` and the expected provider.
3. Switch the same chat to model B.
4. Send the next message in the same chat.
5. Confirm the second `run` payload contains `"model":"<B>"` and the expected provider.
6. For the active/queued path, start a long-running run, switch model while it is active, send a queued message, and confirm that queued message's run payload carries the switched model.

If accessibility refs do not reliably select a model row, dispatch a DOM click on the actual `.model-item`:

```js
(() => {
  const el = Array.from(document.querySelectorAll('.model-item'))
    .find(x => x.textContent?.trim() === 'gpt-5.5')
  el?.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }))
  return { clicked: !!el }
})()
```

Avoid top-level `const item = ...` in repeated `agent-browser eval --stdin` calls on the same page; Chromium may treat it as a duplicate global declaration. Wrap probes in an IIFE.

## Backend confirmation

After collecting the browser session id, check the live-dev bridge log for the same id:

```bash
grep '<session-id>' /home/werserk/.hermes-web-ui-dev/logs/bridge.log \
  | grep -E 'model":"gpt-5\.4-mini|model":"gpt-5\.5' \
  | tail -20
```

The log should show the pre-switch run under model A and the post-switch/queued run under model B. If the browser payload changed but `bridge.log` did not, the server-side model resolution path is still wrong.

## Known root cause pattern

For normal CLI chats, switching must not be treated as first-message-only config. The client should include `model/provider` on every run for CLI sessions, and server-side bridge model resolution should prefer explicit requested `model/provider` over stale local session mirror values.
