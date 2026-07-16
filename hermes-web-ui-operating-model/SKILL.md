---
name: hermes-web-ui-operating-model
description: "Mandatory entrypoint for Hermes Web UI planned work: branches, builds, previews, production deploys, runtime topology, and release/export decisions."
---

# Hermes Web UI Operating Model

Use this skill before code changes, branch decisions, build/preview/deploy work, or runtime topology changes.

For live service/runtime evidence, pair it with `hermes-web-ui-service-ops`.

## Known Kira topology

- Canonical checkout: `/home/werserk/2-kira/hermes-web-ui`
- Canonical repo: `https://github.com/kira-project-lab/hermes-web-ui.git` (`origin`)
- Upstream repo: `https://github.com/EKKOLearnAI/hermes-web-ui.git` (`upstream`, push disabled)
- Production public URL: `https://app.kiraproject.ru/`
- Dev public URL: `https://app.dev.kiraproject.ru/`
- Production service: `hermes-web-ui.service`
- Production source: `origin/main`
- Production command: `/usr/bin/node /home/werserk/2-kira/hermes-web-ui/dist/server/index.js`
- Production port: `127.0.0.1:8648`
- Live-dev runtime: `/home/werserk/2-kira/hermes-web-ui-dev` → `hermes-web-ui-dev.service` → frontend `8649`, backend `8647`
- Live-dev startup command: `bash scripts/start-live-dev.sh`
- Branch-preview command: `bash scripts/deploy-dev-branch.sh <branch>`
- Live-dev transition contract: `references/live-dev-transition.md`
- Dev worktree merge flow and "main → dev" carry-forward: `references/dev-worktree-merge-flow.md`
- Branch discipline for the canonical Web UI checkout: `references/branch-discipline.md`

## Source-of-truth rules

- Private canonical repo is the working source of truth: `kira-project-lab/hermes-web-ui`.
- Production runs from `origin/main`.
- `origin/dev` is the integration/review branch for feature work that should merge before `main`.
- For ongoing implementation after a carry-forward merge, the live-dev worktree `/home/werserk/2-kira/hermes-web-ui-dev` is the default place to continue editing.
- Do not edit `/home/werserk/2-kira/hermes-web-ui` on `main` or `dev` directly. If source changes are actually needed there, create a separate task branch first; for beta-10/ops acceptance work, assume Web UI source changes are unnecessary until evidence says otherwise. See `references/branch-discipline.md`.
- When a plan stored in the Hermes Web UI repo explicitly creates a standalone sibling project (for example under `/home/werserk/2-kira/<new-project>`), treat the Web UI repo as the planning source only: inspect/leave its git state clean, then implement in the standalone workspace rather than forcing the work into live-dev.
- Live-dev and branch-preview are separate runtime modes; verify which one is active before choosing a workflow.
- Do not mix production state with live-dev state.
- Use separate checkout/worktree, port, state dir, and upload dir for preview/live-dev runtimes.

## Dispatch table

| Task shape | Follow |
|---|---|
| Feature, bugfix, refactor, UI copy, tests | This skill, then project docs (`AGENTS.md`, `DEVELOPMENT.md`) |
| Version update / upstream release merge | `references/update-version-runbook.md`; for merging author `upstream/main` into Kira `dev`, use `references/upstream-main-to-dev-merge.md` and `references/upstream-main-merge-validation-pitfalls.md` |
| Live-dev runtime / live reload / dev-host topology | `hermes-web-ui-live-dev` + `hermes-web-ui-service-ops` |
| Branch-preview deploy | `hermes-web-ui-service-ops` + `references/dev-pr-branch-deploy.md` |
| Live service, port, logs, health, SQLite, restart, active checkout | `hermes-web-ui-service-ops` |
| UI behavior differs from source | `hermes-web-ui-service-ops` + live bundle verification reference |
| Bridge timeout/socket/Broken pipe/runtime-provider mismatch | `hermes-web-ui-service-ops` + `references/bridge-boundary-troubleshooting.md` |
| Allow / Allow session / approval guard behavior or reducing manual approval friction | `hermes-agent` + `references/agent-approval-guard-surface.md`; remember Web UI is the transport/UX surface, Hermes Agent owns policy |
| Session stuck/already running/compression/session route issue | `hermes-web-ui-service-ops` + `references/session-runtime-ops.md` |
| DNS/Caddy/public hostname/service promotion | Use the appropriate ops skill; keep this repo focused on app code/builds |
| Upstream PR to original author | Export through legacy fork only after local merge/approval |

## UI/UX surface shaping

For approval prompts, Allow once/session/always semantics, or a requested Web UI YOLO toggle, first read `references/web-ui-yolo-approval-surface.md`: Hermes Agent has session YOLO, but Web UI may not expose `/yolo` unless `session-command.ts` and bridge support have been implemented. Treat toggle-only YOLO as a cross-device/state-drift risk: prefer explicit set/get policy state, broadcast snapshots to all session clients, and catch up on resume before presenting `Allow all` as durable.

