# Chat composer voice controls: inline layout

Use this pattern when updating the chat composer voice UI.

## Contract

- Keep **attach** on the left.
- Keep **send** and **mic/voice toggle** on the right.
- Render recording/transcribing as an **inline strip between** the left attachment action and the right action cluster.
- Do **not** introduce a separate floating or detached recording panel unless Maxim explicitly asks for a modal/drawer experience.

## Implementation notes

- Let the composer container own the start/stop voice state.
- Let the inline voice component render only the current state, preview, and cancel affordance.
- Prefer a compact single-row layout that collapses cleanly on narrow screens.
- If the old voice surface feels visually foreign after a merge, treat it as a layout migration: move the state into the composer flow instead of restyling the old panel.
- If the full transcript must remain readable, place it in a full-width block **directly below the textarea and above the toolbar**. Keep the inline strip for waveform/status/timer/cancel only; do not squeeze transcript text into the narrow action row.
- For waveform visualization, drive bar heights from the live microphone amplitude instead of a looped fake animation. Use the inline meter as a visualization of the current capture level, not as a purely decorative oscillator.
- For recording duration, keep the timer anchored to the actual capture start time (`startedAt`) so the displayed duration resets cleanly when the state returns to idle.

## Verification

- Check the composer in idle, recording, transcribing, and error states.
- Verify the action order still reads left-to-right as: attach → inline voice state → mic/send.
- Confirm the narrow/mobile layout does not wrap the controls into a disconnected second toolbar.