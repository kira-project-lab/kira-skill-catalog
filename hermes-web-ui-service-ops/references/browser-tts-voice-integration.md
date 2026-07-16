# Browser TTS / Voice integration notes

This note captures a practical browser-side integration path for Hermes Web UI voice testing without modifying the Hermes repo.

## Browser-side settings

Hermes voice settings are stored in browser localStorage under:

- `hermes-tts-settings-v2`

Useful fields:

- `provider`: `openai` for OpenAI-compatible TTS endpoints
- `openaiBaseUrl`: base URL for the TTS backend, e.g. `https://voice.ops.kiraproject.ru/v1` or `http://127.0.0.1:8010/v1`
- `openaiVoice`: voice name, e.g. `kira-xiangling`
- `openaiModel`: model name, e.g. `qwen3-tts`

For Kira Voice through the existing Hermes UI, use the existing **OpenAI TTS** provider rather than adding a new provider or server-side route:

```json
{
  "provider": "openai",
  "openaiApiKey": "",
  "openaiBaseUrl": "https://voice.ops.kiraproject.ru/v1",
  "openaiModel": "qwen3-tts",
  "openaiVoice": "kira-xiangling"
}
```

## Verification pattern

1. Set the voice configuration in Hermes settings UI or localStorage.
2. Verify the backend endpoint directly from the browser context with a fetch to `/v1/audio/speech`.
3. Confirm the response is playable audio and that bytes are returned.
4. Only then trust the Hermes `VoiceSettings` test button.

## Common browser failure pattern

If Hermes shows `TypeError: Failed to fetch` in the voice test:

- inspect browser console and network first;
- verify the TTS backend answers `OPTIONS` preflight when the request is cross-origin;
- make sure the audio response includes CORS headers;
- rerun the direct browser fetch to isolate browser/network issues from endpoint issues.

## Notes

- Keep the Hermes repo unchanged when the existing OpenAI-compatible settings can express the desired backend. Configure the UI/localStorage first; do not invent server-side routing or a new provider unless the existing provider cannot represent the contract.
- If the task is only “connect this voice endpoint in Hermes Web UI”, do not rebuild or restart the Web UI service; insert/save the settings in the browser and verify the visible fields plus direct endpoint fetch.
- A working direct fetch is stronger evidence than a UI button state alone.
