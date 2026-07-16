# New-user profile onboarding in Hermes Web UI

Use when Maxim wants to give another person immediate Web UI access to Kira/Hermes.

## Decision fork

1. **Fast shared-host onboarding** — user gets an account on the existing custom `app.kiraproject.ru` Web UI and a separate Hermes profile under `/home/werserk/.hermes/profiles/<profile>`.
   - Fastest path when Maxim explicitly accepts shared runtime/file access.
   - Not OS-isolated: backend/bridge still run as `werserk`.
   - Good for “make it work now; sandbox later”.
2. **Isolated onboarding** — separate Linux user/container and separate Web UI backend process.
   - Required for real filesystem privacy.
   - Do not install stock/npm Web UI if Maxim expects the custom fork UI; use the same custom codebase/build under a separate service or reverse-proxy hostname.

## Fast shared-host checklist

- Create Hermes profile under the existing Hermes root:
  - `hermes profile create <profile> --clone-from kira --clone --description "..." --no-alias`
- Create workspace, e.g. `/home/werserk/<profile>`.
- Edit `<profile>/SOUL.md`:
  - user name and language;
  - channel: `app.kiraproject.ru`;
  - workspace path;
  - explicit note that OS isolation is not enabled yet;
  - separate profile memory, not Maxim/Kira context.
- Edit `<profile>/config.yaml`:
  - `terminal.cwd: /home/werserk/<profile>`;
  - `display.language: ru` if Russian user;
  - enable memory/user profile;
  - if using built-in profile-local memory, set `memory.provider: ""`;
  - remove Kira-specific hooks, `mcp_servers`, and plugin refs when they point into Kira-specific profile GitOps paths or personal workspaces.
- Copy required auth/credentials from the active Kira profile if the model provider is OAuth-backed:
  - prefer `/home/werserk/.hermes/profiles/kira/auth.json` over root `/home/werserk/.hermes/auth.json` when Kira's profile has the working credential pool;
  - verify with a one-shot `hermes --profile <profile> chat -q 'Ответь ровно одним словом: READY' --toolsets ''`.
- Add a Web UI user in the active runtime DB.
  - Production-like runtime DB: `/home/werserk/.hermes-web-ui/hermes-web-ui.db`.
  - Live-dev in `NODE_ENV=development` uses the checkout-local DB, usually `/home/werserk/2-kira/hermes-web-ui-dev/packages/server/data/hermes-web-ui.db`; do not edit `/home/werserk/.hermes-web-ui-dev/hermes-web-ui.db` without verifying it is active.
  - Hash format is `scrypt:<salt>:<hex>` using Node-compatible scrypt parameters from `users-store.ts`; verify with real login after writing.
  - Preferred access model for a non-admin user: role `admin` plus a `user_profiles` row mapping that user to exactly the new profile with `is_default=1`.
  - Use `super_admin` only if the user intentionally needs to see/manage every profile; otherwise it exposes more than needed.
- Verify:
  - login succeeds on the active service URL (`http://127.0.0.1:8648/api/auth/login` for prod-like, `http://127.0.0.1:8647/api/auth/login` for live-dev);
  - handle both login token shapes: `token` and `accessToken`;
  - `/api/auth/me` may nest the authenticated user under `user`; verify `user.username`, `user.role`, and `user.status`;
  - `/api/hermes/profiles` includes the new profile for that login and does not expose unrelated profiles when using the scoped access model;
  - one-shot model smoke-test returns expected text.

## Profile rename / polish checklist

When Maxim asks to rename a freshly-created user profile or make it look like another profile:

- Rename with the CLI first so Hermes filesystem state and aliases move together:
  - `hermes profile rename <old> <new>`
- Rename the workspace directory if one was created under the old name, then update `terminal.cwd` and user-facing workspace docs.
- Update Web UI DB profile bindings:
  - `user_profiles.profile_name`
  - `gc_session_profiles.profile_name`
  - `user_session_browser_prefs.profile_name`
  - `user_session_read_state.profile_name`
- Copy profile avatar metadata from the source profile if needed. Web UI profile avatars live under:
  - `/home/werserk/.hermes-web-ui/profile-metadata/<base64url(profile_name)>/avatar.json`
  - `/home/werserk/.hermes-web-ui/profile-metadata/<base64url(profile_name)>/avatar.bin`
- Keep credentials unchanged unless Maxim explicitly asks to rotate them.
- Re-verify `/api/hermes/profiles` as the target Web UI user, not only as Maxim/admin.

## My-notes / memory / SOUL cloning guidance

When Maxim asks for a new person's notes/memory/SOUL to resemble his Kira profile:

- Keep the operating style and decision discipline: concise Russian by default, direct verdicts, evidence-first fixes, exact paths/statuses, tight scope, anti-flattery, no vague pilots.
- Replace the subject everywhere (`Maxim` → target user) and preserve the deputy framing.
- Remove or generalize Maxim-specific filesystem paths, vault paths, archives, project roots, personal devices, and private project details.
- Keep only class-level reusable conventions that are useful to the new user, such as: compact/no-meta copy, source-of-truth vs UI projection explanations, evidence gates, SOTA/open-source review for serious research, and baseline→repro→root-cause→minimal-fix→validate for debugging.
- After writing, grep SOUL/config/memories for stale names and personal paths before reporting success.

## UX note

The active profile selection is browser-local (`localStorage` key `hermes_active_profile_name`). For a newly-created Web UI user, tell them to choose `PROFILES → <profile>` after first login unless the `user_profiles` default-profile assignment already limits them to exactly the intended profile.

## Pitfalls

- Do not confuse “separate Hermes profile” with filesystem privacy. If Web UI runs as `werserk`, all tools run with `werserk` authority unless separately sandboxed.
- Do not spin up an npm/stock Hermes Web UI for a user when Maxim expects the custom production UI. First decide: existing custom UI profile vs isolated custom-code service.
- Do not leave the new profile with root-level `auth.json` if the provider is actually authenticated only in Kira's profile-local credential pool.
- Do not leave stale old profile names in Web UI DB mapping tables after a profile rename; the UI may show no profiles or the wrong profile.
- `systemctl active` can appear before Web UI is listening; check journal for `[bootstrap] listening` and retry HTTP.
