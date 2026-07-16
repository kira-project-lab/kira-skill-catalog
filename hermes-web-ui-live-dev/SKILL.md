---
name: hermes-web-ui-live-dev
description: "Operate Hermes Web UI live-dev on hermes.dev.ops.kiraproject.ru: persistent watch-based runtime, HMR, backend restart loop, runtime identity, and verification."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [devops, hermes, web-ui, live-dev, hot-reload, hmr]
---

# Hermes Web UI Live Dev

Use this skill when the task is about the persistent live-dev runtime for Hermes Web UI on `https://app.dev.kiraproject.ru`. Older notes may mention `hermes.dev.ops.kiraproject.ru`; treat that as a legacy hostname and verify DNS plus `/health` before relying on it.

This is **not** the branch-preview deploy flow. The goal is the fast inner-loop runtime:

- frontend edits should appear via Vite HMR;
- backend edits should restart automatically via the watch process;
- the dev hostname should keep serving the same live surface without a rebuild/deploy cycle for every small change;
- live-dev state must stay isolated from production state.

## Canonical runtime shape

- checkout: `/home/werserk/2-kira/hermes-web-ui-dev`
- service: `hermes-web-ui-dev.service`
- public host: `https://app.dev.kiraproject.ru`
- legacy/previous host reference: `hermes.dev.ops.kiraproject.ru` (verify DNS/health before using it in reports or tests)
- frontend port: `8649`
- backend port: `8647`
- startup command: `bash scripts/start-live-dev.sh`
- health check: `curl -fsS http://127.0.0.1:8649/health` (public/frontend health surface; backend 8647 may not expose `/health` directly in live-dev)
- transition notes: `references/live-dev-transition.md`

## Operational model

1. Start the persistent watch runtime with `scripts/start-live-dev.sh`.
2. Edit files in the live-dev checkout.
3. Let Vite HMR handle frontend updates.
4. Let nodemon restart the backend process for server-side changes.
5. Verify the browser, websocket connection, and `/health` metadata.
6. For Maxim's small Hermes Web UI design-fix requests, default to committing and pushing the finished change to `origin/dev` unless he explicitly says not to.
7. After pushing a commit to the live-dev branch, restart the user-unit service so the runtime picks up the new checkout SHA and refreshes the build-info metadata: `systemctl --user restart hermes-web-ui-dev.service`. Do not use plain `systemctl` or `sudo systemctl` first; system-level restart attempts can fail with interactive-auth/sudo prompts while leaving `/health` on the old commit.
8. If the current tool session cannot access the user unit, fall back to the documented startup script from the dev checkout: `bash scripts/start-live-dev.sh`. Run it as a tracked background process in agent sessions, not shell-backgrounded with `&`, then verify `http://127.0.0.1:8649/health` and the public dev host. See `references/live-dev-restart-and-verify.md`.
9. If `/health` returns a transient 502 during restart, poll until it comes back green and shows the new `git_commit`.
10. Report compactly: changed surface, commit hash, and whether the public dev host is on that hash.

## Health expectations

`/health` should show:

- `runtime: live-dev`
- the active branch / checkout identity
- the current commit SHA
- `service: hermes-web-ui-dev.service`
- `service_port: 8647`
- `frontend_port: 8649`

If the runtime says `branch-preview`, the host is in the explicit review workflow, not the default live-dev mode.

## Common failure modes

- HMR reconnects fail because the proxy or websocket path is wrong.
- The backend restarts but the browser still points at a stale tab or cached asset.
- Health shows the wrong runtime because the build metadata file is stale.
- A push can be correct in git but still not active on the public dev host until `hermes-web-ui-dev.service` is restarted and `/health` reports the new `git_commit`.
- The first `/health` probe after restart may briefly return `502`; poll until the endpoint is green and the commit matches.
- Someone accidentally used the branch-preview deploy flow instead of the live-dev start script.
- A “slider” request is actually about scrollbars or textarea resizing: verify whether the target is the page scrollbar (`.app-main`), a textarea scrollbar (`.input-textarea` / `NInput type="textarea"`), or the resize handle (`.resize-handle`) before styling.
- Chat header/session-sidebar border alignment can look off by 1–2px even when both headers have the same `$header-height`; inspect `.session-list-resize-handle` as a full-height overlay at the T-junction before changing header height. See `references/chat-session-sidebar-anatomy.md`.
- If the session-list separator looks split or shorter than the navigation separator, compare `.session-list-resize-handle` to `.sidebar-resize-handle`: both should be full-height overlays (`top: 0; bottom: 0`) with the visible 1px line in `::after`, not a handle starting below `$header-height`. See `references/resize-separator-visual-contract.md`.
- The public hostname is blocked by Vite until `server.allowedHosts` includes `hermes.dev.ops.kiraproject.ru`; see `references/public-host-allowlist.md`.
- Session-row UI details can differ between ADRs, tests, and the live checkout. Before claiming a session list status element is absent, inspect the current `SessionListItem.vue` and confirm the rendered browser DOM on the live-dev host.
- For sidebar/nav visual state fixes, inspect the shared style source before patching individual route links: `.route-link-item.nav-item` often inherits from `packages/client/src/styles/action-buttons.scss` via `@include actionButtons.action-button-shell(auto)`. If Maxim asks for all nav buttons to change, update the shared mixin and verify a concrete route link in the browser with `getComputedStyle` plus the served `:hover` CSS rule.
- For icon-button frame complaints, do not stop at `outline: none`: what looks like an outline may be `border`, `box-shadow`, or Naive UI internal state layers. Check `outlineStyle`, `border`, `boxShadow`, and dimensions for `.route-link-item.nav-item`, `button.nav-item`, `.theme-switch`, and `.header-action-button`. Keep these controls frame-free by default, hover-filled via `$state-hover-bg`, and make panel/theme icon buttons compact equal squares. See `references/icon-button-visual-contract.md`.
- For sidebar/panel tooltip requests, match the composer button tooltip design by using `NTooltip` rather than native `title`, typically with a `50ms` delay when Maxim asks for comments to appear 2x faster. Preserve `aria-label`, anchor `href`, and parent classes when wrapping `RouteLinkItem`; see `references/sidebar-tooltip-contract.md`.
- For chat model switching fixes, UI evidence is not enough. Verify the outbound Socket.IO `run` payload includes the selected `model/provider`, then verify the same session in `bridge.log` resolved to that model. Include active/queued-run switching when the user asks about switching “during conversation”; see `references/chat-model-switch-qa.md`.
- For live-dev session inventory questions, use the agentmemory session API directly; current observed session statuses in this workspace are `active` and `completed`. See `references/live-dev-session-statuses.md` for the compact query note.