Use this pattern when a Web UI page has become too technical for the primary user flow:

- Split the main surface by user intent first, not by internal subsystem.
- Prefer two clear surfaces over one overloaded screen when the actions naturally differ.
- Keep the header status-first and move technical/runtime detail into a disclosure or secondary panel.
- Preserve the existing visual system when possible; the goal is clearer information architecture, not a redesign for its own sake.
- If the selection model depends on record state, keep the primary action surface and the management surface synchronized after catalog mutations.

For the voice-panel-specific version of this pattern, see `references/voice-surface-ia-refresh.md`.
For voice-panel-specific version of this pattern, see `references/voice-surface-ia-refresh.md`.
For voice recording/transcription architecture, STT provider runtime checks, Ollama/faster-whisper pitfalls, and the Hermes Agent STT vs Web UI STT distinction, see `references/voice-stt-provider-runtime.md`.
For technically named advanced surfaces such as Devices and Hermes / Claude Code / Codex runtime selection, see `references/user-facing-advanced-surfaces.md`: explain user use-cases first, distinguish source-of-truth runtime from model/provider, and prefer user-facing names such as `Connected Machines` and `Agent Runtime` over vague labels.
For textarea scrollbar/resizer and page-scrollbar overlay behavior, see `references/voice-textarea-and-page-scrollbar-contract.md`.
For chat/session panes that can be over-scrolled until the whole surface disappears, see `references/chat-scroll-containment.md`.
For command-driven continuations where the agent keeps working but the chat UI loses the thinking/working visualization until refresh, see `references/chat-run-lifecycle-visualization.md`.
For bounded user-resizable layout regions such as the app sidebar, chat session list, or composer/input panel, see `references/resizable-layout-panels.md`.
For the session-list-launchers-and-preview pattern, and for the "Search" + "New Chat" launcher pattern that replaces an overloaded header/filter cluster, see `references/session-list-launchers-and-preview.md`.
For the current new-chat creation flow — desktop modal vs mobile/hotkey direct-create, local store session creation, and composer-focus after confirm — see `references/new-chat-creation-flow.md`.
For draft-to-session UX where a blank persistent row is undesirable, see `references/new-chat-draft-session-flow.md`.
For the Hermes / Claude Code / Codex New Chat runtime selector, including why Hermes profiles appear for coding agents and why that does not imply memory/skills injection, see `references/coding-agent-runtime-profile-scope.md`.
  - Practical pitfall: if a New Chat drawer shows only labels such as `Agent`, `Profiles`, `Provider`, or `Models` but no select controls, first check that every Naive UI component used in the template is imported in `ChatPanel.vue` (especially `NSelect`). A missing component import can make the control vanish while adjacent labels and imported controls such as `FolderPicker`/`NInput` still render, which looks like empty model/profile data but is actually a component-resolution/UI bug.
For the Hermes / Claude Code / Codex New Chat runtime selector, including why Hermes profiles appear for coding agents and why that does not imply memory/skills injection, see `references/coding-agent-runtime-profile-scope.md`.
  - Practical pitfall: when a user says they "cannot choose model/options for a new chat," first identify the entrypoint and runtime mode. Desktop New Chat can expose provider/model fields, while mobile New Chat and `Cmd/Ctrl+N` go straight to draft creation, and global coding-agent mode intentionally hides provider/model. Do not call that a broken selector until you have checked the mode.
  - Practical pitfall: when Maxim asks how new-chat creation works or whether to change it, explicitly separate **client-local session row**, **route/active composer state**, and **durable server/DB session**. In the current flow `chatStore.newChat()` can create a local empty row before the server materializes a session on first run, so do not describe the problem as purely server-side persistence.
  - Practical pitfall: when Maxim asks to simplify a sessions pane header from a label such as `Sessions` to only Search/New Chat controls, remove the title DOM instead of hiding it, keep the accessible labels/tooltips on the controls, and set the pane header alignment explicitly left/start (for example `.session-pane-header { justify-content: flex-start; }`). Protect this with a source contract that the title template/class is absent and the toolbar/actions remain.

