# Session list launcher and preview pattern

Use this note for Hermes Web UI session list / history surfaces that need to be simplified.

## What changed in the session list UX

- The old inline header cluster (`Sessions` title, close button, batch controls, profile filter) was removed from the main session list surface.
- It was replaced with two prominent intent buttons at the top of the list:
  - **Search** — opens the existing session search modal.
  - **New Chat** — opens the existing new chat modal.
- This keeps the top of the session list action-oriented instead of status/control-heavy.

## Preview text contract for session rows

- The row preview should show the beginning of the most recent message as clean message text.
- Do not embed author prefixes such as `Me:` or `<profile>:` in the preview text.
- If the last message was sent by the user, render a compact `Me` author badge before the preview text.
- If the last message was sent by the model/LLM, render a compact Hermes profile-name badge before the preview text.
- Keep the title/time row separate from the author badge + preview row.
- Keep the badge visually small and bounded (`max-width`, ellipsis) so long profile names do not steal the preview line.
- For long profile-name badges, do not apply `overflow: hidden` / `text-overflow: ellipsis` directly to the padded badge container. Put the label in an inner span and apply ellipsis there, while the outer badge keeps `padding` and `box-sizing: border-box`; otherwise the right padding can visually disappear for names like `kira-for-sonya`.

## Pinned session visual contract

- Pinned sessions should stay at the top of session lists, but do not add a separate `Pinned` text header/count when each pinned row already has a pin icon.
- Apply this consistently across chat sidebar and History surfaces; they share the session-list mental model but may use different wrappers.
- For small UI regressions in this area, source-based Vitest assertions may be enough: check both `ChatPanel.vue?raw` and `HistoryView.vue?raw` so one surface does not silently keep stale pinned/header markup.

- Same-day times should stay 24-hour (`hour12: false`).

## Launcher contract

- Keep the two top launcher buttons in one row at equal width: **Search** and **New**.
- Use the short visible label `New` for the new-chat launcher, while preserving the full `New Chat` text in `title`/`aria-label` where useful.
- At narrow sidebar widths, labels may ellipsize first; at very narrow widths, switch launchers to icon-only instead of allowing cramped/wrapped text.
- Do not keep a duplicate `New Chat` button in the header when the launcher row already exposes creation.
- After creating a new chat/session, focus the composer automatically after the DOM update (`nextTick` + exposed input focus method) so the user can immediately type the first message.

## Implementation reminders

- Reuse the existing `SessionSearchModal` and new-chat flow instead of inventing new overlays.
- Keep profile filtering out of the header when it competes with the two primary actions.
- Prefer a compact, obvious top-level action area over a crowded inline toolbar for the session list.
- Keep the Search/New Chat launcher button content centered as a unit: center both the button itself and Naive UI's inner `.n-button__content`, not only the outer button.
- After creating a new chat from the launcher flow, return focus to the chat composer through an explicit `ChatInput` expose/ref API rather than parent DOM queries.
- For component-level focus behavior, expose a narrow public method from the composer component (for example `focusComposer()`) instead of reaching into private DOM structure from the parent.

## Preview sync pitfalls

- When the session list preview is derived from in-memory messages, watch the session-switch order carefully: `switchSession()` may clear/replace queued messages before persisted messages are loaded. If a preview refresh runs in that gap, it can erase the server-loaded preview until the session is clicked again.
- After `resumeSession()` or any persisted-message page load replaces `target.messages`, immediately recompute the session summary preview from the loaded messages. Add a regression test for the first click after page reload: preview visible from `fetchSessions()` must remain visible after switching into that session.
- Cross-tab/device updates should still use the existing row-state/session-sync paths. Row-state events with `reason: 'message'` or `reason: 'session_update'` should refresh authoritative summary fields from `fetchSession(...)` when row-state payloads do not include preview text.
