# Voice STT provider architecture

Use this when explaining, debugging, or modifying Hermes Web UI voice input / transcription.

## Current flow

Chat voice input is turn-based, not realtime/full-duplex:

1. User starts capture from the chat composer mic control.
2. Web UI stops active output audio playback first.
3. Active STT provider chooses the transcription path.
4. Final transcript is inserted into the composer as editable draft text; sending remains explicit.

## Provider paths

### Browser STT

- Uses browser `SpeechRecognition` / `webkitSpeechRecognition`.
- Hermes Web UI does not choose or host the underlying model.
- `MediaRecorder` may still run in parallel for live meter/waveform, but the recorded audio is not the transcription source.
- Relevant files:
  - `packages/client/src/composables/useBrowserSpeechRecognition.ts`
  - `packages/client/src/components/hermes/chat/ChatInput.vue`

### Server-backed STT: OpenAI / Custom

- Browser records microphone audio with `MediaRecorder`.
- Client uploads one audio blob as `multipart/form-data` to `POST /api/hermes/stt/transcribe`.
- Backend reads stored provider settings/secrets, then calls an OpenAI-compatible transcription endpoint.
- Relevant files:
  - `packages/client/src/composables/useMicRecorder.ts`
  - `packages/client/src/api/hermes/stt.ts`
  - `packages/server/src/routes/hermes/stt.ts`
  - `packages/server/src/controllers/hermes/stt.ts`
  - `packages/server/src/services/hermes/stt-providers/openai.ts`

## OpenAI-compatible contract

The server-backed adapter posts to an `/audio/transcriptions` endpoint with:

- `file`
- `model`
- optional `language`
- optional `prompt`
- `Authorization: Bearer <apiKey>`

Expected response shape:

```json
{ "text": "transcript text" }
```

OpenAI provider uses the built-in OpenAI transcriptions URL. Custom provider normalizes `baseUrl` so a root/base path gets `/audio/transcriptions` appended, unless it already ends with `/audio/transcriptions`.

## Configurable pieces

User-facing configuration lives in Settings → Voice → STT providers:

- active provider: `browser`, `openai`, or `custom`
- custom/openai model
- custom base URL
- API key
- optional language/prompt fields in the legacy STT state path

A custom self-hosted STT model works without new app architecture if it exposes an OpenAI-compatible `/audio/transcriptions` HTTP API.

## Pitfalls

- Do not describe Browser STT as a Hermes model/provider; it is delegated to the browser/platform.
- There is a naming/default split: UI presets may label OpenAI STT as Whisper and default to `whisper-1`, while server/client fallback code may use `gpt-4o-transcribe`. Verify current source before stating the exact default.
- Custom STT currently reuses URL-safety logic from TTS and may reject localhost/private network URLs. For a local model, use a public HTTPS reverse proxy or intentionally change the safety policy with tests.
- Captured microphone audio is one-shot for server-backed STT. It is not a persistent background stream.
