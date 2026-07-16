# Voice composer send-stop transcript contract

Use this reference when adjusting the chat composer voice-recording experience.

## Contract

- Keep the waveform as a **long, inline visual strip**.
- Do **not** put cancel/confirm buttons inside the same widget as the waveform.
- Prefer **minimal chrome** around the waveform; the strip should read as part of the composer, not as a detached panel.
- In recording mode, the primary send action should **stop the recording** instead of requiring a separate cancel button.
- Keep the transcript area clearly labeled as **`Transcript:`**.
- Preserve the composer layout logic: attach on the left, mic/send on the right, recording state in the middle.

## Implementation notes

- If the send button doubles as stop/confirm during recording, make that state explicit in the button label/appearance.
- Keep the waveform visual distinct from transcript text; do not collapse them into one control.
- Avoid introducing a new floating voice panel when an inline composer treatment is enough.

## Verification

Protect the contract with focused client tests that assert:

- the waveform strip renders without inline action buttons,
- send triggers stop/cancel behavior while recording,
- the transcript header reads `Transcript:`.
