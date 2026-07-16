---
name: hermes-web-ui-upstream-sync
description: Use whenever Maxim wants to update Kira's Hermes Web UI fork from the original author/upstream, compare Kira fork vs upstream, plan or execute an upstream version bump, reconcile origin/dev with upstream/main, or maintain a long-lived downstream fork. This skill is mandatory for Hermes Web UI upstream syncs even if the request sounds like a simple git merge, pull, version check, or cherry-pick.
---

# Hermes Web UI Upstream Sync

This skill governs recurring maintenance of Kira's downstream Hermes Web UI fork against the original author's fast-moving upstream.

Use it together with `hermes-web-ui-operating-model`. For live service, deploy, health, or runtime verification, also use `hermes-web-ui-service-ops`.

Session-specific lessons from the 0.6.11 → 0.6.17/0.6.18 sync work are in `references/0.6.11-to-0.6.17-sync-lessons.md`, `references/kira-0.6.11-to-0.6.17-sync-notes.md`, `references/upstream-sync-static-assets-and-live-qa.md`, `references/integration-to-dev-promotion.md`, `references/upstream-sync-certification-matrix.md`, `references/upstream-branch-reset-and-test-gate-lessons.md`, `references/upstream-0.6.18-certification-lessons.md`, and `references/dev-ci-bootstrap-and-promotion.md`; consult them before large version jumps, downstream-layer assessments, static public asset drift, live QA, promotion from integration branch to `origin/dev`, resetting `dev` after a failed adoption, deciding whether an existing `integration/upstream-*` branch is safe to continue, when tests fail after an upstream rebase, when dynamic imports fail in preview, when authenticated app-start effects look stale after login, when PR-to-`dev` checks do not appear despite workflow edits, or when Playwright CI is green but fails on artifact upload quota.

## Mental model

Treat Kira Hermes Web UI as a **long-lived downstream fork**, not as a casual local modification of upstream.

- `upstream/main` = original author's product line. Keep it clean and read-only.
- `origin/main` = stable Kira production line. Never update it directly from upstream.
- `origin/dev` = Kira integration/review line.
- `integration/upstream-<version>` = temporary update branch where upstream is adopted and Kira's downstream layer is reapplied/reconciled.

Default strategy: **new upstream base first, reapply Kira layers intentionally**.

Prefer:

```text
upstream/main@new-version
  + Kira deploy/topology layer
  + Kira product/integration layer
  + Kira chat/session state layer
  + Kira visual/UX layer
  -> integration/upstream-<version>
  -> origin/dev
  -> origin/main only after approval
```

Avoid:

```text
origin/dev + blind merge upstream/main
```

A blind merge can accidentally let old Kira code override newer upstream fixes in runtime, providers, desktop, bridge, or coding-agent flows.

## Hard rules

- Do not merge, rebase, cherry-pick, deploy, or push during a delta review unless Maxim explicitly asks to execute.
- Never update `origin/main` directly from upstream.
- Start all production-affecting adoption through `dev` or an integration branch that will later merge into `dev`.
- Do not treat package version bump as the update; version bump is only metadata after the code is reconciled.
- Do not assume Kira changes are only cosmetic. Check actual commit/file deltas.
- Keep upstream runtime/provider/desktop/bridge fixes unless there is a deliberate Kira reason to override them.
- Stage only intended hunks; live-dev may contain unrelated parallel work.
- Public static assets under `packages/client/public/` are part of Kira's downstream layer even when no TS import references them. If runtime code fetches a public markdown/manifest/icon file, verify the file is present and served in branch preview; do not suppress the console error as a substitute for restoring the asset.
- For broad generated rewrites during sync repair (especially i18n locale mass-updates or generated test fixtures), first state the exact file set and strategy. Prefer targeted edits over shell one-liners so review can see whether the change preserves upstream or reintroduces stale Kira code.

## Standard workflow

### 0. Branch archaeology for historical/status questions

If Maxim asks whether a special upstream-sync branch/worktree already existed, do not answer from memory. Check both conversation history and git refs:

```text
session_search("hermes web ui integration upstream branch version update")
git branch -a --list '*integration*' '*upstream*' '*backup*'
git worktree list --porcelain
git show-ref | grep -E 'integration/upstream|backup/dev-before' || true
```

Report the lifecycle clearly: branch name, worktree path, whether it was promoted to `dev`, whether `dev` was later reset, and which ref now preserves the abandoned line. After a reset back to stable baseline, treat the old `integration/upstream-<version>` as a backup/inspection line; for a renewed attempt prefer a fresh branch such as `integration/upstream-<version>-v2` or a branch for the current upstream version.

