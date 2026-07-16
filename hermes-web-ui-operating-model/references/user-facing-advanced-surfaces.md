# User-facing advanced surfaces: Devices and Coding Agents

Use when explaining or reshaping technically named Hermes Web UI surfaces for normal users.

## Devices

The `Devices` surface is not a generic consumer device list. It is LAN peer management for trusted Hermes Web UI / Hermes Desktop instances.

User-facing explanation:
- discovers other Hermes instances on the local network;
- sends/accepts pairing requests;
- after pairing, enables remote operations against the peer: command execution, interactive terminal, upload/download, and diagnostics;
- works as a Hermes-native alternative to SSH for trusted local machines.

Good examples:
- use a laptop Web UI to run diagnostics on the home PC;
- fetch logs or upload configs between paired machines;
- launch an interactive shell on a paired machine without setting up SSH;
- approve/block inbound requests from other Hermes instances.

UX naming guidance:
- Avoid plain `Devices` in primary navigation; it is too vague.
- Prefer `Connected Machines` for user-facing language.
- Prefer `LAN Peers` / `Remote Devices` for technical/admin language.
- If not core to the current user flow, place under Settings / Advanced / Developer.

One-line UI copy:
> Pair trusted local Hermes machines to run commands, terminals, and file transfers across them.

## Hermes / Claude Code / Codex choice

This is a runtime choice, not a model/provider choice.

Explain as:
- `Hermes Agent` — the normal Kira/Hermes runtime with Hermes tools, skills, memory, profiles, cron, delegation, etc.
- `Claude Code CLI` — launch/manage Anthropic Claude Code as an external coding-agent runtime.
- `Codex CLI` — launch/manage OpenAI Codex as an external coding-agent runtime.

Important distinction:
- `Claude Code` does **not** mean “choose a Claude model”.
- `Codex` does **not** mean “choose an OpenAI model”.
- Model/provider selection is the LLM inside the selected runtime.

Practical examples:
- run Claude Code on a repository while Hermes Web UI acts as launcher/log surface;
- run Codex on the same workspace and compare implementation quality;
- use Hermes as the orchestrator/context surface and Claude/Codex as specialized coding executors;
- keep coding-agent sessions visually distinct from normal Hermes sessions.

UX naming guidance:
- Prefer label `Agent Runtime` over “chat with Hermes / Claude Code / Codex”.
- Options should be `Hermes Agent`, `Claude Code CLI`, `Codex CLI`.
- Put Claude/Codex under Developer / Coding Agents / Advanced unless the current surface is explicitly for code work.
