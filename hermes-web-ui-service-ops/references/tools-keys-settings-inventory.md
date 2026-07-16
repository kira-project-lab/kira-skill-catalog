# Hermes Web UI Tools & Keys settings inventory

Use when Maxim asks what the **Tools & Keys → Tools** or **Tools & Keys → Settings** entries mean, or asks for the whole list.

## Scope

These UI rows are profile `.env` variables, not chat-model parameters. They include:

- tool/API credentials and backend URLs;
- messaging/gateway credentials and allowlists;
- agent/runtime settings such as sudo, max iterations, prefill files, and ephemeral prompts;
- extra profile keys written by setup/provider flows.

## Safe answer rules

- Never print actual secret values. List variable names and meanings only.
- Call out dangerous rows explicitly: `SUDO_PASSWORD`, `GATEWAY_ALLOW_ALL_USERS`, `API_SERVER_KEY`, webhook secrets, bot tokens, passwords, and public bind settings.
- Distinguish configured/missing UI state from capability: a row existing does not mean the integration is active.
- Explain that most rows should stay empty unless that integration is intentionally used.

## Source-of-truth extraction pattern

Prefer live repo/config inspection over guessing from the screenshot.

```bash
cd /home/werserk/2-kira/kira-hermes-agent
python3 - <<'PY'
from hermes_cli.config import OPTIONAL_ENV_VARS, _EXTRA_ENV_KEYS

for cat in ['tool', 'skill', 'messaging', 'setting', 'provider']:
    print('\n##', cat)
    for key, meta in OPTIONAL_ENV_VARS.items():
        if meta.get('category') == cat:
            print(f"{key}\t{meta.get('description', '')}")

print('\n## extra env keys')
for key in sorted(_EXTRA_ENV_KEYS):
    print(key)
PY
```

For screenshot-specific rows not present in `OPTIONAL_ENV_VARS`, search `_EXTRA_ENV_KEYS`, gateway setup metadata, and plugin manifests/providers. Examples seen in Web UI settings: `SMS_HOME_CHANNEL`, `HERMES_SIMPLEX_TEXT_BATCH_DELAY`, `RAFT_PROFILE`, and plugin-specific keys such as `BRV_API_KEY`.

## Answer shape

1. One sentence: these are `.env` settings for Hermes integrations/runtime, not model settings.
2. Explain only the visible screenshot rows first.
3. Then give the full relevant list grouped by category.
4. End with practical guidance: which can stay empty and which are risky.

Keep the answer compact. If the list is long, use grouped code blocks rather than prose for every item.