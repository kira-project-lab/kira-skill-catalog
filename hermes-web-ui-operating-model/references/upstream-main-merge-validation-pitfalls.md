# Upstream-main merge validation pitfalls

Use this as a companion to `upstream-main-to-dev-merge.md` when reconciling large author `upstream/main` drops into Kira `origin/dev`.

## Push gate

Do not push the merge commit just because conflicts are resolved and `build` passes. For broad upstream merges, require the full broad-change gate before publishing `origin/dev`:

```bash
NODE_ENV=development npm ci --ignore-scripts
npm run harness:check
npm run build
npm run test:coverage
```

If `test:coverage` is red, stop before push and report the failing suites as blockers. Live-dev restart/health verification comes only after a pushed green merge.

## Common reconcile patterns

- Server abort/runtime state: when upstream and Kira both touch abort helpers, avoid accessing a possibly undefined `state` after lookups. Prefer the already-narrowed active state object for profile/runtime fields, and rerun `npm run build` to catch TypeScript narrowing regressions.
- Hoisted Vitest mocks: when a module mocked by `vi.mock(...)` needs a shared mock object, create it with `vi.hoisted(...)`; plain top-level variables can be unavailable because Vitest hoists the mock factory.
- Session row/source-contract tests: if Vue SFC text is needed, Vite `?raw` imports can be appropriate. If SCSS or mixed assets raw-import to an empty string or run through jsdom/browser externalization, switch the contract to a Node-capable file read or a narrower component-source assertion instead of hardcoding stale strings.
- Socket/store tests: upstream may add handlers or change socket call shape. Update existing mocks to match the new public store/socket contract rather than preserving old assertion shapes.
- Chat tool-trace merges: preserve Kira's transient-tool contract when upstream refactors trace rendering. Active run tool calls stay in the live `.tool-calls-panel` and are hidden from transcript until `run.completed`; completed historical/named tool calls render in transcript when tool traces are visible. Treat both `run_marker` and Socket.IO `run_id` as run markers, and keep compatibility selectors such as `.message.tool .tool-line`, `.tool-details`, and `.tool-error-badge` unless tests/contracts are deliberately migrated.

## Reporting rule

When validation is red, the correct completion report is: merge state, exact green checks, exact red check, top failing suites, and an explicit "not pushed" decision. Do not present the plan as completed.