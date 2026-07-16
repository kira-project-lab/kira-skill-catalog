# Session Preview vs Runtime State

Use this reference when session-card previews or status badges start surfacing intermediate agent activity.

## What went wrong in this session

The UI was treating several technical events as if they were the final visible message:

- `thinking` / `reasoning` deltas
- `tool.started` / `tool.completed`
- command/system messages
- queued or in-flight assistant fragments

That caused two symptoms:

1. **Preview message drift** — the session card preview could be replaced by a tool/thinking fragment instead of the last user-facing message.
2. **Running flicker** — `running` could briefly disappear when the client refetched session summaries or replayed socket state out of order.

## Ground rule

Split the state into two concepts:

- **Visible preview**: the last user-facing or final assistant message that should represent the conversation card.
- **Technical runtime**: running / queued / approval / clarification / error, which should be driven by runtime state and not by preview text.

ADR-007 now codifies this as the **business-visible session preview contract**: preview and unread targets must come from the same business-visible message selection, and transient reasoning/tool chatter must not override that selection.

Do not let transient reasoning/tool chatter become the card preview unless the product explicitly wants to expose it.

## Implementation notes

Relevant code paths in this repo:

- `packages/client/src/stores/hermes/chat.ts`
  - `refreshSessionPreview()` currently uses the last message in the session, so technical messages can override the preview.
  - streaming/runtime state is merged from `serverWorking`, `streamStates`, queue state, and replayed socket events; short gaps can appear during reconnect/refetch.
- `packages/server/src/db/hermes/sessions-db.ts`
  - `last_message_preview` and `last_message_role` are derived from the most recent stored message, even if it is technical.
- `packages/server/src/db/hermes/session-read-receipts-store.ts`
  - `getLatestRelevantMessage()` currently treats assistant/tool/command as relevant for read state.
- `packages/server/src/services/hermes/session-row-status.ts`
  - row state is assembled from read + runtime; keep this authoritative, but avoid mixing it with preview text.

## Repair pattern

When fixing this class of bug:

1. Decide which messages are **visible** versus **technical**.
2. Derive preview from the visible subset only.
3. During an active run, keep the row/card preview on the latest user or queued-user message; do not let interim assistant text, including assistant chunks closed by tool starts, become the committed preview before `run.completed` / `run.failed` / `abort.completed`.
4. Keep runtime status authoritative and separate.
5. Persist a server-side preview snapshot (`preview_message_id`, `preview_message_role`, `preview_message_at`) so the client does not reconstruct preview from the raw tail on every render.
6. If the UI still flickers, stabilize the client with last-known runtime state until the next authoritative event arrives.

A useful diagnostic question: “Does the Stop button still think this run is active?” If yes, the session row must still use active-run preview/status rules even if local message events have created or closed assistant/tool messages.

## Contract detail from ADR-007

- The row/card preview should come from a business-visible message, not from transient reasoning/tool events.
- The preview selector and the read-target selector must agree on the same business-visible concept, otherwise the card can show one message while unread logic is tracking another.
- A technical event may still change runtime state, but it must not become the visible preview unless explicitly requested by product.

## Pitfalls

- Do not use the newest message blindly for session previews.
- Do not use `thinking` or tool chatter to decide that a run is “done”.
- Do not conflate read/unread with runtime progress; they answer different questions.
- If read-state must track the latest visible agent output, update the server-side relevance filter instead of patching only the client.
