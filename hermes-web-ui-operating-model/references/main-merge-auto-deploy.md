# Hermes main-merge auto-deploy

Session note: stable Hermes production is deployed from `hermes-web-ui` after a successful `Build` workflow on `origin/main`.

## Flow
1. Merge to `origin/main` in `hermes-web-ui`.
2. `Build` workflow runs on main.
3. `Deploy Hermes Home` triggers via `workflow_run` after successful build.
4. Deploy script SSHes to the home host, checks out the exact commit, runs install/build, restarts `hermes-web-ui.service`, and waits for `/health`.

## Policy split
- `hermes-web-ui` owns CI/deploy orchestration.
- `kira-ops` owns deploy policy and service inventory.
- Production auto-deploy is documented in ops, but implemented in the app repo.

## Secrets required in `hermes-web-ui`
- `HERMES_DEPLOY_SSH_KEY`
- `HERMES_DEPLOY_SSH_HOST`
- optional: `HERMES_DEPLOY_SSH_USER`
- optional: `HERMES_DEPLOY_SSH_PORT`
- optional: `HERMES_DEPLOY_SSH_KNOWN_HOSTS`

## Verification reminders
- Build success is not deploy success.
- Confirm the workflow source is `workflow_run` on `Build`, not a manual-only deploy.
- Check `gh secret list --repo kira-project-lab/hermes-web-ui`; an empty/missing `HERMES_DEPLOY_SSH_KEY` makes prod deploy fail at `Prepare SSH key` before SSH.
- `Deploy Hermes Prod` can create skipped `workflow_run` entries for PR Build completions; the relevant prod deploy is the non-skipped run after the successful `push` Build on `main`.
- Confirm the service target is the stable unit, not the dev preview service.

## Secret boundary: GitHub Secrets vs Yandex Lockbox

For Hermes Web UI production auto-deploy, the deploy SSH key is consumed by **GitHub Actions before it can reach the home host**. The practical default is therefore GitHub repository/environment secrets for:

- `HERMES_DEPLOY_SSH_KEY`
- `HERMES_DEPLOY_SSH_HOST`
- optional `HERMES_DEPLOY_SSH_USER`
- optional `HERMES_DEPLOY_SSH_PORT`
- recommended `HERMES_DEPLOY_SSH_KNOWN_HOSTS`

Do not move this to Yandex Lockbox as a quick fix unless the task explicitly includes building a GitHub→Yandex trust bridge. Reading Lockbox from GitHub Actions still needs authentication first:

- simple path: store YC service-account credentials in GitHub Secrets anyway;
- stronger path: configure GitHub OIDC federation to a Yandex Cloud service account, then grant narrow Lockbox payload read.

Use Lockbox for Kira runtime secrets and cloud-hosted runtime payloads. Use GitHub Secrets for CI boundary credentials unless an OIDC federation is already present or explicitly in scope. If using GitHub Secrets, prefer a dedicated deploy SSH key restricted on the home host (separate deploy user or forced command to `scripts/deploy-prod.sh`).