For the session-row right-click menu contract — order, dividers, icons, brighter text, instant hover, and red destructive action styling — see `references/session-context-menu-actions.md`.
For chat mobile/desktop parity around composer Enter behavior, desktop-only chat header actions, and routing header actions such as Conversation outline through the session context menu, see `references/chat-mobile-parity-and-context-menu-actions.md`.
For mobile session drawer launcher parity, keep the Filter control between Search and New and make it reuse the desktop identity/tag filtering semantics; see `references/mobile-session-filter-parity.md`.
For reusable compact action-button styling across composer controls and sidebar/navigation links — including short hints, preserving anchor behavior for middle-click/new-tab, and semantic composer states such as append/queue using the queued-message info accent — use `references/action-button-link-controls.md`.
For mobile browser “Add to Home Screen”/iOS shortcut icon support, add `apple-touch-icon`, a web manifest, and public PNG assets; see `references/mobile-web-app-icons.md`.
For the session-vs-history distinction, why the history list grows, and the exact UI projections over the same records, see `references/session-vs-history.md`.
For chat/session rows with title/profile/time/status-dot/action-menu layout, see `references/session-row-layout-status.md`.
For the current three-row session card with a full-height left avatar, preview-only second row, persistent profile/runtime/custom tag row, reusable tag management, and session-list profile/runtime/tag filters, see `references/session-card-badges-and-avatar.md`.
For session tag assignment UX, prefer the Telegram-like `Tags ›` context submenu with immediate membership toggles, separate `Create and add`, and separate `Manage tags…`; keep destructive reusable-tag deletion out of the fast assignment path. Use `references/session-tag-assignment-telegram.md` for implementation/test/browser-QA details. Canonical repo ADR: `docs/adr/ADR-011 — Telegram-Like Session Tag Assignment.md`.
For post-merge/update regressions where chat chronology looks random, pinned sessions disappear, or session tags/badges vanish, use `references/session-list-prefs-order-recovery.md`: compare Hermes `state.db` with Web UI `user_session_browser_prefs`, inspect `__session_badges_meta__`, check pagination-before-claim and timestamp comparator drift, and backfill browser localStorage pins/badges before overwriting them with empty server prefs.
For server-authoritative chat row-state runtime transitions, read/no-dot behavior, and completion paths that bypass central socket emitters, see `references/session-row-state-runtime.md`.
For the unified session row status state machine — ADR-012, single server resolver, runtime/read/outcome facts, client projection boundaries, queue-vs-running priority, and coding-agent/external-run settlement pitfalls — see `references/session-row-status-state-machine.md`.
For stale/delayed cross-tab status-dot reports that need a deep plan before code, use `references/status-realtime-sync-rearchitecture-planning.md`: research realtime best practices, audit server/client status paths, then design versioned server snapshots plus reconnect/visibility catch-up before implementation.
For deeper audits of conflicting chat/session-list statuses, local client flags overriding `rowState.primary`, coding-agent/external-run completion bypasses, and the desired single source-of-truth priority order, use `references/session-row-status-source-of-truth-audit.md`.
For browser QA of chat status-dot scenarios, including read-receipt presence payloads, running/queued/approval/clarification probes, same-user iframe sync checks, and cleanup pitfalls, see `references/session-row-state-browser-qa.md`.
For the business-visible session preview contract, server snapshot fields (`preview_message_id` / `preview_message_role` / `preview_message_at`), visible-message filtering, and running-flicker causes, see `references/session-preview-vs-runtime-state.md` and ADR-007.
For the committed session-card snapshot contract — latest-user preview during active runs, terminal assistant commit, runtime/read/preview ordering, and stale socket/refetch protection — see `references/session-card-committed-snapshot.md` and ADR-008.
For the formal session-card state contract — committed preview vs runtime status, terminal completion rules, monotonic snapshot versioning, and the never-empty second row invariant — see `references/session-card-state-contract.md`.
For auditing flickering/resetting chat status indicators against the Stop-button lifecycle source, slash-command/tool/partial-assistant events, and stable latest-user preview while a run is active, see `references/chat-status-source-audit.md`.
For the transcript-vs-visual contract for user slash commands (e.g. `/plan`), see `references/chat-slash-command-bubble-contract.md`.
For the unified read/unread + runtime-status contract (priority order, visible gates, UX rules, and read-receipt dwell/reactivity pitfalls), see `references/session-read-runtime-status.md`.
For a concise taxonomy of ordinary chat session-list statuses (`row_state.primary`), labels, visual dot meanings, priority order, and the legacy/common `MessengerRowStatusKind` pitfall, see `references/session-list-status-taxonomy.md`.
For ADR-driven removal/redesign of the fork session-list status-dot layer, including what not to delete from Ekko/live-state behavior, see `references/session-row-status-layer-removal.md`.
For ADR-006 single session-row status dot semantics after the launcher/preview row redesign, see `references/session-row-status-adr-006.md`.
  - Practical pitfall: complete `read` rows should be visually quiet and may omit the dot entirely; use the neutral dot only for missing/idle runtime state, not as a gray read indicator.
For active session rows that must not lose their visible runtime indicator, and for the no-gray-dot read-row contract, see `references/session-row-active-status-no-gray-read.md`.
  - Practical pitfall: when making `rowState` server-authoritative, keep a narrow local runtime fallback from the parent list (`streaming` / `waiting`) so a transient `read`/`idle` snapshot cannot hide an in-progress row while Stop is still available.
