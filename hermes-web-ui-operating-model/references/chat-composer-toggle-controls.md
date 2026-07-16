# Chat composer toggle controls

Use this reference when changing binary controls in the chat composer, especially controls like autoplay speech and tool trace visibility.

## UX contract

- Treat composer binary controls as peer buttons, not a mix of switch + ghost button.
- Attach/upload may be a stateless utility button; autoplay speech, tool trace visibility, and session-scoped YOLO/Allow all are stateful flag/toggle buttons.
- Adjacent composer utility buttons should share one visual button grammar even when only some are toggles: same size, border, radius, color, and icon centering.
- Do not put a visual divider between attach and the flag buttons unless Maxim explicitly asks for grouping; the row should read as one compact utility cluster.
- Inactive state: outlined/empty, gray/neutral text and border.
- Active state for toggles: filled button using the primary foreground/neutral white treatment in dark theme; icon/text should visibly switch from gray to white/filled.
- Expose toggle state with `aria-pressed` as a real boolean so tests and accessibility tooling read the state consistently. Stateless attach/upload should use `aria-label`, not `aria-pressed`.
- Keep the label/action semantics clear: the button may say the enabled capability (`Autoplay speech`, `Show tools`) while `aria-pressed` carries the on/off state.
- SVG centering is part of the contract. Center the actual rendered icon inside the button, not just the button box.
- When autoplay/tool toggles sit in the composer top bar alongside left-side status content, split the bar into explicit left and right blocks and keep the toggles in the right block. Prefer `justify-content: space-between` or a dedicated right cluster over relying on `margin-left: auto` inside a mixed-content row.
- Composer send/action buttons should use the same slight rounding as the utility toggles (`8px` in the current Web UI). Avoid reverting to fully circular `circle`/primary-shaped buttons unless Maxim explicitly asks for a round control.
- The composer input shell/textarea wrapper should share that same radius (`8px`) when Maxim asks controls and input to feel like one family. Avoid leaving `.input-wrapper` square (`border-radius: 0`) while nearby action buttons are rounded.

## Top-bar alignment contract

- Keep the left side of the top bar focused on session/model/context status.
- Keep autoplay/tool toggles visually grouped on the far right, with no accidental wrap to the left edge when the left block grows.
- Add/update a focused contract test that asserts the top bar has distinct left/right blocks, the toggle cluster is the second child, and the old `margin-left: auto` placement trick is absent.

## Implementation pattern

- Use matching `NButton` controls with shared class names for the group and item state, e.g. `.composer-toggle-group`, `.composer-control-button`, `.composer-toggle-button`, and `.composer-toggle-button--active`/`.active`.
- Put the SVG in the default button slot when Naive UI's `#icon` slot causes uneven visual centering; then explicitly center `:deep(.n-button__content)` with flexbox and give SVGs a common `.composer-control-icon` size.
- Keep source-of-truth state in the relevant chat/composer store or existing refs; the button classes are only UI projections of that state.
- For session-scoped YOLO/Allow all in Hermes Web UI, wire the composer toggle through `/yolo`: add the Web UI session command alias/handler, an `AgentBridgeClient` method, a `yolo_toggle` bridge action that calls Hermes Agent `tools.approval.enable_session_yolo/disable_session_yolo/is_session_yolo_enabled`, and store the returned `yolo_enabled` per session so `aria-pressed` reflects backend state.
- Avoid `NSwitch` when Maxim asks for the controls to look like buttons. Avoid mixing a switch for one setting and a ghost/tertiary button for another if they are visually adjacent peer toggles.
- Remove old grouping chrome such as `border-left` and compensating padding/margins when converting the controls into one peer cluster.
- Add/adjust a focused client contract test that asserts attach/autoplay/tool controls share the common control class, toggles have `aria-pressed`, active toggles receive the active class, and old divider/switch selectors are absent.
- When changing composer surface geometry, add a source contract for `.input-wrapper` as well as the buttons: assert the wrapper references the same radius value as the action buttons and that old square shell styling (`border-radius: 0`) is absent.

## Composer input edge-action alignment

When the composer textarea can autogrow or be manually resized:

- Keep the input shell as the alignment source. A good default is `.input-wrapper { display: flex; align-items: center; }` so the one-line state still looks vertically centered.
- Pin edge actions, not the whole row, for tall inputs: set the right-side `.input-actions` and the left attach button to `align-self: flex-end` so they remain in the bottom corners as the textarea grows.
- If Maxim asks the attach button to match send, move attach/upload into `.input-wrapper` as a `.composer-action-button` peer, not as a separate top-bar utility control. Keep the real hidden file input as the canonical file source.
- Share the send button styling selector with attach, e.g. `.composer-action-button--send, .composer-action-button--attach { ... }`, so border, radius, disabled/hover language, and icon centering stay consistent.
- Add a focused contract test that attach exists inside `.input-wrapper`, no longer exists under `.input-top-bar`, uses `composer-action-button--attach`, and that both attach and `.input-actions` are bottom-aligned while `.input-wrapper` remains centered for the one-line state.

## Composer textarea autogrow and resize bounds

When changing the chat composer textarea height behavior:

- Default to one row (`rows="1"`) with no inline height until content requires growth.
- Autogrow against textarea `scrollHeight`, but cap at a viewport-relative bound when Maxim asks for proportional height; `50vh` / `window.innerHeight * 0.5` is the established current contract.
- After the cap, keep textarea scrolling (`overflow-y: auto`) rather than growing the whole chat surface further.
- Treat the resize handle as resizing the composer section through the textarea height. Clamp manual drag, keyboard resize, persisted values, and `aria-valuemax` to the same max bound used by autogrow.
- Add tests for: one-row default, autogrow cap, scroll-after-cap, manual resize clamp, dynamic `aria-valuemax`, and persistence across remounts.

## Send/action button pattern

When simplifying the chat composer send action:

- Prefer a laconic upward-arrow icon over a paper-plane/send-airplane glyph when Maxim asks for a cleaner send affordance.
- Avoid `type="primary"` + `circle` if the complaint is visual heaviness or Naive UI wrapper noise; use a compact rounded-square button with explicit CSS for enabled/disabled state.
- Render the SVG directly in the button content instead of through the `#icon` slot when precise centering matters. The slot adds `.n-button__icon` / `.n-icon-slot` wrappers that can make the glyph look off-center.
- Center via shared button-content rules: `:deep(.n-button__content) { display:flex; align-items:center; justify-content:center; width:100%; height:100%; }` plus a fixed-size SVG class.
- Add a source contract that the upward-arrow paths exist, the old paper-plane polygon is absent, and `type="primary"`/`circle` are not used for the send button.

## Verification

- Run the focused composer/client test plus any adjacent shell/layout contract impacted by the UI change.
- Run `npm run build` and `git diff --check` before reporting done.
- For live-dev UI changes, restart/verify the dev service and confirm the served Vite source or built bundle contains the new selectors and no old switch-specific selectors such as `auto-play-speech-switch` / `NSwitch` remnants.
- For send-button icon changes, verify served `ChatInput.vue` contains the upward-arrow SVG paths and no old paper-plane polygon, and verify the served style module contains the new compact button rules.
