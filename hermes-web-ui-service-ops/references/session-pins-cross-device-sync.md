# Server-backed session pins: cross-device sync pitfalls

Use this when implementing or reviewing Hermes Web UI pinned-session persistence across windows, devices, or profiles.

## Root cause pattern found

A server-backed pin feature can still fail cross-device sync if the client stores pins under the **current active profile** instead of the **profile that owns the pinned session**.

Observed failure shape:

- Session row: `sessions.id = mpzcx71fghxx19`, `sessions.profile = kira`.
- Pin preference row: `user_session_browser_prefs.profile_name = default`, `pinned_session_ids = ["mpzcx71fghxx19"]`.
- A second device opened profile `kira`, requested pins for `kira`, got `[]`, and showed no pin.

## Design rules

1. Treat a pin as state on `(user, session_id)` or `(user, session_profile, session_id)`, not on a browser's transient active profile.
2. On pin/unpin, derive the profile from the session object or server-side session lookup, not from `activeProfileName` / `localStorage`.
3. Prefer server APIs like `PUT /sessions/:id/pin` and `DELETE /sessions/:id/pin` that validate the session and profile server-side.
4. If storing grouped arrays by profile, the server should verify that every pinned session belongs to that profile or migrate it to the owning profile.
5. Do not let a client with a partial session list prune and overwrite server pins. Local pruning is acceptable for display; server deletion should happen only on explicit unpin or confirmed session deletion.
6. When implementing confirmed deletion cleanup, wire every server-side deletion path that can actually remove a session: direct delete, batch delete, and deferred/GC delete if present. The cleanup should remove the deleted session ID from all user/profile pin buckets.
7. Hydrate profile selection before loading profile-scoped preferences, or make the preference API profile-agnostic and return pins for all profiles visible to the user.

## Regression tests to add

- With no `hermes_active_profile_name` in localStorage, pin a session whose row has `profile = 'kira'`; assert server stores/returns it for `kira`, not `default`.
- Load a second client/device with active profile `kira`; assert the pinned session appears as pinned after server hydration.
- Load a fresh client whose active profile is still `default` but whose visible session list contains `profile = 'kira'`; assert the client hydrates the `kira` pin bucket from the server before rendering pinned state.
- Load a client with an incomplete/filtered session list; assert it does not delete server pins through automatic pruning.
- If user scoping is required, assert pins are isolated by `user_id` but consistent across devices for the same user.

## Client hydration pitfall

Fixing the write path is not sufficient. If the pin store only fetches the active profile bucket on startup, a fresh phone can still render a visible `kira` session as unpinned while the active profile fallback is `default`. When the session browser/history list loads sessions, collect the distinct `session.profile` values in the visible list and refetch those pin buckets without changing the active profile. Same-window invalidation should also refetch the affected profile bucket rather than copying another tab's local state.

## Debug probes

When a report says “pin did not sync to phone,” first identify the SQLite file actually opened by the running backend process. Do not rely only on service environment variables or expected state directories; in dev/live-dev, runtime config can drift. Use the listener PID/systemd MainPID and inspect open files when needed, then query that DB.

Inspect:

```sql
SELECT id, profile, title FROM sessions WHERE id = ?;
SELECT user_id, profile_name, pinned_session_ids, updated_at FROM user_session_browser_prefs;
```

If the pinned session's `sessions.profile` differs from the prefs row `profile_name`, the bug is profile binding, not mobile rendering.