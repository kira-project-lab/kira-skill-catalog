# Testing Research + CodeGraph + TDD Plan Execution

Use this when Maxim asks to fully execute a Hermes Web UI plan that combines research, CodeGraph analysis, and test implementation.

## Pattern

1. Confirm the live-dev checkout, branch, commit, and CodeGraph status before writing artifacts or tests.
2. Read repo docs first (`AGENTS.md`, `DEVELOPMENT.md`, `ARCHITECTURE.md`, `docs/harness/validation.md`) and any existing `.hermes/analysis/*` artifact before external testing theory.
3. Convert research into a repo-specific artifact under `.hermes/research/`, but do not treat research as completion if the plan asks for implementation.
4. Run CodeGraph deep-dives per product contract, then write focused `.hermes/plans/*` follow-up plans with exact RED tests and validation commands.
5. Implement at least the first requested P0 test plan with strict RED/GREEN: write the failing Vitest test, run it and capture the intended failure, implement the minimal production change, rerun focused tests.
6. After production changes, run `git diff --name-only | codegraph affected --path /home/werserk/2-kira/hermes-web-ui-dev --stdin` and include the affected tests in validation when practical.
7. Run `npm run harness:check` after touching chat/session-chain files, not only at the end; it may require a `docs/chat-chain-changes/*.md` fragment.

## Pitfalls

- `packages/server/src/controllers/hermes/sessions.ts` is considered part of the chat/session chain by the harness. If changed, add a fragment under `docs/chat-chain-changes/` with date, PR/commit (`pending` if local), touched feature, and behavior impact.
- Vitest is not Jest. Do not append Jest-only flags such as `--runInBand` to `npm run test -- ...`; use the repo's normal `vitest run` invocation unless a Vitest-supported flag is needed.
- `.hermes/research` and `.hermes/plans` may be locally ignored and not appear in `git status`. Verify their existence directly before reporting them.
- CodeGraph affected-test output can include surprising tests (for example broad controller/skills coupling). Treat it as a selection hint, not proof; run the affected tests that are cheap/relevant.
- Build warnings from existing CSS/chunk-size issues are not failures if `npm run build` exits 0; report only if they affect the task.

## Session-list claimed scan regression pattern

Known P0 contract: logged-in curated session list must keep older claimed/pinned/tagged Hermes sessions discoverable even when many newer unclaimed sessions precede them in chronological order.

A good regression test shape:

- Mock Hermes summaries as one fresh claimed row, many newer unclaimed rows, and one old claimed row.
- Mock `getClaimedSessionIds` to include the fresh and old rows.
- Request a small `limit`.
- Assert both claimed sessions are returned.

The minimal production fix used successfully was to scan a larger Hermes candidate window for logged-in users before claim filtering, while leaving anonymous/non-user behavior on the smaller window.