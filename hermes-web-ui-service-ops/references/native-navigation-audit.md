# Hermes Web UI native navigation audit

Use this note when reviewing or improving navigation/buttons in Hermes Web UI.

## Core rule

Navigation must be a real link; actions must be buttons.

- Use links (`RouterLink` custom rendering a real `<a href=...>`, or `<a>`) for resources/routes users can open directly.
- Use buttons for local UI actions: open modal, delete, rename, pin, toggle sidebar/list/drawer, update, logout.

This preserves native browser behavior: middle-click, Ctrl/Cmd-click, copy link, status-bar URL preview, context-menu open-in-new-tab, and accessibility semantics.

## High-value targets

1. **Sidebar route items**
   - Avoid `button.nav-item @click="router.push(...)"` for route navigation.
   - Convert route entries to real links while keeping existing `.nav-item` styling.
   - Keep search/open-modal/collapse/logout/update controls as buttons.

2. **Chat session rows**
   - Normal mode session rows are resources and should expose `/session/:id` as `href`.
   - Batch/selectable mode should remain non-navigation so row selection does not open a session.
   - Modified clicks (`metaKey`, `ctrlKey`, `shiftKey`, `altKey`, non-left button) should not be hijacked by SPA click handlers.

3. **Session context menu**
   - Add explicit `Copy link` and `Open in new tab` actions for session resources.
   - Build URLs with `router.resolve({ name: 'hermes.session', params: { id } }).href`; make copied links absolute with `new URL(href, window.location.origin).toString()`.

4. **Persistent navigation UI state**
   - Persist low-risk UI state such as collapsed sidebar groups in localStorage.
   - Do not use persisted state as resource identity; routes remain source of truth for selected resources.

## Implementation pattern that worked

- Add a tiny reusable link wrapper (for example `RouteLinkItem.vue`) around `RouterLink custom` that renders a real `<a>` and forwards classes/slots. Use it for sidebar/logo navigation so existing styles remain intact while browser semantics return.
- For session rows, make the component mode-aware:
  - normal/resource mode: render `<a class="session-item" :href="to">`;
  - batch/selectable mode: render `<button class="session-item" type="button">`.
- Keep left-click SPA behavior by preventing default and emitting the existing `select` event only for unmodified left clicks. Do **not** intercept modified clicks (`metaKey`, `ctrlKey`, `shiftKey`, `altKey`, non-left button`), so native browser tab behavior wins.
- If a row has nested warning/delete controls while the parent is an anchor, either restructure them as sibling controls or make every nested action use both propagation and default prevention (`@click.stop.prevent`). Add a focused regression test for this; independent review caught this as a real blocker.

## Test strategy

- Unit tests: assert rendered route controls are actual anchors with expected `href`.
- Unit tests: assert selectable/batch session rows are not anchors.
- Unit tests: assert nested row action controls do not emit row selection and do not trigger anchor navigation (`.prevent`).
- E2E tests: query route navigation by role `link`, not `button`, and assert hrefs.
- Manual browser smoke: middle-click/Cmd-click sidebar links and session rows; verify current tab is not unexpectedly hijacked.
- If the full repo `npm test` has unrelated baseline failures, do not conflate them with navigation work; run and report targeted unit tests, build, relevant E2E, plus the unrelated failure list.

## Pitfalls

- Styling an anchor like a button is fine; making route navigation a button is not.
- Avoid nested interactive controls inside anchors when possible. If unavoidable, child action controls need both `stopPropagation` **and** `preventDefault`; `@click.stop` alone can still allow native anchor navigation.
- Do not rely on unit tests to prove middle-click opens a tab; test href semantics plus Playwright/browser smoke.

## Related files from the May 2026 audit

- `packages/client/src/components/layout/AppSidebar.vue`
- `packages/client/src/components/hermes/chat/ChatPanel.vue`
- `packages/client/src/components/hermes/chat/SessionListItem.vue`
- `packages/client/src/router/index.ts`
- Plan artifact: `docs/plans/2026-05-24-web-ui-native-navigation.md`
