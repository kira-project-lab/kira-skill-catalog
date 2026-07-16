# Hermes Agent approval guard in Hermes Web UI

Use this when Maxim asks what the Web UI "Allow", "Allow session", "Always", or approval guard means, or when designing features that reduce manual approval friction.

## Source of truth

The approval policy is owned by Hermes Agent, not Hermes Web UI.

- Agent policy/source: `~/.hermes/hermes-agent/tools/approval.py`
- Terminal pre-exec hook: `~/.hermes/hermes-agent/tools/terminal_tool.py` calls `check_all_command_guards(...)`
- Web UI bridge client: `packages/server/src/services/hermes/agent-bridge/client.ts`
- Web UI run socket handler: `packages/server/src/services/hermes/run-chat/index.ts`
- Web UI bridge event projection: `packages/server/src/services/hermes/run-chat/handle-bridge-run.ts`
- Client single chat approval bar: `packages/client/src/components/hermes/chat/ChatPanel.vue`
- Client group chat approval bar: `packages/client/src/components/hermes/group-chat/GroupChatPanel.vue`

## Mental model

Hermes Web UI is mostly the transport and UX surface for approval events. Do not describe the Web UI as the owner of the guard.

Flow:

1. Agent is about to run a terminal command.
2. `terminal_tool.py` calls the consolidated guard.
3. `approval.py` checks hardline blocks, sudo-stdin guard, dangerous-command patterns, Tirith findings, yolo/off/smart/session/permanent approval state.
4. In gateway/Web UI contexts, the agent thread waits on a queued approval entry.
5. The bridge emits `approval.requested` to Web UI.
6. Web UI sends `approval.respond` with a choice.
7. The bridge/agent resolves and emits `approval.resolved`.

## Choice semantics

- `once`: allow only the current command execution; no persistence.
- `session`: `approve_session(session_key, pattern_key)`; allows the same pattern for the current approval session.
- `always`: persists the pattern to `command_allowlist` in config, but Tirith findings are intentionally session-only even when the user chooses always.
- `deny`: hard block; the agent is told not to retry, rephrase, or attempt the same outcome via another command.

## Bypass and policy modes

- CLI/process yolo: `HERMES_YOLO_MODE` / `--yolo`.
- Session yolo: in-memory session-scoped bypass.
- Config: `approvals.mode: off` bypasses ordinary approval prompts.
- Config: `approvals.mode: smart` asks the auxiliary approval model to approve/deny/escalate before manual prompt.
- Cron: governed by `approvals.cron_mode`.

Hardline blocks and the sudo-stdin guard remain below these bypasses: they are not ordinary approvals.

## Design pitfall

If the requested feature is "stop making me click Allow / Allow session", do not only hide or auto-click the Web UI buttons. Choose the policy layer explicitly:

- session-level yolo/allowlist for a specific active session;
- smarter default `approvals.mode` behavior;
- better command pattern granularity;
- profile-level settings UI for approvals;
- or a safer workflow that avoids triggering dangerous patterns.

State clearly which layer is being changed and what risk boundary remains.