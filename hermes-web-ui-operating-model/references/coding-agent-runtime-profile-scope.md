# Coding-agent runtime vs Hermes profile scope

Use this when explaining or editing the New Chat flow that lets the user choose Hermes / Claude Code / Codex.

## Source-of-truth distinction

The Agent selector chooses the runtime that will handle the chat:

- `Hermes` => normal Hermes Agent session (`source: cli`, Hermes profile runtime, tools, skills, memory).
- `Claude Code` => external `claude` CLI wrapped by Web UI (`source: coding_agent`, `coding_agent_id: claude-code`).
- `Codex` => external `codex` CLI wrapped by Web UI (`source: coding_agent`, `coding_agent_id: codex`).

Do not describe Claude Code / Codex as merely model choices. They are separate agent runtimes.

## What Profiles means for coding agents

In `packages/client/src/components/hermes/chat/ChatPanel.vue`, the New Chat drawer passes `profile: newChatProfile.value` into `chatStore.startDraftChat(...)`. The client then sends that profile in the run payload for both Hermes and coding-agent sessions.

For coding agents, the selected Hermes profile is mainly a namespace/config scope:

- session storage profile;
- profile-specific provider/model catalog;
- provider credentials/config read from the selected profile (`config.yaml` / `.env`);
- scoped coding-agent config directory under Web UI state, keyed by `<profile>/<provider>/<agent>`;
- scoped default workspace directory under Web UI state, keyed by `<profile>/<provider>` when no explicit workspace is selected.

It is not, by itself, a Kira memory/skills bridge.

## What is not injected today

Unless a separate bridge is implemented, a Web UI-launched Codex / Claude Code session does **not** automatically receive:

- Hermes memory;
- Kira user profile;
- Hermes skills;
- session_search context;
- current assistant/deputy instructions;
- Paperclip/Kira conventions except those discoverable from repo docs like `AGENTS.md`, `CLAUDE.md`, etc.

## UX pitfall

A field labeled only `Profiles` in the Codex/Claude Code New Chat drawer can mislead the user into thinking the external agent will inherit the selected Hermes profile's memory and skills.

Prefer labeling/copy such as:

- `Hermes profile` or `Config profile` instead of bare `Profiles`;
- hint: `Selects model/provider settings and where the session is stored. Does not inject Hermes memory or skills into Codex/Claude Code.`

For a real value-add, consider an explicit `Inject Kira context` option that generates scoped `AGENTS.md` / `CLAUDE.md` from selected profile rules, project docs, and selected skills before launch.

## Codex OAuth vs scoped provider/model

When Maxim asks whether Codex can be connected through OAuth, check the existing Codex auth path before assuming API-only support:

- `packages/server/src/routes/hermes/codex-auth.ts` exposes `/api/hermes/auth/codex/start` and related status/poll endpoints.
- `packages/server/src/controllers/hermes/codex-auth.ts` implements OpenAI Codex device auth and saves tokens both to the selected Hermes profile `auth.json` (`providers.openai-codex`) and to Codex CLI auth (`~/.codex/auth.json`, or `CODEX_HOME/auth.json`).
- The `OpenAI Codex` provider exists in `packages/server/src/shared/providers.ts` with `value: 'openai-codex'` and ChatGPT Codex backend URL.

Important distinction:

- `Codex` + `Global config` can use the Codex CLI's OAuth login/auth file today.
- `Codex` + scoped `Provider and model` mode currently blocks OAuth/subscription providers such as `openai-codex`, `copilot`, `xai-oauth`, and `nous` via `CODING_AGENT_SCOPED_AUTH_PROVIDERS` in `packages/server/src/services/coding-agents.ts`.

Do not present this as “Codex OAuth is impossible.” The accurate answer is: global Codex OAuth exists; profile-scoped Codex OAuth launch is not yet wired as a first-class mode. A proper implementation would add a `Codex OAuth (profile)` mode that refreshes the selected profile's `openai-codex` token, writes an isolated scoped `CODEX_HOME/auth.json`, and launches Codex with that `CODEX_HOME` without mutating the user's global `~/.codex`.