### 1. Establish state

Use the checkout with both remotes configured. Usually:

```bash
cd /home/werserk/2-kira/hermes-web-ui
```

Record current state before touching anything:

```bash
git status --short --branch
git remote -v
git fetch origin main dev --prune
git fetch upstream main --prune
git rev-parse --verify --short refs/remotes/origin/main
git rev-parse --verify --short refs/remotes/origin/dev
git rev-parse --verify --short refs/remotes/upstream/main
git merge-base refs/remotes/origin/main refs/remotes/upstream/main | cut -c1-8
git rev-list --count refs/remotes/origin/main..refs/remotes/upstream/main
git rev-list --count refs/remotes/upstream/main..refs/remotes/origin/main
```

Check versions robustly:

```bash
git show refs/remotes/origin/main:package.json | jq -r .version
git show refs/remotes/upstream/main:package.json | jq -r .version
curl -fsS --max-time 8 https://app.kiraproject.ru/health | jq '{webui_version,webui_latest,git_branch,git_ref,git_commit,runtime}'
```

### 2. Produce upstream delta review

Summarize upstream-only work:

```bash
git log --oneline --decorate --no-merges refs/remotes/origin/main..refs/remotes/upstream/main
git diff --stat --find-renames refs/remotes/origin/main...refs/remotes/upstream/main
git diff --name-only --find-renames refs/remotes/origin/main...refs/remotes/upstream/main
```

If upstream has a changelog/i18n entries, inspect them too:

```bash
git show refs/remotes/upstream/main:packages/client/src/data/changelog.ts
git show refs/remotes/upstream/main:packages/client/src/i18n/locales/en.ts | grep -n "new_0_6" -A80
```

Report product buckets, not raw commit spam:

- user-visible features;
- reliability/runtime fixes;
- provider/model/coding-agent changes;
- desktop/update flow;
- security/storage/device changes;
- UI polish;
- Kira-sensitive conflict surfaces.

### 3. Produce Kira downstream layer map

Do not trust memory. Inspect Kira-only deltas:

```bash
git log --format=%s --no-merges refs/remotes/upstream/main..refs/remotes/origin/main
git diff --stat --find-renames refs/remotes/upstream/main...refs/remotes/origin/main
git diff --name-only --find-renames refs/remotes/upstream/main...refs/remotes/origin/main
```

Classify Kira changes by layer:

1. **Kira topology/deploy**
   - `.github/workflows/*deploy*`
   - `scripts/deploy-*`, `scripts/start-live-dev.sh`, topology docs
   - health metadata that reports Kira runtime accurately

2. **Kira product integrations**
   - Paperclip entrypoint/API/view
   - Kira-specific routes/settings/defaults
   - local profile/runtime assumptions

3. **Chat/session architecture**
   - server-authoritative row state
   - read receipts/read status
   - committed session snapshots
   - realtime session row sync
   - draft-first new chat lifecycle
   - session tags/filtering/pins/browser prefs

4. **Bridge/runtime policy**
   - YOLO/session-command routing
   - Codex profile OAuth/global defaults
   - local STT safety/probe behavior
   - run lifecycle/error reporting

5. **Visual/UX layer**
   - Obsidian-like shell
   - activity rail
   - composer/session-list styling
   - mobile parity
   - icons/PWA polish

6. **Tests/ADRs/docs**
   - Kira contracts that protect the fork
   - tests that should survive if their contract still matters

### 4. Choose adoption strategy

Use this default decision rule:

- If upstream touched mostly runtime/providers/desktop and Kira touched mostly UI: branch from `upstream/main` and reapply Kira layers.
- If upstream touched the same chat/session core Kira changed: branch from `upstream/main`, reconcile manually by contract, not by accepting either side wholesale.
- If upstream change is a tiny isolated fix: cherry-pick into `origin/dev` may be cheaper.
- If Kira's downstream feature now exists upstream in better form: drop or shrink the Kira patch instead of preserving it by inertia.

State the recommended route and strongest risk before executing.

### 5. Create integration branch

Only when Maxim asks to execute:

```bash
git switch --detach refs/remotes/upstream/main
git switch -c integration/upstream-<version>
```

Then apply Kira layers in this order:

1. deploy/topology and health reporting;
2. product integrations such as Paperclip;
3. backend/session contracts;
4. bridge/runtime policy;
5. frontend state stores and APIs;
6. visual/UX layer;
7. tests/docs/ADRs;
8. package/changelog metadata last.

Prefer small commits per layer. This makes conflict review and rollback possible.

### 6. Conflict resolution policy

When a conflict appears, decide by subsystem:

