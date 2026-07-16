# Session list status taxonomy

Use when Maxim asks what statuses chat/session rows can have, or when changing the session list status dot model.

## Current ordinary chat-row source of truth

For the regular chat session list, the canonical state is server-authoritative `row_state.primary`, not the older generic `MessengerRowStatusKind` union.

Current `SessionPrimaryState` values:

| Primary state | RU label key value | Visual intent |
|---|---|---|
| `error` | `Ошибка` | red error dot |
| `needs_approval` | `Нужно разрешение` | yellow/user-action required |
| `needs_clarification` | `Нужен ответ` | yellow/user-action required |
| `stopping` | `Останавливается` | yellow/stopping |
| `running` | `В работе` | pulsing running dot |
| `queued` | `В очереди` | queued dot |
| `unread` | `Новое` | unread/new-agent-output dot |
| `idle` | `Нет действий` | quiet/read/idle; read rows should render no dot |

Server priority in `primaryFrom()`:

`error → needs_approval → needs_clarification → stopping → running → queued → unread → idle`

## Code anchors

- Server type + priority: `packages/server/src/services/hermes/session-row-status.ts` (`SessionPrimaryState`, `primaryFrom`).
- Client list-dot rendering: `packages/client/src/components/hermes/chat/SessionListItem.vue` (`statusDot`).
- RU labels: `packages/client/src/i18n/locales/ru.ts` (`rowStatus`).

## Pitfall

`MessengerRowStatusKind` / `deriveSessionRowStatusMetadata()` still contains older or cross-surface statuses such as `streaming`, `waiting`, `current`, `read`, `archived`, and `group`. Do not present those as the current ordinary chat-list status contract unless the question explicitly includes history rows, group rows, or legacy/common row-status metadata.
