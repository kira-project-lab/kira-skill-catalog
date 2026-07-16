# Hermes Web UI multi-instance topology

Use this pattern when you need both a stable production surface and a preview/dev surface for the same codebase.

## Target shape

- One canonical checkout is the source of truth for `origin/main` and production.
- Preview work should use a temporary worktree or an explicitly isolated checkout, not a second equal-priority copy.
- Each runtime instance must have its own port, `HERMES_WEB_UI_HOME`, `HERMES_WEBUI_STATE_DIR`, and upload directory.
- Different domains must map to different runtimes when you want isolation.

## Canonical Kira pair

For Kira home deployments, the known canonical pair is:

- `hermes.ops.kiraproject.ru` → production runtime on `127.0.0.1:8648`
- `hermes.dev.ops.kiraproject.ru` → preview/dev runtime on `127.0.0.1:8649`

Treat this pair as authoritative only if the inventory and service files agree.
If they drift, update the inventory and service definitions together, then verify the live ports and `/health` endpoints.

## Operational rule

Do not keep two permanent checkout copies in a symmetric role unless there is a concrete reason.
Prefer one canonical checkout plus disposable preview worktrees so the source of truth stays obvious and synchronization overhead stays low.

## Accepted two-folder Kira policy

Maxim accepts a simpler two-folder policy for Hermes Web UI on this machine:

- `/home/werserk/2-kira/hermes-web-ui` is the production deploy checkout only. It must stay on `origin/main`, serves `hermes.ops.kiraproject.ru`, and should not be used for feature-branch development.
- `/home/werserk/2-kira/hermes-web-ui-dev` is the unstable dev/preview checkout. It may switch to arbitrary pushed feature branches and serves `hermes.dev.ops.kiraproject.ru`.

This policy is safe only if deploys are ref-based and destructive in deploy checkouts: `git fetch`, `git reset --hard <remote-ref>`, clean/build/restart/health. Do not copy files between checkouts for deploy. Feature work should be committed and pushed before preview deployment. If a separate work checkout is later needed, add it explicitly rather than reusing the production checkout.