For stronger visual attention in session rows using a left status rail plus right-side dot/halo states, see `references/session-attention-indicator-redesign.md`.
For chat visual-system recolor work, first inventory the full visible chat screen and then reduce surfaces/decor through semantic tokens; see `references/chat-visual-system-recolor-audit.md`. For the successful Design Token Pass 1 contract — token groups, source-text regression tests, component migration order, panel-surface alignment, preserved color-differentiated status cues, circular dots/rounded rails, and live-dev verification path — see `references/design-token-pass-1.md`.
For Obsidian-inspired workspace redesigns, docked panes, pane toolbars, activity rails, right inspector panes, and UI ADRs for this direction, use `references/obsidian-like-workspace-shell.md`.
For aligning top separators across the activity rail, session pane, and main chat pane into one continuous workspace line, use `references/workspace-header-alignment.md`.
For chat composer binary controls such as autoplay speech and tool trace visibility, and for keeping the composer input shell radius aligned with composer action buttons, use `references/chat-composer-toggle-controls.md`.
  - Practical pitfall: if Maxim says these toggles should be "on the right" or "right of tokens", place them in the **same lower composer toolbar row as the textarea**, not in the header/top bar above the textarea. The intended anchor is the textarea section's right edge, so the controls should be part of the row that also contains attach/send, with the toggle group pushed to the far right.
  For the chat composer binary controls such as autoplay speech and tool trace visibility, and for keeping the composer input shell radius aligned with composer action buttons, use `references/chat-composer-toggle-controls.md`.
  For the chat composer binary controls such as autoplay speech and tool trace visibility, and for keeping the composer input shell radius aligned with composer action buttons, use `references/chat-composer-toggle-controls.md`.
  For the right-edge contract on those same toggles — keep them in the top composer section, make the row full-width, and pin the toggle group to the far right instead of moving it into the lower toolbar — see `references/chat-composer-toggle-right-edge.md`.
  For the chat composer voice layout contract — attach left, mic/send right, and recording as an inline strip between them rather than a detached panel — see `references/chat-composer-voice-inline-controls.md`.
For mobile composer keyboard parity, especially the contract that mobile `Enter` inserts a newline while desktop `Enter` sends, see `references/mobile-composer-enter-key.md`.
For configurable STT modes — browser-only, browser live preview with backend final transcription, backend-only — and the local faster-whisper OpenAI-compatible service pattern, see `references/voice-stt-provider-modes-and-local-whisper.md`.
  For configurable STT modes — browser-only, browser live preview with backend final transcription, backend-only — and the local faster-whisper OpenAI-compatible service pattern, see `references/voice-stt-provider-modes-and-local-whisper.md`.
  For local/OpenAI-compatible STT `Connect & fetch models` failures, misleading TTS safety errors, and the required API + browser verification loop, see `references/voice-stt-local-provider-probe-debugging.md`.

  For the live-meter + confirm/cancel voice flow variant, including the AudioContext resume pitfall and transcript/status separation, see `references/voice-composer-live-meter-and-confirm.md`.
For voice input/STT provider architecture — Browser STT vs server-backed OpenAI-compatible transcription, custom model requirements, config points, and localhost/private-network URL pitfalls — see `references/voice-stt-provider-architecture.md`.
For the wavesurfer.js Record-plugin fallback when the custom waveform is flaky or the requirement is a real live mic waveform, see `references/voice-composer-wavesurfer-record.md`.
For inline composer waveform micro-flicker/root-cause diagnosis, including wavesurfer `renderMicStream()` tight-loop redraw and silent-threshold chatter, see `references/voice-inline-waveform-stability.md`.
  - Practical pitfall: keep the **transcript** in a full-width block **below the textarea and above the toolbar** when the user expects it to be appended at the bottom of the composer; do not move it above the text area unless that explicitly improves legibility.
  - Practical pitfall: the waveform/meter must reflect the **live microphone amplitude** (via analyser/level sampling) or use a proven mic waveform widget like wavesurfer Record; do not leave a decorative animation that only looks active. If the third-party widget can appear blank before it is ready, keep a visible fallback waveform until the plugin has mounted and bound the live stream.
  - Practical pitfall: for small inline composer meters, do not assume a third-party waveform widget is more stable than a custom analyser-driven renderer. If micro-flicker looks like the waveform briefly goes flat, separate stream/meter health from renderer redraw behavior; wavesurfer Record can repeatedly call async `load()` on a tight interval.
  - Practical pitfall: when the transcript or meter layout changes, update the focused client contract tests to assert both the **render order** and the **state-driven meter level**; otherwise a visually plausible but wrong layout can regress without failing tests.
For the contract that tool-trace visibility must not hide the live thinking GIF / streaming indicator, see `references/tool-trace-thinking-indicator-contract.md`.
For chat transcript UI taxonomy work, use repo ADR `docs/adr/ADR-013 — Unified Chat Transcript UI Taxonomy.md`: classify surfaces by semantic visual family (`MessageBubble`, `TranscriptEventRow`, `ActionRequestBar`, `LiveRunPanel`, `QueuePanel`, `AttachmentCard`) rather than raw message role; keep normal chat and group chat on shared event/action primitives instead of parallel tool/approval/thinking layouts.
For reusing the composer-style compact outlined/filled action-button language across nav/sidebar controls while preserving real anchor behavior for route links, use `references/nav-action-button-style.md`.

