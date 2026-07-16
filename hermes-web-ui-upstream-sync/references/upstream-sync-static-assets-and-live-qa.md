# Upstream sync static assets and live QA notes

Lessons from the Kira Hermes Web UI 0.6.11 → 0.6.17 sync.

## Static public assets can be downstream features

During an upstream-base reconstruction, public assets that are not imported by TypeScript can disappear silently if they exist only in Kira `origin/dev`.

Example:

- `packages/client/public/skill-recommendations.en.md`
- `packages/client/public/skill-recommendations.zh.md`

`SkillsView.vue` fetched `/skill-recommendations.en.md` / `/skill-recommendations.zh.md` at runtime. The UI still loaded, tests passed, but live QA caught a console error because the branch-preview bundle served the SPA HTML fallback instead of the markdown file.

Check for these before declaring browser QA clean:

```bash
git diff --name-only refs/remotes/upstream/main...refs/remotes/origin/dev -- packages/client/public
curl -fsS https://app.dev.kiraproject.ru/skill-recommendations.en.md | sed -n '1,20p'
curl -fsS https://app.dev.kiraproject.ru/skill-recommendations.zh.md | sed -n '1,20p'
```

If the runtime code still fetches a static file and the feature is useful, restore the asset from `origin/dev` rather than suppressing the error.

## Dedicated dev QA account

For live-dev/preview browser QA, use the dedicated `kira` dev superadmin account from `hermes-web-ui-service-ops` instead of ad hoc/default credentials.

Key details:

- Credential file: `/home/werserk/.hermes-web-ui-dev/secrets/kira-superadmin-credentials.env`.
- Do not print or save the password in memory.
- Login token belongs in `localStorage.hermes_api_key`; do not guess keys like `auth_token` or `hermes_auth_token`.
- Live-dev in development mode may use `packages/server/data/hermes-web-ui.db` under the checkout, not the production-like `HERMES_WEB_UI_HOME` DB.

## Branch preview worktree pitfall

If `preview/upstream-<version>` is checked out by `/home/werserk/2-kira/hermes-web-ui-dev`, do not run `git branch -f preview/...` from another worktree. Reset/push from the worktree that owns that branch, or create a new short-lived preview branch.

Pattern:

```bash
cd /home/werserk/2-kira/hermes-web-ui-dev
git fetch origin integration/upstream-<version>
git reset --hard origin/integration/upstream-<version>
git push -f origin preview/upstream-<version>
```

Then redeploy:

```bash
cd /home/werserk/2-kira/hermes-web-ui-upstream-sync
bash scripts/deploy-dev-branch.sh preview/upstream-<version>
curl -fsS https://app.dev.kiraproject.ru/health | jq '{webui_version,git_branch,git_commit,runtime}'
```

## Minimal live QA gate

After deploy, run a smoke that checks:

1. `/health` commit/version/branch.
2. API login as `kira` and `/api/auth/me` reports `super_admin`.
3. `/api/hermes/profiles` is accessible.
4. Browser boot reaches shell, not login loop or blank screen.
5. Chat, Skills, Settings routes render.
6. Chat draft typing works without sending a provider request.
7. Console/page errors are clean.

For Skills page, a missing recommendations file is a real console-gate failure even if the page has fallback UI.
