# Voice STT provider runtime notes

Use when Maxim asks how Hermes Web UI voice recording/transcription is wired, or whether a local provider such as Ollama/faster-whisper can be used.

## Web UI STT flow

- Chat voice input has two capture paths:
  - `browser`: uses `SpeechRecognition` / `webkitSpeechRecognition` in the browser. `MediaRecorder` may still run for the live mic meter, but audio is not sent to backend for STT.
  - `backend`: records with `MediaRecorder`, uploads audio as `multipart/form-data` to `POST /api/hermes/stt/transcribe`, then the server calls the configured OpenAI-compatible STT provider.
- Server-side STT adapters currently support stored providers `openai` and `custom`; `custom` reuses the OpenAI-compatible `/audio/transcriptions` adapter.
- Relevant code paths:
  - `packages/client/src/components/hermes/chat/ChatInput.vue` — chooses browser vs backend capture and commits transcript.
  - `packages/client/src/composables/useBrowserSpeechRecognition.ts` — browser STT wrapper.
  - `packages/client/src/composables/useMicRecorder.ts` — MediaRecorder capture.
  - `packages/client/src/api/hermes/stt.ts` — transcription upload.
  - `packages/server/src/routes/hermes/stt.ts` and `packages/server/src/controllers/hermes/stt.ts` — backend API.
  - `packages/server/src/services/hermes/stt-providers/openai.ts` — OpenAI-compatible transcription call.

## Provider defaults and UI mismatch to verify

- Server fallback in `openai.ts` may default to `gpt-4o-transcribe`.
- UI presets may still label OpenAI STT as `OpenAI Whisper` and default to `whisper-1`.
- When answering “which model is used,” inspect both the saved provider settings and the server fallback; do not infer from the preset label alone.

## Local provider pitfalls

- Hermes Agent STT and Hermes Web UI STT are separate surfaces.
  - Hermes Agent can use local `faster-whisper` on demand via `stt.provider: local` in profile config.
  - Hermes Web UI Custom STT expects an HTTP endpoint compatible with OpenAI `/audio/transcriptions`; an installed Python package or cached model is not enough.
- Ollama may expose OpenAI-compatible model endpoints and, on newer versions, an audio transcription route, but this does not mean it has a usable STT model installed. Verify installed models and a real `/v1/audio/transcriptions` smoke test before recommending it.
- Web UI URL safety for custom STT currently reuses TTS URL safety and can reject `localhost`, `127.0.0.1`, and private-network base URLs. For local STT, either use a trusted HTTPS/reverse-proxy endpoint or intentionally change the Web UI safety policy with tests.

## Useful live checks

```bash
# Is a local STT server actually running?
ps -eo pid,ppid,etime,stat,cmd | grep -Ei 'faster[-_ ]?whisper|whisper|stt|transcrib|speech-to-text|uvicorn' | grep -v grep || true
systemctl --user list-units --type=service --all --no-pager | grep -Ei 'faster|whisper|stt|transcrib|speech' || true
ss -ltnp | grep -E ':11434|:8000|:8001|:8080|:5000|:5001|:7860|:9000' || true

# Does Hermes Agent have local faster-whisper installed/configured?
/home/werserk/.hermes/hermes-agent/.venv/bin/python - <<'PY'
import importlib.util
for m in ['faster_whisper', 'ctranslate2']:
    print(m, bool(importlib.util.find_spec(m)))
PY
sed -n '/^stt:/,/^[^ ]/p' /home/werserk/.hermes/profiles/kira/config.yaml

# Does Ollama expose OpenAI-compatible endpoints and audio route?
curl -sS --max-time 3 http://127.0.0.1:11434/v1/models
curl -sS -i --max-time 3 -X POST http://127.0.0.1:11434/v1/audio/transcriptions
```