For activity rail header/collapse-button independence, scroll containment, and preventing nav items from visually passing through separators/header regions, use `references/activity-rail-scroll-containment.md`.
  - Practical pitfall: for chat composer placeholder/copy changes, update the source locale key that the component actually reads (`chat.inputPlaceholder`) across all locale files, and update any Playwright helpers that locate the input by placeholder text. When verifying served source, check the exact key/value context, not a broad old-string absence, because similarly named placeholders in other surfaces such as group chat may intentionally remain.
  - Implementation pitfall: when fully implementing the workspace ADR, remove the old launcher-card / overlay-drawer contracts rather than styling over them. Update stale tests that still expect `session-list-launchers`, `session-launch-button`, or `showDrawer = true`; they should instead protect pane toolbars, inspector toggles, and absence of body-level drawer overlays. Verify live-dev served source contains the new selectors and no old overlay selectors.
  - Practical pitfall: when Maxim asks to make one section background “the same as” another, do not assume the lighter token is desired. Identify which semantic token is actually darker/lighter (`surface-sidebar` vs `surface-panel`) and align in the requested direction. For chat/sidebar alignment, include every visible reading surface in the contract: app sidebar, session list, chat main wrappers, and `VirtualMessageList`; otherwise the message area can stay visually lighter than the surrounding panels.
  - Practical pitfall: when Maxim asks for a “dark gray” Web UI surface, do not introduce blue, green, or other tinted grays. Use true neutral grayscale hex values where RGB channels are equal (for example `#181818`, not `#181c20`), and add/keep a source contract that parses dark surface tokens and asserts `R === G === B` for `surface-root`, `surface-sidebar`, `surface-panel`, `surface-raised`, and `surface-hover`.
  - Practical pitfall: selected/active panes, selected sessions, nav items, badges, hover/active backgrounds, and generic accent tokens are not status markers. Do not give them blue/cool/color tints. If the color is not a semantic status marker (`--status-*`, success/warning/error/unread/running/queued), keep it neutral grayscale where `R === G === B`; active state should usually use `--state-active-bg` plus normal text color, not accent-colored text. Add/keep a source contract for non-status `--accent-*`, `--state-active-bg`, `--state-focus-ring`, `--text-secondary`, and `--text-muted` so later UI polish cannot reintroduce colored selection tint.
  - Practical pitfall: treat neutral surfaces/selection colors and semantic status colors as separate palettes. If Maxim says status colors are too muted, brighten only `--status-*` / success-warning-error tokens and keep the neutral surface and non-status selection grayscale contracts intact. Add/keep a source contract for the chosen vivid status hex values so a later neutral-surface cleanup does not accidentally desaturate the status indicators again.
  - Practical pitfall: keep the activity rail quiet and utility-first. Do not reserve a top logo/brand section unless Maxim explicitly asks for branding; prefer nav immediately at the top, with thin `nav-panel-separator` dividers between nav groups. Profile/model switching belongs with the small footer controls (logout/status/theme/version area) in compact form, not as primary nav entries, and the `Profiles`/`Models` routes should not appear as rail items when they are just selectors/settings surfaces.
  - Practical pitfall: keep activity-rail sections visually flush. Avoid outer horizontal padding on `.sidebar` / `.activity-rail` that makes panels, separators, footer rows, or controls look artificially inset; put spacing inside clickable rows instead, and make dividers span the rail width unless Maxim explicitly asks for inset cards.
  - Practical pitfall: compact composer binary controls such as autoplay speech and tool-call visibility should be symmetric toggle buttons, not a mixed switch/ghost-button pair. Default state should be empty/outlined/gray; active state should be filled with `text-primary`/white foreground semantics and expose `aria-pressed`.
  - Practical pitfall: for chat composer voice workflows, keep the voice state inline in the composer flow: attach stays left, mic/send stay right, and recording/transcribing appears as a strip between them. Do not keep a detached floating panel if the merged UI feels visually foreign; move the state into the composer instead. Let the composer container own start/stop, and let the voice strip render the current state plus cancel/preview only. Protect this with a source contract that checks the action order and the absence of the old panel wrapper.
  - Practical pitfall: for chat composer utility/action buttons, visual centering of SVGs matters more than preserving Naive UI's default icon-slot structure. If Maxim complains about icon alignment or wrapper noise, render the SVG directly in button content, center `.n-button__content` with flex, and use a fixed-size SVG class. For send, prefer a laconic upward arrow over a paper-plane glyph when simplifying the composer.
  - Practical pitfall: for the chat composer input shell, keep the one-line state visually centered while pinning edge actions at the bottom when textarea grows. Put the attach action inside `.input-wrapper` as the left peer of the textarea, style it with the same `composer-action-button` language as Send, and set attach / `.input-actions` to `align-self: flex-end` while leaving `.input-wrapper { align-items: center; }` for the one-line optical baseline.
  - Practical pitfall: when the session row running status uses the blue dot, make the dot pulse to communicate live activity, but keep queued/waiting/unread/complete/read states non-pulsing unless explicitly requested. Protect this with a source contract for `.session-item-status-dot[data-tone="running"]` using `session-status-dot-pulse` and a negative contract that queued does not inherit the pulse.
  - Practical pitfall: chat session status attention must not tint or background-highlight the whole row unless Maxim explicitly asks for it. Keep runtime/unread/error/status emphasis in accent-only affordances such as the left rail, status dot, text weight, or vivid semantic status color; add/keep a source contract that `.session-item[data-attention-tone]` does not set a `background` while `.session-item[data-attention-tone]::before` and `.session-item-status-dot[data-tone=...]` remain present.
  - Practical pitfall: do not add a redundant bottom workspace status bar to the chat pane by default. If runtime/profile/model state is already visible in the rail/footer, chat header, Stop affordance, session row state, or Run inspector, remove/avoid `workspace-statusbar` and its dot; otherwise it becomes noisy duplicate chrome. Protect this with a source contract when removing it.

