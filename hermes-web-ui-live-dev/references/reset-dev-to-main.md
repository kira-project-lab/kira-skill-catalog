# Reset live-dev branch to main

Use when Maxim explicitly asks to erase/reset `dev` and recreate it as a clone of `main` for Hermes Web UI live-dev.

Checklist:

1. Work in `/home/werserk/2-kira/hermes-web-ui-dev`.
2. Verify scope and cleanliness before destructive operations:
   ```bash
   git remote -v
   git fetch origin main dev --prune
   git status --short --branch
   git rev-parse HEAD origin/dev origin/main
   git status --porcelain | wc -l
   ```
3. If the worktree is clean and the user explicitly approved erasing `dev`, reset local `dev` to `origin/main`:
   ```bash
   OLD_DEV=$(git rev-parse origin/dev)
   MAIN_SHA=$(git rev-parse origin/main)
   git switch dev
   git reset --hard "$MAIN_SHA"
   ```
4. Force-update the remote with a lease pinned to the previously observed `origin/dev`, not a blind force push:
   ```bash
   git push --force-with-lease=refs/heads/dev:$OLD_DEV origin dev
   ```
5. Re-fetch and prove `dev` equals `main`:
   ```bash
   git fetch origin dev main
   git status --short --branch
   git rev-parse HEAD origin/dev origin/main
   git rev-list --left-right --count origin/main...origin/dev  # expect: 0 0
   ```
6. Restart the user service so public live-dev picks up the reset SHA:
   ```bash
   systemctl --user restart hermes-web-ui-dev.service
   ```
7. Poll local and public health until `runtime=live-dev` and `git_commit` equals `origin/main`/`origin/dev`:
   ```bash
   curl -fsS http://127.0.0.1:8649/health
   curl -fsS https://app.dev.kiraproject.ru/health
   ```

Report compactly: old dev SHA, new shared SHA, `origin/main...origin/dev` count, service state, and public `/health` commit.

Pitfalls:

- This is destructive branch history rewriting; do it only after explicit user instruction like “сотри dev”.
- Do not use plain `--force`; use `--force-with-lease` against the old observed remote SHA.
- A successful push is not enough: live-dev may still serve the old commit until `hermes-web-ui-dev.service` is restarted.
- Expect version metadata such as `webui_version` to roll back if `main` is older than the previous `dev`; mention this if visible in `/health`.
