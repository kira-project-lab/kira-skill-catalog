# Voice composer waveform widgets

Use this when replacing the custom chat voice waveform with a ready-made mic visualizer.

## Recommended shortlist

### 1) `wavesurfer.js` + `Record` plugin
- License: BSD-3-Clause
- Why it fits: mature waveform renderer, official microphone Record plugin, can render a real live mic waveform rather than a decorative animation.
- Integration notes:
  - Use dynamic import / client-only mounting.
  - Register the Record plugin and pass the live `MediaStream` to `renderMicStream(stream)`.
  - Treat the plugin as the primary renderer but keep a visible fallback until the plugin has actually mounted.
  - Call `destroy()` and stop tracks on unmount / cancel.
- Source docs verified in this session:
  - `wavesurfer.js` docs include the Record plugin and describe v7 as Shadow DOM based.
  - `dist/plugins/record.d.ts` exposes `renderMicStream(stream)`, `startMic()`, `startRecording()`, `stopRecording()`, `pauseRecording()`, `resumeRecording()`, and `destroy()`.

### 2) `AudioMotionAnalyzer`
- License: AGPL-3.0-or-later
- Why it fits: very good live amplitude / spectrum meter if you want a compact inline visual instead of a full waveform engine.
- Caveat: the AGPL license is usually a poor fit for proprietary distribution unless the project is already compatible.

### 3) `vue-audio-visual`
- License: MIT
- Why it fits: Vue-oriented visual components and quick integration.
- Caveat: verify Vue 3 support and whether the live mic stream behavior is stable enough for the composer before committing to it.

## Pitfalls discovered

- A third-party waveform can render "blank" even when recording is active if you only rely on the plugin canvas and never show a fallback.
- If the fallback is removed too early, the widget can appear to disappear entirely while the plugin is initializing.
- Once the Record plugin is actually mounted and `renderMicStream(stream)` has been called, remove the fallback from the DOM (`v-if="!waveformReady"` or equivalent), not merely dim it; otherwise Maxim can see two waveform widgets overlaid.
- For an endless right-edge mic waveform, prefer the Record plugin's `scrollingWaveform: true` + `scrollingWaveformWindow` and keep `continuousWaveform: false`; `continuousWaveform` can visually jump/teleport when the captured data reaches the end of its window.
- If the scrolling waveform looks too jerky, increase `scrollingWaveformWindow` before changing renderers; a longer window (for example `10s` instead of `6s`) reduces visible step size because the plugin shifts a larger data window at the same sampling cadence.
- If the waveform is too insensitive, increase WaveSurfer renderer amplification via `barHeight` (for example `2.4`) rather than raising raw mic gain; this preserves the recorded audio while making quiet input visually legible.
- Set the WaveSurfer colors explicitly for the target visual language (`waveColor` / `progressColor`, e.g. `#ffffff` for active input). Do not rely on `currentColor` when parent text/status styles can make the live waveform black or muted.
- If the microphone is active but level is effectively zero, keep a small grey quiet/noise indicator so the widget does not look broken; switch to white as soon as live analyser level crosses a low threshold.
- Avoid threshold flicker in silent/noise states: use hysteresis, not a single cutoff. A practical pattern is separate `on` / `off` thresholds (for example `on >= 0.01`, `off <= 0.003`) so near-silence does not repeatedly flip color and overlay state.
- Keep quiet/noise overlay DOM stable. Prefer an always-mounted node with class/opacity transitions over `v-if` on every level transition; this avoids tiny DOM removal/reinsert flashes during recording.
- Be careful with `waveSurfer.setOptions()` for color changes: it can trigger a WaveSurfer re-render. Gate color changes behind hysteresis so a noisy level around the threshold does not create render churn.
- WaveSurfer Record's `renderMicStream()` internally updates on a tight interval and calls `wavesurfer.load(...)`, which clears/rebuilds canvas containers during render. If Maxim reports millisecond blank/zero frames, this is a plausible code-level cause. Quick mitigation: hysteresis + stable overlay + fewer `setOptions()` calls. Robust fix: replace the Record-plugin renderer with a custom `requestAnimationFrame` canvas/ring-buffer renderer using one analyser.
- The visible waveform should be driven by real mic input, not a decorative timer animation.
- Browser STT (`SpeechRecognition`) does not automatically provide the `MediaStream` needed by the WaveSurfer Record renderer. If Browser STT is selected, start a parallel mic recorder/analyser for the live meter/stream and cancel it on stop/cancel; keep transcript capture and waveform capture as separate responsibilities.
- Browser QA matters here: a green unit test/build does not prove the widget is visibly drawing in the live app.

## Practical recommendation

For Hermes chat composer voice UI, prefer `wavesurfer.js` + `Record` when you need a real waveform. Keep a lightweight inline fallback only until the plugin has mounted and started receiving the live stream, then remove the fallback entirely so the new waveform is the only visible widget.