### Chat header action controls

When moving a chat affordance from a floating overlay into the chat header, treat it as a full surface migration, not just a visual restyle: add the control as a regular `NButton` inside `.header-actions`, preserve the click behavior and tooltip/accessibility label, add any new user-facing string to every locale file, remove the old floating wrapper DOM, remove orphan CSS/keyframes/mobile overrides, and add a raw-component contract that the new header action exists while the old wrapper classes are absent. Then run the focused client contract test and build, commit/push `dev`, restart live-dev, and verify `/health` plus the served Vite source/bundle contains the new selector and no old wrapper selector.

For chat-header micro-controls that Maxim wants to match the composer/send-button style, use `references/action-button-link-controls.md`: apply the shared `action-buttons.scss` mixins, use compact square outlined/filled controls, render SVGs directly rather than through Naive UI `#icon` slots, and project panel-open state into an active class.

### Mobile chat parity pitfalls

When aligning mobile chat behavior with desktop, treat mobile as its own interaction contract rather than shrinking the desktop UI:

- Mobile textarea `Enter` / return key should insert a newline; do not submit from plain `Enter` on mobile. Keep desktop `Enter` submit and `Shift+Enter` newline behavior intact. Use the existing `isMobileViewport()` helper and cover both normal `ChatInput` and `GroupChatInput` with focused tests.
- Chat-header controls that are desktop-specific (for example Outline, Copy Session ID, Files/Inspector buttons in `.chat-header-toolbar`) should not merely be visually squeezed on mobile. Prefer a Vue render guard such as `v-if="!isMobile"` on the desktop toolbar so the controls are absent from the mobile DOM, while mobile-specific navigation/session controls remain in the header.
- When the desktop Outline button has been routed through the session context menu, preserve mobile parity by rendering a separate mobile-native top-right session-options button (outside the desktop-only toolbar). Do not leave mobile with no way to open active session options just because `.chat-header-toolbar` is hidden.
- Do **not** make that mobile button open the same desktop cascading `NDropdown` when the menu contains nested `children` groups such as Tags, Export, or Copy. Root dropdown placement does not control nested submenu placement, and mobile side-opening submenus produce confusing/right-vs-left chevron regressions. Prefer a dedicated mobile action surface: a right-side session options drawer with drill-down views, or a bottom/action sheet. Style the drawer rows like the app's sidebar/activity-rail nav rows, not as a stack of rounded boxed buttons. See `references/mobile-session-options-surface.md`.
- Protect this with source/component contracts: first prove the old behavior fails, then assert the mobile guard exists, the unguarded toolbar form is absent, the mobile options button exists, the desktop `NDropdown` is gated behind `!isMobile`, and the mobile options surface does not rely on desktop cascade submenu hacks (`sessionSubmenuLabel`, custom left-chevrons, or `session-context-menu-submenu-left`).
- If a temporary dropdown/chevron fix is unavoidable before the drawer ships, verify the real rendered DOM or screenshot, not only source text: Naive UI teleports dropdown internals and `DropdownOption.props.class` can land on `.n-dropdown-option-body` rather than an outer container.

## Standard planned-work workflow

