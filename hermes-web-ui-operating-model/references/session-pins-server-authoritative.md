# Server-authoritative session pins

Use this reference when designing, reviewing, or debugging Hermes Web UI session pinning/favorites/bookmarks across tabs, devices, or restarts.

## Durable contract

Session pins are a durable user preference, not a browser-local UI tweak.

Authoritative state should be server-side and scoped by:

- authenticated `user_id`;
- the real `profile` of the pinned session.

LocalStorage may be used only as a display/cache optimization. It must not be the durable source of truth for cross-device behavior.

## Pitfalls found in session-pin sync work

### Do not derive durable pin profile from active client profile

Avoid this pattern for writes:

```ts
activeProfileName || localStorage.getItem('hermes_active_profile_name') || 'default'
```

On a fresh device, profile hydration can lag behind session-browser mounting. A visible `kira` session can then be pinned into the `default` bucket.

Preferred mutation shape:

1. client sends `sessionId` for pin/unpin;
2. server authenticates user;
3. server loads the session row;
4. server derives `profile_name` from `session.profile`;
5. server updates the user prefs row for that profile.

The client may provide a profile hint for routing/optimization, but the server should not trust it as the source of truth.

### Do not sync destructive prune from partial client lists

A current session list is not proof that absent pinned IDs were deleted.

Unsafe pattern:

```ts
pruneMissingSessions(currentlyLoadedSessionIds)
// then PUT reduced pinned_session_ids back to server
```

Absence can be caused by profile filters, async loading, search/list limits, stale state, or a fresh device. Only confirmed session deletion, explicit user unpin, or a controlled migration should remove server pins.

### Cross-device sync should use server-pushed invalidation after persistence is correct

Correct persistence model comes before push mechanics, but durable pins should feel live across devices once the server-authoritative contract is in place.

Implementation pattern used in Hermes Web UI:

- local mutation writes to the server first;
- server emits a user-scoped Socket.IO invalidation event after `pin`/`unpin`/bulk update;
- clients subscribed to the prefs-events namespace refetch the affected profile bucket;
- same-browser `BroadcastChannel`/`storage` remains a fallback/fast path for tabs in one browser;
- event payloads should be invalidation hints, not replicated mutable pin arrays.

### Clean up pins only on confirmed deletion

Server-authoritative pins should survive incomplete client views, but they should not outlive confirmed session deletion forever.

When a session is deleted through a server-confirmed path, remove that session ID from all user/profile pin buckets. Cover direct delete, batch delete, and deferred/GC delete paths if the app has more than one deletion mechanism. Do not implement this as client-side list pruning; deletion cleanup belongs to the server path that knows the session was actually removed.

### Treat pin arrays as manual order, not just membership

The order of `pinned_session_ids` is user-authored UI state. Do not sort pinned sessions by `updatedAt`, `lastActiveAt`, or title after pinning; only unpinned/ordinary session lists should keep time-based sorting.

Implementation pattern used in Hermes Web UI:

1. render pinned rows by the server/cache `pinned_session_ids` array order;
2. use time sorting only as a fallback for pinned sessions missing from the array during hydration or recovery;
3. allow reordering only among pinned sessions in the same real profile bucket;
4. persist reorder with the bulk `PUT /api/hermes/session-browser-prefs/pins` endpoint using `{ profile, pinned_session_ids }`;
5. optimistically update the local cache, then apply the server response or roll back/refetch on failure;
6. keep History/read-only surfaces consistent by respecting the same manual order even if only the chat sidebar exposes drag-and-drop.

Regression tests should prove both contracts: pinned rows are not wrapped in `sortSessionsWithActiveFirst(...)`, and drag/drop calls the prefs store reorder path rather than changing only local DOM order.

## Debugging checklist

When a pin does not appear on another device:

1. Identify the exact session ID.
2. Check the session row's real `profile`.
3. Check server prefs rows by `user_id + profile_name`.
4. Look for a mismatch: pinned ID under `default` while session belongs to `kira` or another profile.
5. Check whether a client-side prune path wrote `[]` or a truncated list after a partial session load.
6. Verify the two devices use the same authenticated user and profile visibility.

## Migration / reconciliation requirement

When replacing a broken active-profile-based implementation, do not only fix future writes. Existing rows may already contain pins under the wrong profile bucket, for example `default` containing a session whose `sessions.profile` is `kira`.

Preferred repair pattern:

1. On server read/mutation, reconcile the user's pin rows against the canonical `sessions` table.
2. For each pinned ID with an existing session row, move the ID from the stored bucket to `session.profile` if they differ.
3. Preserve unresolved/orphaned IDs unless there is a confirmed session deletion path; do not treat absence from a client list as deletion.
4. Add a regression test that seeds a mismatched row and proves reading the real profile returns the pin and the old bucket is emptied.

This closes the “new code works, old bad state still fails on the phone” gap.

## Implementation refinement rules

### Keep explicit unpin separate from deletion cleanup

Do not use the same client method for two different intents:

- **Explicit user unpin** should optimistically update local state and call the session-based unpin API.
- **Confirmed session deletion cleanup** should remove the ID from local pin cache/UI only; the server deletion path already owns durable cleanup.

If deletion cleanup calls the unpin API after the session was deleted, it can create avoidable 404s, noisy refreshes, and misleading error logs. Add a regression test that deleting/cleaning a pinned session does not call `unpinSession()`.

### Keep prefs-event sockets user-scoped, not active-profile-scoped

The `/session-prefs` live invalidation channel should authenticate the user and join a user room. Do not bind socket connection identity to the current active profile when the payload already names the affected profile. Active profile is a UI view filter, not the resource identity for cross-device preference invalidation.

### Treat socket event payloads as invalidation hints

Do not replicate full mutable pin arrays over the event stream. Payload should be minimal: profile, optional session ID, reason, timestamp. The receiving client refetches the affected profile bucket from the server source of truth. Avoid leaking internal routing keys such as `userId` to the browser payload when the socket room already enforces user scope.

### Keep compatibility APIs clearly secondary

A legacy/bulk `PUT /pins` endpoint can remain for compatibility or migration tests, but the client-facing steady-state API should prefer session-based `POST/DELETE /pins/:sessionId`. Remove unused client helpers for compatibility endpoints so new call sites do not accidentally revive active-profile-based writes.

## Regression tests to require

- Fresh device with no `hermes_active_profile_name` pins a `kira` session; server stores it under `kira`, not `default`.
- Existing mismatched server rows are reconciled from the wrong bucket to the session's real profile.
- Loading an incomplete session list must not overwrite remote pins with `[]`.
- Explicit unpin removes from the profile bucket derived from the session row.
- Confirmed session deletion removes the deleted session ID from all user/profile pin buckets through every server-side deletion path: direct delete, batch delete, and deferred/GC delete when present.
- Client-side deletion cleanup removes the pin from local cache/UI without calling the unpin API.
- Server push emits a user-scoped invalidation event after pin/unpin/update, and another client refetches the affected profile bucket.