- After pushing a new commit, the service may still expose the previous `git_commit` until the user unit is restarted with `systemctl --user restart hermes-web-ui-dev.service`; poll `/health` and retry through brief `502` windows.

## Verification shortcut

When checking whether a live-dev change is active on `hermes.dev.ops.kiraproject.ru`, compare these facts in order:

1. Fetch the branch you care about before trusting the remote-tracking ref: `git fetch origin dev`.
2. Check the local checkout state: `git status --short --branch` and `git rev-parse HEAD`.
3. Compare the fetched remote ref: `git rev-parse origin/dev`.
4. Compare the running service: `curl -fsS https://hermes.dev.ops.kiraproject.ru/health` and read `runtime`, `git_branch`, `git_ref`, and `git_commit`.
5. If the question is about the session list inventory or dates, query `/home/werserk/.hermes-web-ui/hermes-web-ui.db` directly; do not use the profile-scoped `state.db` as a proxy for UI session rows.

A live-dev change is active only when:

- the checkout is on the expected branch,
- the worktree is clean,
- the fetched remote-tracking commit matches the intended ref,
- and `/health` reports the same commit for the running service.

If local `HEAD` and `origin/dev` match but `/health` lags behind, the runtime is stale: restart `hermes-web-ui-dev.service` and poll `/health` until it reports the new commit.

See `references/live-dev-verification.md` and `references/live-dev-session-inventory.md` for the compact probe checklists.

## Support files

- `references/public-host-allowlist.md` — blocked-request / allowedHosts fix pattern for the public dev hostname.
- `references/scrollbar-and-resize-handle.md` — map of page scrollbar vs textarea scrollbar vs resize-handle styling in Hermes Web UI.
- `references/live-dev-restart-and-verify.md` — commit/push/restart/poll pattern for getting the public dev host to pick up a new ref.
- `references/reset-dev-to-main.md` — destructive but approved flow for recreating `origin/dev` as an exact clone of `origin/main`, including `--force-with-lease`, service restart, and public `/health` verification.
- `references/live-dev-verification.md` — minimal checklist for deciding whether a change is actually active on the public dev host.
- `references/live-dev-session-inventory.md` — where the live-dev session list data lives and how to query its date range.
- `references/chat-model-switch-qa.md` — how to prove chat model switching is real across UI state, Socket.IO run payload, and backend bridge logs, including queued active-run checks.
- `references/session-row-status-removal.md` — exact cleanup pattern for removing the session-list status dot from the live-dev checkout and updating the stale tests with it.
- `references/session-sidebar-launchers.md` — pattern for replacing the session sidebar header/filter with two equal-width launchers.
- `references/chat-session-sidebar-anatomy.md` — map of the Chat session sidebar, header controls, session body, and interactive resize separator.
- `references/chat-session-state-stability-debugging.md` — route/session/status state-ownership checklist for `/chat` draft-mode bugs, stale A/B session-detail races, and row-status drift.

## Guardrails

- Do not copy built assets between prod and live-dev folders.
- Do not treat `deploy-dev-branch.sh` as the default dev-host path.
- Keep production and live-dev state directories separate.
- Verify runtime identity before debugging application code.
- Before removing a UI element from the live-dev checkout, verify the current tree and the actual rendered DOM; do not rely on an earlier snapshot or on assumptions about what a sibling checkout contains.
- When replacing the top session-sidebar controls, prefer a two-column equal-width layout with a visible gap and no inset strip padding; confirm the buttons are not visually merged in the browser.
