# Upstream Sync Certification Loop

Use this when executing a Hermes Web UI testing-development loop or preparing a future `integration/upstream-*` update gate.

## Execution pattern

1. Start from the live-dev checkout unless the task explicitly targets production:
   - `/home/werserk/2-kira/hermes-web-ui-dev`
   - branch `dev`
   - verify `git status --short --branch`, `git rev-parse --short HEAD`, and `codegraph status`.
2. Close already-started P0 slices before opening broader work.
3. For each high-risk contract:
   - run CodeGraph exploration / affected-test discovery;
   - write or update deterministic tests first;
   - verify RED when production behavior is changed;
   - apply minimal GREEN production fix only if the RED test proves a gap;
   - run focused tests and the affected tests CodeGraph suggests.
4. Keep stable gate docs tracked when they should guide future agents. Local `.hermes/plans` and `.hermes/research` can stay ignored, but durable promotion rules belong under `docs/harness/`.
5. When a committed `dev` slice is intended to update live-dev, push `dev`, restart `hermes-web-ui-dev.service`, and verify local/public `/health` reports the pushed commit.

## Useful certification groups

Session list / prefs / persistence:

```bash
npm run test -- tests/server/sessions-controller.test.ts tests/server/session-browser-prefs.test.ts tests/server/sessions-db.test.ts tests/server/sessions-db-lineage.test.ts tests/client/session-browser-prefs.test.ts tests/client/session-list-item.test.ts
```

Chat row-state / run lifecycle:

```bash
npm run test -- tests/server/session-row-status.test.ts tests/server/chat-run-bridge-readiness.test.ts tests/client/session-row-sync.test.ts tests/client/session-list-item.test.ts
```

Runtime / provider / coding-agent launch:

```bash
npm run test -- tests/server/coding-agents-launch.test.ts tests/server/handle-coding-agent-run.test.ts tests/server/agent-bridge-profile-env.test.ts tests/client/coding-agent-runtime-source-contract.test.ts
```

Static assets / settings preservation:

```bash
npm run test -- tests/client/web-app-icons.test.ts tests/client/i18n-coverage.test.ts tests/client/paperclip-view.test.ts
curl -fsSI https://app.dev.kiraproject.ru/skill-recommendations.en.md
curl -fsSI https://app.dev.kiraproject.ru/site.webmanifest
```

Full promotion confidence:

```bash
npm run harness:check
npm run test:coverage
npm run test:e2e
npm run build
codegraph sync /home/werserk/2-kira/hermes-web-ui-dev
codegraph status /home/werserk/2-kira/hermes-web-ui-dev
```

## Pitfalls discovered in execution

- Full E2E can expose stale tests unrelated to the product-code slice. Do not patch production code to satisfy an obsolete test assertion. First inspect the current UI snapshot/error context and update the test to the current contract when the product behavior is already correct.
- Session row width tests must account for the avatar/identity column. A content-only width assertion can falsely fail after the current three-row session-card layout; assert that no action-menu space is reserved while allowing intentional avatar space.
- Voice dialogue E2E should follow the current inline voice flow: click the record toggle, wait for the cancel/confirm recording controls, confirm the recording, then assert the transcript is staged. Do not assume the original record toggle remains the active pressed control while recording.
- Socket.IO E2E mocks may need the manager-style `socket.io.on(...)` API as well as `socket.on(...)` when testing reconnect/catch-up behavior.
- If `packages/server/src/controllers/hermes/sessions.ts` or other chat/session-chain files change, run `npm run harness:check`; add a `docs/chat-chain-changes/*.md` fragment when required before claiming the gate is green.
