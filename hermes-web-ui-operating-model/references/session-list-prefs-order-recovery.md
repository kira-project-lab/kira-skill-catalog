# Session list prefs/order recovery

Use when a Hermes Web UI merge/update makes chat chronology look random, pinned sessions disappear, or session tags/badges vanish.

## Fast diagnosis

1. Verify runtime/source first:
   - `systemctl --user show hermes-web-ui.service -p WorkingDirectory -p ExecStart -p Environment --no-pager`
   - `curl -fsS http://127.0.0.1:8648/health`
   - `git log --oneline --decorate --graph -12` in the active checkout.
2. Compare data authorities, not just UI symptoms:
   - Hermes agent session authority: `<profile>/state.db`, especially `sessions`, `messages`, `messages_fts`.
   - Web UI state authority: `$HERMES_WEB_UI_HOME/hermes-web-ui.db`, especially `users`, `user_profiles`, `sessions`, `user_session_browser_prefs`.
3. For the affected user/profile, inspect `user_session_browser_prefs`:
   - `pinned_session_ids` stores pinned session IDs.
   - `overlays` stores claimed sessions and reserved metadata key `__session_badges_meta__`.
   - `__session_badges_meta__.definitions` are tag/badge definitions.
   - `__session_badges_meta__.sessions` maps session IDs to tag/badge IDs.
4. Check whether the apparently missing pinned/tagged session IDs still exist in Hermes `state.db` and whether they appear in the first page returned by the session list query.

## Common root causes

- **Data exists but projection is wrong:** Hermes `state.db` still has sessions, but Web UI list pagination/filtering/sorting excludes pinned or tagged IDs before the UI can render them.
- **Server prefs are incomplete:** pinned/tags may previously have lived in browser `localStorage` (`hermes_session_pins_v1_*`, `hermes_session_badges_v1_*`). If the new server-backed prefs row is empty, client refresh can overwrite the local cache with empty server state.
- **Conflicting sort layers:** server sorts by projected `last_active`, client maps timestamps to `updatedAt`, then components may sort pinned/unpinned again. Mixed seconds/ms or stale `last_active` can make order look random.
- **Pagination-before-claim bug:** list endpoints that over-fetch recent roots, then apply claim/profile filters and slice can omit older pinned/tagged/claimed sessions even though prefs still reference them.

## Fix pattern

- Keep the fix narrow; do not rollback a broad upstream merge unless the merge itself is unrecoverable.
- Add a regression test with: a recent unpinned session, an older pinned session, an older tagged session, stale `last_active`, and a server prefs row containing pins/badges.
- Make one authority responsible for final list order, or prove server/client comparators are identical.
- Ensure pinned/tagged IDs are explicitly hydrated into the visible list even when they are older than the current page window.
- Apply pagination after final projection/sort when possible; otherwise return a separate pinned/tagged section or hydrate missing IDs by ID.
- Add a safe localStorage-to-server backfill: if browser has non-empty pins/badges and server prefs are empty/shorter, merge into server prefs before overwriting the local cache.
- Never clear `hermes_session_pins_v1_*` or `hermes_session_badges_v1_*` as “old cache” until server prefs are confirmed to contain equivalent data.

## Recovery notes

- Pinned sessions can often be restored from `user_session_browser_prefs.pinned_session_ids`.
- Tags/badges can be restored from `user_session_browser_prefs.overlays.__session_badges_meta__` if present.
- If server tag definitions are empty but the user saw tags before, ask them to export/copy browser localStorage keys before hard-refreshing or clearing site data.
