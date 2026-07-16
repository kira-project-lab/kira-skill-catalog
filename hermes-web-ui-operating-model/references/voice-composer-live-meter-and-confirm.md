# Voice composer live meter + confirm flow

Use this reference when the chat composer voice UI needs to match the current Hermes visual language.

## Contract

- The waveform must reflect **live microphone amplitude**, not a decorative animation.
- Sample levels from the recording stream with a WebAudio analyser or equivalent live meter.
- If the audio context can start suspended, resume/activate it **before** or alongside `getUserMedia`, otherwise the meter can stay flat while transcription still works.
- Surface the live `level` in recorder state and pass it into the voice strip.
- Keep the waveform/status strip visually aligned with the other composer actions so it reads as part of the same control row.
- Keep transcript content in a separate readable block; do not let waveform bars and transcript text compete in the same visual container.

## UX labels

- Prefer `Recording` over `Capturing`.
- Prefer `Transcription` as the status label when the transcript is being produced.
- Render the status as a chip/label distinct from transcript text.
- Replace `stop` with `confirm` when the user is finishing a recording they want to keep.
- Put `cancel` immediately to the left of `confirm`.

## Verification

- Add or update focused client tests for:
  - live waveform reacting to level changes,
  - Browser STT starting a separate mic meter/stream source when `SpeechRecognition` is used,
  - mic meter cleanup on browser-STT stop/cancel,
  - confirm/cancel behavior,
  - transcript/status separation,
  - locale strings for the new labels.
- If the waveform looks alive but transcript is the only thing changing, verify the meter is bound to the live stream rather than to recording state alone.
- If two waveform visuals appear at once, check that the fallback is removed after the primary renderer is ready rather than left underneath with lower opacity.
- For Browser STT / native `SpeechRecognition`, do not assume transcription implies a `MediaStream` exists. Browser recognition can transcribe without `useMicRecorder`, so the waveform can stay flat unless the composer also starts a mic-meter stream. Add a regression test that selecting the browser provider still calls `micRecorder.start()` for live `stream`/`level`, and that stop/cancel calls `micRecorder.cancel()` to release the meter.
- When STT provider can be `browser`, test it separately from backend STT (`openai`/`custom`). Browser `SpeechRecognition` can produce transcript text without going through `useMicRecorder`, so `stream` may be `null` and `level` may remain `0`; in that case the waveform/meter is a product bug, not a microphone or STT configuration issue. The fix should either start a live mic meter/recorder alongside browser recognition or clearly render a non-live fallback.
