# Session row status layer removal

Use this when removing or redesigning Hermes Web UI chat/session row statuses.

## Durable distinction

Separate two layers before editing:

1. Fork row-status / dot layer — removable or replaceable for a clean redesign.
   - `row_status` API fields
   - `rowStatus` client/store fields
   - `MessengerRowStatus.vue`
   - `messenger-row-status.ts`
   - `api/hermes/row-status.ts`
   - `messengerRowStatus.*` locale keys
   - dot-specific client tests such as `messenger-row-status.test.ts` and `row-status-metadata.test.ts`
2. Ekko/live-state chat runtime logic — do not delete as part of dot cleanup.
   - active run / streaming / `isWorking`
   - queue lengths and queued user messages
   - pending approvals / pending clarifies
   - run handlers and socket lifecycle events
   - message-list read/receipt behavior unless the task explicitly targets it

## Removal workflow

1. Read the governing ADR first; keep the implementation inside that scope.
2. Build a repo-wide removal inventory with searches for at least:
   - `row_status`
   - `rowStatus`
   - `MessengerRowStatus`
   - `messengerRowStatus`
   - `markSessionRead`
   - `setSessionRuntimeStatus`
   - `setSessionReadMarker`
   - `last_read_message_id`
   - `last_read_at`
   - `status_kind`
   - `status_reason`
   - `status_updated_at`
   - `latest_relevant_message_id`
3. Delete dot-specific components/helpers/tests/locales together, not piecemeal.
4. Keep upstream/live-state code intact unless the ADR explicitly says otherwise.
5. Update session-list tests to assert the baseline without status-dot rather than encoding the removed behavior.
6. Re-run targeted client/server tests and `npm run build`.
7. Run the search inventory again and expect zero source matches for the removed layer. If docs/ADR intentionally mention historical terms, distinguish those from code matches in the final report.

## Pitfalls

- Do not treat `MessageList.vue` read receipts as the same thing as session-list status dots. They can share vocabulary but are different surfaces.
- Do not remove runtime status helpers from run-chat handlers just because their names resemble row-status fields; first prove they are part of the fork dot layer.
- Do not report full test-suite failures as caused by this task without checking whether they are existing environment/config failures.
