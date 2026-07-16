# Design Token Pass 1 pattern

Use when Maxim asks to make Hermes Web UI darker/stricter/more Notion- or Obsidian-like, reduce gray noise, remove glow/shadow decor, or standardize chat/session visual states.

## Durable outcome from the successful pass

Design Token Pass 1 worked best as a token contract, not a component-by-component repaint:

1. Add a small semantic layer in `packages/client/src/styles/variables.scss` first.
2. Keep compatibility aliases while migrating components, so the pass can land without forcing the whole app to change at once.
3. Convert broad chat/session surfaces to the semantic layer in one coherent visual pass.
4. Use tests to lock the contract before tuning individual components.

## Token groups to preserve

The first pass introduced this shape; future passes should extend it instead of creating new local gray palettes:

- surfaces: `--surface-root`, `--surface-sidebar`, `--surface-panel`, `--surface-raised`, `--surface-hover`
- lines: `--line-subtle`, `--line-default`, `--line-strong`
- interaction states: `--state-hover-bg`, `--state-active-bg`, `--state-focus-ring`
- statuses: `--status-running`, `--status-queued`, `--status-waiting`, `--status-error`, `--status-success`, `--status-unread`
- message/event primitives: `--msg-user-bg`, `--msg-assistant-bg`, `--msg-system-border`, `--event-bg`, `--event-border`, `--event-accent-line`
- radii: `--radius-none`, `--radius-xs`, `--radius-sm`, `--radius-md`, `--radius-lg`
- motion: `--motion-instant`, `--motion-fast`, `--motion-normal`

Also keep SCSS aliases for tokens that existing component styles consume (`$surface-*`, `$line-*`, `$state-*`, `$status-*`, `$event-*`, `$radius-*`, `$motion-*`, plus accent aliases such as `$accent-soft` and `$accent-line`).

## Regression test shape

Add or maintain a focused client contract test similar to `tests/client/design-token-pass.test.ts` that reads source files and asserts:

- semantic token groups exist in `variables.scss`;
- permanent panes do not rely on decorative shadows/glows;
- broad `transition: all` is not reintroduced in chat surface components;
- session/chat state visuals use semantic tokens instead of ad hoc hardcoded grays;
- status visual contracts preserve distinct `running` / `queued` / `waiting` / `error` / `unread` colors, circular dots, and rounded left rails;
- sidebar/session-list background contracts stay explicit when aligning the panel surfaces.

For these source-text contract tests, choose the import strategy by environment:

- Vite `?raw` imports are good for Vue SFC text when the Vitest transform supports them.
- Filesystem reads are acceptable for style/source contract tests when raw importing SCSS or mixed Vite-only assets fails. The key is keeping the test in a Node-capable Vitest environment and asserting source text, not DOM behavior.

## Component migration order

1. `variables.scss` token layer and SCSS aliases.
2. App shell/sidebar and model controls.
3. Session list and session rows/status indicators.
4. Chat panel, message list, message item/event blocks.
5. Composer/input and slash/context surfaces.
6. Outline/drawer/files/terminal panels.

## Visual guardrails

- Permanent structural panes should use thin lines, not box shadows.
- Keep the app navigation/sidebar pane and chat session-list pane on the same background token when Maxim asks for calmer sectioning; this avoids the “separate collage pieces” feel. Pitfall: do not infer the direction of alignment from “same as session list” or similar wording. Confirm the target surface semantics from the current token values / computed colors: in the corrected dark-navigation pass both panes consumed the darker `$surface-sidebar`, not the lighter `$surface-panel`, while straight borders preserved separation.
- Status indicators should stay semantic and restrained, but do not collapse them into monochrome. Maxim explicitly preferred restored color differentiation after the first pass: `running`, `queued`, `waiting`, `error`, and `unread/success` need distinct status colors.
- Preserve the familiar status geometry unless the request explicitly asks for sharp markers: session-row status dots should remain circular (`border-radius: 50%`), and the left colored attention rail should keep rounded exposed corners (`border-radius: 0 $radius-xs $radius-xs 0`). Avoid halos/pulse/glow unless the state requires urgent attention.
- Motion should feel immediate: prefer short explicit transitions over `transition: all`.
- Do not change runtime/status data semantics during a visual token pass. Keep behavior changes as a separate task.

## Verification path used successfully

- Run the focused token/session/sidebar tests first.
- Run `npm run build`.
- Run `git diff --check` and clean whitespace before commit.
- Commit and push to `origin/dev`.
- Restart/verify live-dev and check `/health` reports the new commit when Maxim expects the dev site updated.
