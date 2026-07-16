# Hermes Agent update + Kira service recovery

Use this when updating the live Hermes Agent checkout that Web UI, gateway, and bridge workers depend on.

## Trigger

- User asks to update Hermes Agent itself, not just Hermes Web UI.
- Web UI bridge/gateway depends on `/home/werserk/.hermes/hermes-agent`.
- The goal is to restore stable Kira communication after the update.

## Safety rule

Hermes Agent updates are production-impacting for Kira on Maxim's PC. Do not run the update silently after drafting a script unless Maxim explicitly approves execution. Creating a script is safe; executing it stops services.

Tracked local edits in the agent checkout may be discarded only after explicit approval. If Maxim says a local patch is not needed, use `git reset --hard HEAD` before update so `hermes update` does not stash/restore unwanted code.

## Preflight

Check and record:

```bash
AGENT_ROOT=/home/werserk/.hermes/hermes-agent
HERMES=/home/werserk/.hermes/hermes-agent/.venv/bin/hermes

git -C "$AGENT_ROOT" status --short --branch
git -C "$AGENT_ROOT" remote -v
"$HERMES" --version
systemctl --user cat hermes-gateway-kira.service hermes-web-ui.service hermes-web-ui-dev.service
systemctl --user list-units 'hermes*' --no-pager
```

Current known topology on Maxim's PC:

- Agent checkout: `/home/werserk/.hermes/hermes-agent`
- Kira profile: `/home/werserk/.hermes/profiles/kira`
- Gateway: `hermes-gateway-kira.service`
- Prod Web UI: `hermes-web-ui.service`, health `http://127.0.0.1:8648/health`
- Dev Web UI: `hermes-web-ui-dev.service`, backend health `http://127.0.0.1:8647/health`, frontend `http://127.0.0.1:8649/`

## Update sequence

1. Create a timestamped backup directory under `~/.hermes/update-backups/`.
2. Save:
   - git status/remotes/head;
   - tracked diff;
   - `systemctl --user cat` for the three services;
   - `systemctl --user show` for ExecStart, env, PID, and working dirs.
3. Stop service dependents before mutating the agent checkout:

```bash
systemctl --user stop hermes-web-ui-dev.service hermes-web-ui.service hermes-gateway-kira.service
```

4. Kill stale bridge/gateway processes tied to this agent root if any survived:

```bash
pkill -TERM -f '/home/werserk/.hermes/hermes-agent.*hermes_bridge.py' || true
pkill -TERM -f '/home/werserk/.hermes/hermes-agent.*gateway run' || true
sleep 2
pkill -KILL -f '/home/werserk/.hermes/hermes-agent.*hermes_bridge.py' || true
pkill -KILL -f '/home/werserk/.hermes/hermes-agent.*gateway run' || true
```

5. If local tracked edits are approved for deletion:

```bash
git -C /home/werserk/.hermes/hermes-agent reset --hard HEAD
```

6. Normalize update remote. `hermes update` fetches `origin/main`; if `origin` is an inaccessible fork but `upstream` is healthy, switch `origin` fetch URL to upstream before update:

```bash
cd /home/werserk/.hermes/hermes-agent
if ! git fetch origin --prune; then
  upstream_url=$(git remote get-url upstream)
  git remote set-url origin "$upstream_url"
  git fetch origin --prune
fi
```

7. Run the updater with backup and noninteractive prompts:

```bash
HERMES_HOME=/home/werserk/.hermes/profiles/kira \
  /home/werserk/.hermes/hermes-agent/.venv/bin/hermes update --yes --backup --branch main
```

8. Verify the venv entrypoint:

```bash
/home/werserk/.hermes/hermes-agent/.venv/bin/hermes --version
```

If the entrypoint fails after code changed, reinstall editable package into the venv used by systemd, then retry `--version`.

## Restart and verification

Start in dependency order:

```bash
systemctl --user daemon-reload
systemctl --user reset-failed hermes-gateway-kira.service hermes-web-ui.service hermes-web-ui-dev.service || true
systemctl --user start hermes-gateway-kira.service
systemctl --user start hermes-web-ui.service
systemctl --user start hermes-web-ui-dev.service
```

Then wait and verify:

```bash
curl -fsS http://127.0.0.1:8648/health
curl -fsS http://127.0.0.1:8647/health
curl -fsS http://127.0.0.1:8649/
HERMES_HOME=/home/werserk/.hermes/profiles/kira \
  /home/werserk/.hermes/hermes-agent/.venv/bin/hermes --profile kira gateway status
systemctl --user --no-pager --plain status hermes-gateway-kira.service hermes-web-ui.service hermes-web-ui-dev.service
ss -ltnp | grep -E ':(8648|8649|8647)\b'
```

## Failure behavior

If update/restart fails:

- do not leave Kira stopped;
- restart the known services on the current checkout;
- print recent journals for the three services;
- report the backup/log directory.

A good script should use `trap ERR` for this recovery path.

## Reporting

For a generated script, report the absolute path, exact run command, and what it will stop/restart. Do not claim the update happened unless the script actually ran and health checks passed.