1. Start from the right base.
   - Inspect `git status --short --branch` and remotes before editing.
   - When Maxim asks whether everything is committed before dev work, check both the live-dev worktree and the canonical production checkout: `/home/werserk/2-kira/hermes-web-ui-dev` should be clean for `dev` work, while `/home/werserk/2-kira/hermes-web-ui` may still carry local `main` changes that need stashing or explicit handling.
   - When Maxim explicitly asks to merge `origin/dev` into `origin/main` and push, treat it as an execution request, not a PR-planning task: verify both worktrees are clean, fetch `origin main dev`, perform the merge from the canonical production checkout on `main`, prefer a fast-forward when possible, push `main`, then re-fetch/verify `main == origin/main` and report the resulting commit. Do not claim production deployment from this merge alone; deployment needs its own health/workflow evidence.
   - When Maxim explicitly asks to make `dev` a clean copy of current `main` after a bad integration, treat it as a remote ref reset with preservation: fetch `origin main dev`, record the commits and version delta, create and push a backup branch such as `backup/dev-before-main-reset-<timestamp>` at the old `origin/dev`, then update `dev` to `origin/main` with `--force-with-lease=refs/heads/dev:<old-dev-sha>`. Afterward re-fetch and verify `origin/dev == origin/main`; if live-dev uses the `dev` worktree, reset that worktree to `origin/dev`, restart `hermes-web-ui-dev.service`, and verify local/public `/health` reports the copied commit. This is allowed only after explicit user direction because it rewrites `dev` history.
   - If stashing the canonical checkout, verify after `git stash push --include-untracked`: nested `.paperclip/` worktrees may remain untracked/ignored by stash and should be reported rather than deleted.
   - For ongoing Hermes Web UI implementation work, use the live-dev worktree (`/home/werserk/2-kira/hermes-web-ui-dev`) and keep future edits there once the task is meant to continue in `dev`.
   - For review-first work, branch from `origin/dev` and open PRs with base `dev`.
   - Branch from `origin/main` only for production-ready hotfixes or when Maxim explicitly chooses `main`.
   - If `dev` is already checked out in another worktree, operate in that worktree instead of trying to `git switch dev` from the canonical checkout.
2. Choose the right runtime.
   - Use live-dev for fast browser-visible implementation work.
   - Use branch-preview only when you explicitly need to pin the dev host to a pushed branch.
   - Do not treat a local build as a deploy.
   - When Maxim asks to work directly on `dev`, committed changes should update `https://hermes.dev.ops.kiraproject.ru/` automatically unless he explicitly says not to deploy; follow `references/dev-auto-update-working-site.md`.
   - Do not treat a local build as a deploy.
3. Implement narrowly.
   - Preserve existing behavior unless the task asks to change it.
   - Do not mix unrelated refactors into bugfix/update work.
   - Add user-facing strings to all locale files.
   - In the live-dev worktree, expect parallel agent/user changes. Before committing, re-check `git status --short --branch`, `git log -1`, and the exact intended diff. Stage only the files/hunks that belong to the requested change. If the requested change is already present in `HEAD`/`origin/dev`, do not manufacture a duplicate or empty commit; report the existing commit and continue with runtime verification.
4. Validate before promotion.
   - Run the smallest relevant checks while iterating.
   - For broad changes, use the project harness: `npm run harness:check`, `npm run test:coverage`, `npm run test:e2e`, and `npm run build`.
   - For research/CodeGraph/test-implementation plans, use `references/testing-research-codegraph-tdd-plan-execution.md`: repo docs first, CodeGraph deep-dive per contract, RED/GREEN for the first P0 test, CodeGraph affected-test discovery, and direct existence checks for ignored `.hermes/*` artifacts.
   - For executing a full testing-development loop or preparing an upstream promotion gate, use `references/upstream-sync-certification-loop.md`: certify session prefs, chat row-state, runtime/coding-agent launch, static assets/settings, full E2E, coverage, build, CodeGraph sync, and live-dev health before future upstream merges.
   - If a server chat/session-chain file changes — including `packages/server/src/controllers/hermes/sessions.ts` — run `npm run harness:check` and add a `docs/chat-chain-changes/*.md` fragment when the harness requires it.
   - For Vitest source-text contract tests, choose the read strategy by transform environment: prefer Vite `?raw` imports for Vue SFC text when supported, but use Node-capable filesystem reads for style/source contracts when raw-importing SCSS or mixed Vite assets fails. Avoid browser-like transforms that externalize `fs` and fail as `readFileSync is not a function`.
   - Vitest is not Jest: do not use Jest-only flags such as `--runInBand` with `npm run test -- ...`; use the repo's normal `vitest run` invocation unless a Vitest-supported flag is needed.
   - For deploys, verify the active service target, port, health endpoint, and served bundle through `hermes-web-ui-service-ops`.
5. Promote only with approval.
   - Merge micro-feature PRs into `origin/dev` for integration/review.
   - Promote `origin/dev` to `origin/main` only after approval when production is affected.
   - Deploy production only from `origin/main`.
6. Export upstream only when requested.
   - Keep local-only Kira changes separate from upstream-exportable changes.
   - Recreate/cherry-pick into `hermes-web-ui-legacy` before opening an upstream draft PR.

## Production deploy reality check

A merged PR on `main` is **not** proof of deployment. For Hermes Web UI production, the real sequence is:

1. PR merges into `origin/main`.
2. `Build` runs on the pushed `main` commit.
3. Only if `Build` succeeds does `Deploy Hermes Prod` become a real deploy candidate via `workflow_run`.
4. `Deploy Hermes Prod` can appear with `conclusion: skipped` when the upstream build fails or the workflow is a non-deploying `workflow_run` artifact.
5. Treat the deployment as successful only after confirming both:
   - a non-skipped `Deploy Hermes Prod` run for the target commit, and
   - `/health` on `hermes.ops.kiraproject.ru` reports the expected `git_commit` / `origin/main` state.

