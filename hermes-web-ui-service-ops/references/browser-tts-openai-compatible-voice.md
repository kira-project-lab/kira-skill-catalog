# Browser TTS via existing OpenAI-compatible Voice UI

Use this when connecting a custom TTS service such as `voice.ops.kiraproject.ru` to Hermes Web UI chat playback.

## Default approach

1. Prefer the existing **Settings → Voice → OpenAI TTS** UI if the service exposes an OpenAI-compatible endpoint.
2. Set browser-side `hermes-tts-settings-v2` rather than changing server TTS code:
   - `provider: "openai"`
   - `openaiBaseUrl: "https://voice.ops.kiraproject.ru/v1"`
   - `openaiModel: "qwen3-tts"`
   - `openaiVoice: "kira-xiangling"`
   - `openaiApiKey: ""` when the endpoint does not require a key.
3. Verify the settings page visibly shows `OpenAI TTS`, the endpoint, model, and voice.
4. Verify playback with the existing **Test Voice** button or direct browser fetch to `<baseUrl>/audio/speech`.

## Avoid

- Do not reroute `/api/hermes/tts` or `/api/tts/proxy` just to use a custom OpenAI-compatible browser TTS endpoint.
- Do not add a new provider when existing UI fields already express the configuration.
- Do not rebuild or restart production just to write browser/localStorage settings.
- Do not hide Kira Voice behind server-side magic when Maxim expects the configured endpoint/model/voice to be visible in the existing UI.

## Useful browser snippet

```js
localStorage.setItem('hermes-tts-settings-v2', JSON.stringify({
  provider: 'openai',
  webspeechVoice: '',
  openaiApiKey: '',
  openaiBaseUrl: 'https://voice.ops.kiraproject.ru/v1',
  openaiModel: 'qwen3-tts',
  openaiVoice: 'kira-xiangling',
  customUrl: '',
  customApiKey: '',
  edgeUrl: '',
  edgeVoice: 'zh-CN-XiaoxiaoNeural',
  edgeRate: 1,
  edgePitchHz: 0,
  mimoApiKey: '',
  mimoBaseUrl: 'https://api.xiaomimimo.com/v1',
  mimoModel: 'mimo-v2.5-tts',
  mimoVoice: '冰糖',
  mimoVoiceDesignDesc: '',
  mimoStylePrompt: '',
}))
location.hash = '#/hermes/settings?tab=voice'
```
