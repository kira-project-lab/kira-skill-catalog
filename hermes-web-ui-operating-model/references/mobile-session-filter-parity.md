# Mobile session filter parity

Use when restoring or changing session-list launchers on mobile.

## Contract

Mobile chat session drawer (`ChatSessionDrawerPane.vue`) should keep the same launcher order as desktop:

1. Search
2. Filter
3. New

The mobile Filter control should not be a dummy button. It should reuse the same filtering semantics as desktop:

- identity group: Hermes profiles and coding-agent runtimes;
- tag group: reusable session badges/tags;
- selected identity/tag state;
- visible session lists filtered before splitting into pinned and unpinned groups.

## Implementation notes

- Import `NDropdown` and `DropdownOption` in the mobile drawer when using the same dropdown pattern.
- Build `sessionFilterOptions`, `sessionIdentityFilterOptions`, `sessionTagFilterOptions`, `sessionFilterLabel`, and `handleSessionFilterSelect` in the mobile component or extract a shared composable if the logic grows further.
- Compute `filteredSessions = chatStore.sessions.filter(session => sessionMatchesFilters(session))`.
- Use `filteredSessions.value.filter(...)` for both pinned and unpinned computed lists.
- Empty state should key off `filteredSessions.length === 0`, not raw `chatStore.sessions.length`, so a filter with no matches shows the empty state.

## Test pattern

Add/keep a raw component contract that asserts:

- mobile drawer source contains `session-filter-button`;
- Search comes before Filter and Filter comes before New in the toolbar template;
- `:options="sessionFilterOptions"` and `@select="handleSessionFilterSelect"` exist;
- pinned/unpinned lists use `filteredSessions.value.filter`;
- the same user-facing labels (`chat.filterSessions`, `chat.filterSessionsShort`) are used.

Then run the focused session-list contract test and build before deploying live-dev.