Never answer “deployed” from merge status alone. Check the workflow conclusion and the prod `/health` commit.

## Guardrails

- Do not force-push unless Maxim explicitly asks for history rewrite.
- Do not assume the live service runs the checkout you are viewing; verify systemd `ExecStart`/`WorkingDirectory`.
- When a dev preview branch is separate from the PR branch, apply fixes to both branches and run the relevant tests/build on both before reporting done. A green preview can still leave the PR branch incomplete if their bases diverged.
- Do not run `hermes-web-ui update` for Kira production unless the active unit proves production runs from the global npm package.
- If a task is execution, act; do not stop at a plan.
- For standing/product goals, distinguish subgoal artifacts from actual goal completion. Creating documents, roadmaps, research notes, meta-plans, smoke checks, or a single patch is partial progress unless the requested working product contour is implemented and verified. Do **not** write “goal reached”, “goal complete”, “цель достигнута”, or “цель выполнена” for a substep. Report “implemented/created/verified this step; goal remains incomplete” and name the next execution gate.
- When Maxim corrects completion language, treat it as a workflow-skill signal, not only a memory preference: patch the governing class-level skill so future sessions do not overclaim plan/document/subgoal completion.
- For Kira beta/user-contour work where `app.kiraproject.ru` must not be broken, prefer temp-root `kira-ops` smoke checks before live `/data/kira/users` changes; see `references/kira-beta-user-contour-smoke.md`.
- For Kira beta-10 VM acceptance, use `references/kira-beta-10-vm-acceptance.md`: home PC / `werserk-tachka` is dev/operator/fallback only; real beta tenant contours currently belong on Yandex Cloud VM `kira-main-ops-01`; acceptance needs VM identity, dummy tenant, negative-read checks, runtime tool-policy denial, backup/restore, first real user E2E, and healthy PC fallback.
- For Hermes Web UI beta hardening of ordinary users vs server/admin operations, use `references/beta-admin-route-hardening.md`: work in live-dev, gate profile/runtime lifecycle routes with `requireSuperAdmin`, add route-middleware source-contract tests, build, and verify prod health without calling the whole product goal complete.

## References

- `references/beta-10-vm-acceptance.md` — VM-first beta-10 acceptance execution pattern: target selection, evidence gates, tenant contour provisioning, loopback Web UI runtimes, and reporting pitfalls.

- `references/dev-integration-branch-flow.md` — `origin/dev` staging branch model.
- `references/dev-pr-branch-deploy.md` — branch-preview deploy workflow.
- `references/update-version-runbook.md` — exact version-update flow for Kira production.
- `references/upstream-main-delta-review.md` — read this when Maxim asks what is new on `upstream/main` versus Kira `origin/main`; fetch both refs, summarize features/fixes, and identify divergent-merge risk without editing or deploying.
- `references/upstream-main-merge-validation-pitfalls.md` — broad upstream-main merge push gate and known reconcile pitfalls: red `test:coverage` blocks push/live-dev, abort-state narrowing, `vi.hoisted` mocks, source-contract read strategies, and socket/store mock drift.
- `references/feature-branch-commit-push-deploy.md` — compact feature branch/build/preview workflow.
- `references/main-merge-auto-deploy.md` — main merge auto-deploy policy and gates.
- `references/local-checkout-deploy-drift.md` — live host serving an unexpected checkout/branch.
- `references/multi-window-sync-and-adr-routing.md` — ADR canon and cross-window sync patterns.
- `references/session-title-generation.md` — title generation/provider alias pitfalls.
- `references/session-title-settings-ui.md` — compact Session settings UI pattern for title naming modes.
- `references/session-pins-server-authoritative.md` — source-of-truth contract and pitfalls for durable cross-device session pins.
- `references/account-scoped-ui-preferences.md` — server-authoritative user-scoped UI preferences such as Activity Rail visibility: per-user storage, cross-device sync, fallback local cache, routes, schemas, and TDD contracts.
- `references/session-read-status-receipts.md` — read/unread status semantics: visible focused latest-message receipt, server-authoritative state, and multi-tab/device invalidation.
- `references/paperclip-entrypoint-readiness.md` — cross-repo Paperclip/Hermes UI entrypoint pattern: BFF endpoint, client route, dry-run guardrails, tests, and readiness evidence.
- `references/session-row-layout-status.md` — historical chat session-list row layout with status-dot context; check current ADRs before reintroducing dots.
- `references/session-row-status-layer-removal.md` — ADR-driven removal/redesign guardrail for fork session-list status-dot code versus Ekko/live-state logic.
- `references/session-row-status-adr-006.md` — single server-authoritative session-row status dot semantics: preview-row placement, priority mapping, quiet read state, and tests.
- `references/voice-surface-ia-refresh.md` — voice-panel IA pattern: split Speak vs Voices, minimize the header, group lifecycle actions, and keep picker/catalog state synchronized.
- `references/chat-composer-voice-inline-controls.md` — chat composer voice layout: attach left, inline recording strip, mic/send right.
