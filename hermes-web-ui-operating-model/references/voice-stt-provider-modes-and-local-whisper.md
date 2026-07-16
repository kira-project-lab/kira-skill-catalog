# Hermes Web UI voice STT provider modes and local Whisper

Use this when Maxim asks how chat voice input should work with Browser STT, OpenAI-compatible STT, or local Whisper/faster-whisper.

## Architecture verdict

Keep two layers separate:

1. **STT service layer** — exposes an OpenAI-compatible `POST /v1/audio/transcriptions` endpoint and turns audio into text. Local `faster-whisper` should be a separate small service, not embedded in Hermes Web UI.
2. **Hermes Web UI voice mode layer** — owns capture UX: browser live preview, backend final transcription, fallback behavior, and composer insertion.

Do not make the Whisper service responsible for browser live preview. Browser preview is a client-side `SpeechRecognition` feature.

## Useful modes

Define the user-facing setting as three modes:

```ts
type VoiceInputMode =
  | 'browser-only'
  | 'browser-preview-backend-final'
  | 'backend-only'
```

### `browser-only`

- Start `SpeechRecognition` / `webkitSpeechRecognition`.
- Show live partial/final transcript while speaking.
- Use `MediaRecorder` only for meter/waveform if needed.
- On stop, commit browser transcript to the composer.
- Do not call backend STT.

### `browser-preview-backend-final`

- Start browser recognition for live preview.
- Start `MediaRecorder` at the same time for final backend audio.
- While speaking, display browser text as tentative preview.
- On stop, stop browser recognition and recorder.
- Send audio to backend STT and treat backend text as authoritative final.
- If backend fails, keep browser preview as fallback and show a warning.

Pitfall: in this mixed mode, do **not** cancel `micRecorder` after stopping browser recognition; its audio blob is needed for backend final transcription.

### `backend-only`

- Start `MediaRecorder` only.
- Show recording/waveform but no live transcript.
- On stop, send audio to backend STT and insert returned text.

## Rollout default

For safe rollout, preserve existing behavior by default:

- active provider `browser` -> `browser-only`
- active provider `openai` or `custom` -> `backend-only`

Let users explicitly opt into `browser-preview-backend-final`. It has better UX but more moving parts.

## Local faster-whisper service shape

Recommended separate project/service:

```txt
kira-local-stt-service
  FastAPI wrapper
  faster-whisper backend
  systemd user service
  /health
  /v1/audio/transcriptions
```

Minimal OpenAI-compatible request:

```http
POST /v1/audio/transcriptions
Content-Type: multipart/form-data

file=<audio>
model=medium
language=ru
prompt=<optional>
```

Minimum response:

```json
{ "text": "распознанный текст" }
```

Recommended defaults for Maxim's local host:

```txt
model: medium
language: ru
device: cuda
compute_type: float16
vad_filter: true
```

Use `small` for lower latency; use `large-v3` only after measuring VRAM/latency.

## Web UI local endpoint policy

Hermes Web UI Custom STT currently uses URL-safety that may reject `localhost`, `127.0.0.1`, and private addresses. Do not globally weaken TTS URL safety. Add STT-specific trusted local allowlist instead, e.g. env/config:

```txt
HERMES_WEB_UI_STT_ALLOWED_LOCAL_BASE_URLS=http://127.0.0.1:8765,http://localhost:8765
```

Use the OpenAI-compatible base URL with `/v1` in the UI:

```txt
Base URL: http://127.0.0.1:8765/v1
Model: medium
API key: local
```

Practical pitfall: the local faster-whisper service may not require auth, but the Web UI Custom STT form/settings can still require a non-empty secret. Use a harmless placeholder such as `local`; do not add real secrets to docs or summaries.

When patching Web UI for trusted local STT endpoints, keep the safety layer STT-specific (for example `stt-providers/url-safety.ts`) and add focused tests in provider execution, settings persistence, and the shared provider-probe/model-discovery path. The probe route may live in TTS-named code (`controllers/hermes/tts.ts`) while serving both `kind: 'tts'` and `kind: 'stt'`; branch URL safety by `kind` so STT probes use the STT allowlist and TTS probes keep blocking localhost/private networks.

Provider-probe pitfall: the local faster-whisper service usually does not require authentication, but the Web UI form may still contain a placeholder API key. Do not blindly forward placeholder or non-ASCII values as an `Authorization` header for trusted local STT probes: Fetch headers are ByteString/LATIN-1 and values such as `дщсфд` (Russian-layout `local`) throw `Cannot convert argument to a ByteString`. For trusted local STT model discovery, omit an unsafe/non-ASCII auth header; for external providers, keep requiring an ASCII API token and surface a clear validation error. Add a regression test that sends a trusted local STT probe with a non-ASCII placeholder key and verifies `/v1/models` is called without `Authorization`.

Verify the live-dev runtime inherited the allowlist env after restart rather than assuming the shell env reached the service process.

## Planning docs created in session

When this topic recurs, prefer repo docs/runbooks/plans as canonical operational truth:

- `docs/runbooks/2026-06-10-local-faster-whisper-stt-service.md` — local faster-whisper OpenAI-compatible service runbook.
- `docs/plans/2026-06-10-configurable-voice-stt-modes.md` — Web UI implementation plan for configurable modes.

If those docs are missing or stale, recreate/update them in the repo rather than only explaining in chat.