- **Providers/model catalog/coding-agent launch/desktop runtime/update flow:** prefer upstream first, then re-add only Kira-specific behavior.
- **Kira deploy topology/Paperclip/Kira profile assumptions:** preserve Kira behavior unless upstream introduced a cleaner generic hook.
- **Chat/session state:** reconcile against Kira ADRs and current product contract; do not blindly keep old Kira code if upstream added a more robust primitive.
- **Visual styling:** preserve Kira UX direction, but adapt to upstream component structure rather than reviving deleted/obsolete DOM.
- **Tests:** update tests to protect current intended behavior, not stale implementation details.

If a Kira patch exists only to compensate for an upstream bug that is now fixed, remove the Kira patch.

### 7. Validation gates before merge to dev

For broad upstream syncs, first produce an Integration Risk Report and Certification Matrix using `references/upstream-sync-certification-matrix.md`. If preview/live-dev shows multiple unrelated regressions (for example session order plus missing functions), treat it as a failed certification process: freeze `origin/main`, keep the integration branch for inspection, and certify protected product contracts before further promotion.

Run the smallest focused checks while iterating. Before proposing merge into `origin/dev`, run at least:

```bash
npm run harness:check
npm run test
npm run build
```

For broad chat/session changes, add:

```bash
npm run test:coverage
npm run test:e2e
```

For browser-visible changes, deploy to live-dev or branch preview according to `hermes-web-ui-operating-model`, then browser QA the critical flows. Use `references/live-qa-gate.md` for the dedicated `kira` dev superadmin flow, credential handling, token injection pitfall, and report shape:

- login/auth survives refresh;
- new chat and first send;
- existing session history loads;
- Codex/Claude Code conversation starts;
- model/provider selector works;
- files/upload/download if touched;
- voice/STT if touched;
- session row status/read/unread/running/queued states if touched;
- tags/pins/filters if touched;
- Paperclip entrypoint if touched;
- mobile session drawer/composer Enter behavior if touched.

### 8. Merge path

After integration branch is green:

```text
integration/upstream-<version> -> origin/dev -> live-dev verification -> origin/main after Maxim approval
```

Do not claim production is deployed from a merge alone. Production requires build/deploy workflow and `/health` evidence for the target commit.

## Report shape

For delta review:

```text
Проверил <checkout/ref>.
Наш webui: <version/commit>. Upstream: <version/commit>.
Divergence: upstream-only <N>, Kira-only <M>, merge-base <sha>.

Что нового у автора:
- ...

Наши конфликтные зоны:
- ...

Вердикт:
<merge/cherry-pick/rebase-like integration recommendation>

Следующий шаг:
<one concrete action>
```

For executed sync work:

```text
Сделано:
- branch: <name>
- applied layers: <list>
- checks: <pass/fail>
- live-dev/preview: <URL/status if deployed>

Блокеры/риски:
- ...

Следующий шаг:
- ...
```

## Kira-sensitive files and areas

Expect conflicts or regressions around:

- `packages/client/src/components/hermes/chat/ChatPanel.vue`
- `packages/client/src/components/hermes/chat/ChatInput.vue`
- `packages/client/src/components/hermes/chat/SessionListItem.vue`
- `packages/client/src/stores/hermes/chat.ts`
- `packages/client/src/stores/hermes/session-browser-prefs.ts`
- `packages/client/src/api/hermes/sessions.ts`
- `packages/server/src/controllers/hermes/sessions.ts`
- `packages/server/src/db/hermes/*session*`
- `packages/server/src/services/hermes/run-chat/*`
- `packages/server/src/services/hermes/session-row-status.ts`
- `packages/server/src/services/hermes/session-title-generator.ts`
- `packages/server/src/services/hermes/agent-bridge/*`
- `packages/server/src/services/coding-agents.ts`
- `packages/client/src/views/hermes/PaperclipView.vue`
- `packages/server/src/controllers/hermes/paperclip.ts`
- `scripts/deploy-*`, `scripts/start-live-dev.sh`
- `.github/workflows/deploy-*.yml`
- i18n locale files when UI text changes

This list is a starting point, not a substitute for `git diff --name-only`.

## Common mistakes

- Updating version in `package.json` before reconciling behavior.
- Letting Kira's old chat/session files overwrite upstream coding-agent fixes.
- Treating UI-only assumptions as fact without checking server/session/store diffs.
- Running only build when session state changes need e2e/browser verification.
- Merging to `main` because the integration branch builds locally.
- Forgetting that upstream may rename repository/package metadata; preserve what is product-correct for Kira while keeping functional upstream changes.
