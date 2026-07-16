# Local STT provider probe debugging

Use when `Settings → Voice → Add STT API → Custom STT → Connect & fetch models` fails for a local/OpenAI-compatible STT service.

## Root-cause pattern

Do not assume the transcription path and the model-discovery/probe path use the same safety/adapter code.

In Hermes Web UI the visible `Connect & fetch models` button uses the shared provider probe endpoint (`/api/voice/providers/probe`) in the TTS controller area, even for STT providers. A local STT URL can therefore fail with a misleading TTS-shaped message such as:

```txt
Provider probe TTS baseUrl cannot target localhost or private network addresses
```

That means the **probe path** is still using TTS URL safety, not that the STT service itself failed.

## Debug sequence

1. Read fresh live-dev logs before editing:
   - `journalctl --user -u hermes-web-ui-dev.service --since '20 minutes ago' --no-pager`
   - the Web UI server log for the active app home.
2. Verify the running live-dev commit via `/health`; do not trust the checkout alone.
3. Reproduce the probe path separately from transcription:
   - browser UI: Add STT API → Custom STT → Base URL → API key → Connect & fetch models;
   - API: authenticated `POST /api/voice/providers/probe` with `kind: "stt"`.
4. In source, trace `probeVoiceProvider(...)` to `probeProvider(...)`; verify it passes `kind: 'stt'` and that server-side normalization/safety branches on that kind.
5. Add/keep regression coverage for both sides:
   - trusted local STT probe is allowed and calls `/v1/models`;
   - local/private TTS probe remains blocked.

## Implementation contract

- STT provider save/transcribe and STT provider probe should both use STT-specific trusted-local safety.
- TTS provider probe must keep blocking localhost/private network targets.
- Do not weaken shared TTS/general SSRF protection to make local STT work.
- Keep the allowlist explicit, e.g. `HERMES_WEB_UI_STT_ALLOWED_LOCAL_BASE_URLS=http://127.0.0.1:8765,http://localhost:8765`.

## Browser QA contract

After tests and restart, verify the actual Web UI flow, not only the API:

1. Open `#/hermes/settings`.
2. Voice tab.
3. Add STT API.
4. Select Custom STT.
5. Base URL: `http://127.0.0.1:8765/v1`.
6. API key: any required placeholder if the local service does not require auth.
7. Click `Connect & fetch models`.
8. Success evidence is visible discovered models and/or model field auto-filled.

If the user reports the same error after a push, check for stale tabs, old runtime commits, and live-dev compile/restart failures before writing another fix.