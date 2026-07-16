# Voice inline waveform stability

Use this when diagnosing or changing the chat composer voice waveform / mic meter.

## Durable finding

For the small inline composer waveform, a full waveform library can introduce visible micro-flicker even when microphone capture is healthy.

In the current wavesurfer.js Record plugin implementation, `renderMicStream(stream)` samples on a very tight interval and repeatedly calls `wavesurfer.load('', [dataWindow], ...)` to redraw live mic data. Because `load()` is asynchronous and rebuilds waveform state, this can briefly clear or flatten the rendered waveform. In a compact 30px composer strip, that reads as a millisecond-scale "zero wave" flicker.

## Diagnostic shape

Before blaming mic permissions or stream wiring, check these layers separately:

1. Mic capture state: `useMicRecorder.state.stream` is non-null while `VoiceDialogueControls` status is `capturing`.
2. Meter state: `useMicRecorder.state.level` updates from the Web Audio analyser.
3. Waveform renderer: look for redraw paths that call third-party `load()`/canvas rebuilds on tight intervals.
4. Silent-state UI: thresholds around low amplitude can toggle classes/colors rapidly.

## Pitfalls

- A passing mic meter does not prove the waveform renderer is stable.
- A focused Vue test that only asserts `renderMicStream(stream)` was called will not catch visual redraw flicker.
- Single-threshold silence detection such as `level > 0.006` can chatter near the threshold. Use hysteresis or avoid changing DOM/classes on every low-amplitude sample.
- If a prior quiet-state stabilization was reverted, do not simply reapply it as the whole fix; distinguish silent-overlay flicker from renderer redraw flicker.

## Preferred implementation direction

For the inline composer meter, prefer a lightweight custom renderer driven by existing analyser output (`micRecorder.state.level`) plus a ring buffer and `requestAnimationFrame`/CSS transforms. Reserve wavesurfer Record for larger/full waveform surfaces where its redraw model is acceptable.

## Verification

Add focused source/component coverage for:

- stable DOM node presence for quiet/noise overlays if used;
- hysteresis or equivalent no-chatter behavior around silence thresholds;
- renderer contract does not repeatedly recreate or remount the waveform shell on level updates.

Manual/browser verification should look for millisecond flattening while speaking continuously, not just for "waveform appears".