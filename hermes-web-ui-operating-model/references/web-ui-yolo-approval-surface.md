# Web UI YOLO / Approval Surface

Use this when Maxim asks whether Hermes Web UI can enable YOLO mode, skip approval prompts, or add an approval-bypass control.

## Current split

- Hermes Agent has the approval engine in `tools/approval.py`.
  - Session-scoped bypass exists via `enable_session_yolo(session_key)` / `disable_session_yolo(session_key)`.
  - CLI/gateway `/yolo` toggles this session-scoped bypass.
  - `approvals.mode: off` is profile/config-level and should not be treated as a per-session UI toggle.
- Hermes Web UI primarily transports approval decisions.
  - Client approval bars live in `packages/client/src/components/hermes/chat/ChatPanel.vue` and `packages/client/src/components/hermes/group-chat/GroupChatPanel.vue`.
  - Server approval response path goes through `approval.respond` → `AgentBridgeClient.approvalRespond(...)`.

## Important current pitfall

Do not tell Maxim that typing `/yolo` in Hermes Web UI already works unless verified in the current checkout.

In the observed Web UI implementation, slash commands are whitelisted in:

- `packages/server/src/services/hermes/run-chat/session-command.ts`

`COMMAND_ALIASES` included `/usage`, `/status`, `/abort`, `/queue`, `/plan`, `/goal`, `/subgoal`, `/clear`, `/title`, `/compress`, `/steer`, `/destroy`, `/reload-mcp`, but not `/yolo`. Unknown commands return an `Unknown bridge command: /<name>` message.

The bridge file also had `dispatch_command(...)` support for goal/subgoal and skill/bundle command dispatch, not a generic Hermes CLI command runner.

## Recommended feature shape

If implementing Web UI YOLO:

1. Add an explicit session-scoped `/yolo` command in `session-command.ts` rather than routing arbitrary slash commands to the Hermes CLI.
2. Add bridge client support that calls Hermes Agent's session yolo functions for the same approval/session key used by Web UI runs.
3. Add Python bridge action support **and register the action in the bridge broker/dispatch allow-list**. A common failure mode is adding a `yolo_toggle` handler but forgetting to include it in the action set, causing runtime socket calls to fail with `unknown action: yolo_toggle` even though source-level plumbing exists.
4. Make the command toggle state and return a clear command message: enabled/disabled, session-only, hardline guard still active.
5. Reflect state in `/status` and optionally in the approval bar, composer toggle, or session header as a small "YOLO session" indicator.
6. Keep it session-only by default. Do not silently set `approvals.mode: off` for the whole profile.
7. Preserve hardline semantics: catastrophic commands and sudo-stdin password guessing remain blocked even when YOLO is enabled.

## Tests and runtime probes

- Add a server contract for `/yolo` in `session-command.ts`.
- Add a bridge-routing regression test that proves the Python bridge accepts the new action name and dispatches it, not only that the TypeScript client exposes a method.
- For the live runtime, probe the bridge/socket path directly or through the Web UI command and check for `unknown action` errors before declaring the slash command fixed.
- If a composer toggle is added, expose real pressed state with `aria-pressed` and keep it in the shared compact binary-control grammar.

## Wording to use

Verdict: Hermes Agent supports session YOLO, but Hermes Web UI may not expose it yet. Verify `COMMAND_ALIASES` and bridge support before answering. If absent, say the feature is possible but needs a Web UI command/toggle implementation.
