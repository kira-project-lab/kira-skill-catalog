# Isolated Linux-user Hermes Web UI profile

Use when creating a Hermes/Web UI space for another person where filesystem privacy matters.

## Core rule

A Hermes profile alone is not a security boundary. If the user must not access Maxim's files or other disks, run Hermes Agent and Hermes Web UI as a separate OS user (or a container/sandbox with equivalent filesystem isolation). Instruction-only rules such as “stay under `/home/<user>`” are not enough when `terminal`, `file`, `browser`, or MCP tools are enabled.

## Recommended layout

```text
Linux user:      <user>
Home:            /home/<user>
Hermes root:     /home/<user>/.hermes
Hermes profile:  /home/<user>/.hermes/profiles/<profile>
Workspace:       /home/<user>/workspace
Web UI state:    /home/<user>/.hermes-web-ui
Web UI service:  system service running as User=<user>
```

Create the OS user/home first, then install Hermes/Web UI under that user. Keep `/home/<user>` mode `700` and verify that the new user cannot read `/home/werserk` before reporting success.

## Active profile pitfall

Hermes Web UI derives the active profile from `<hermes-root>/active_profile`. If the service starts with `HERMES_HOME=/home/<user>/.hermes/profiles/<profile>`, Web UI may still show/use `default` in profile UI because it detects the root and reads `<root>/active_profile`.

Set the active profile explicitly:

```bash
printf '%s\n' '<profile>' | sudo tee /home/<user>/.hermes/active_profile >/dev/null
sudo chown <user>:<user> /home/<user>/.hermes/active_profile
sudo chmod 600 /home/<user>/.hermes/active_profile
```

For profile-scoped credentials, copy or configure auth/env in the effective profile location as well as the root when needed:

```bash
sudo install -o <user> -g <user> -m 600 /path/to/auth.json /home/<user>/.hermes/auth.json
sudo install -o <user> -g <user> -m 600 /path/to/auth.json /home/<user>/.hermes/profiles/<profile>/auth.json
sudo install -o <user> -g <user> -m 600 /path/to/.env /home/<user>/.hermes/profiles/<profile>/.env
```

## Systemd service pattern

Use a dedicated system service for the isolated user. Pin state and profile paths explicitly, and add filesystem restrictions for defense-in-depth.

```ini
[Service]
User=<user>
Group=<user>
WorkingDirectory=/home/<user>/workspace
Environment="HOME=/home/<user>"
Environment="PORT=<port>"
Environment="PATH=/home/<user>/.hermes/hermes-agent/.venv/bin:/home/<user>/.hermes/hermes-agent/venv/bin:/home/<user>/.npm-global/bin:/usr/local/bin:/usr/bin:/bin"
Environment="HERMES_HOME=/home/<user>/.hermes/profiles/<profile>"
Environment="HERMES_BIN=/home/<user>/.hermes/hermes-agent/venv/bin/hermes"
Environment="HERMES_AGENT_ROOT=/home/<user>/.hermes/hermes-agent"
Environment="HERMES_WEB_UI_HOME=/home/<user>/.hermes-web-ui"
Environment="HERMES_WEBUI_STATE_DIR=/home/<user>/.hermes-web-ui"
ExecStart=/usr/bin/node /home/<user>/.npm-global/lib/node_modules/hermes-web-ui/dist/server/index.js
Restart=on-failure
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/home/<user>
InaccessiblePaths=/home/werserk /root /mnt /media /run/media /srv
```

## Verification gates

Do not stop at `systemctl active`; Web UI can take several seconds before listening.

```bash
systemctl status hermes-web-ui-<user>.service --no-pager
journalctl -u hermes-web-ui-<user>.service -n 120 --no-pager
ss -ltnp | grep ':<port>'
curl -fsS -I http://127.0.0.1:<port>/
sudo -Hu <user> test -r /home/werserk && echo FAIL || echo PASS
sudo -Hu <user> env HOME=/home/<user> HERMES_HOME=/home/<user>/.hermes \
  PATH=/home/<user>/.hermes/hermes-agent/venv/bin:/home/<user>/.npm-global/bin:/usr/bin:/bin \
  hermes --profile <profile> profile show <profile>
```

If the first curl immediately after start fails with connection refused, inspect fresh journal lines and retry after the `[bootstrap] listening on 0.0.0.0:<port>` log line before calling it a failure.

## Login hardening

After `hermes-web-ui reset-default-login`, immediately change `admin / 123456` via the auth API or UI, then verify old credentials return `401` and new credentials return a token. Do not leave the default password on a LAN-reachable service.
