# Participant platform UX pattern

Use when reviewing or designing hackathon / competition platform navigation for participant-facing flows, especially OrangeHack-style products.

## Core principle

Participant navigation should follow the participant journey, not organizer data entities.

Organizer consoles can expose entity panels (`settings`, `cases`, `invitations`, `teams`, `submissions`, `certificates`) because organizers manage objects. Participants usually need a compact product path:

1. find or join a competition;
2. understand participation status;
3. open/create/join a team;
4. select/open a case;
5. submit final materials;
6. check results, achievements, and certificates.

## Recommended participant nav

Prefer a short nav:

- `Соревнования` / `Competitions` — catalog, filters, invite-code entry, new participation.
- `Моё участие` / `My participation` — participant home and current work summary.
- `Профиль` / `Profile` — personal data, achievements, public profile settings.
- `Сертификаты` / `Certificates` — optional top-level item only if certificates are a frequent standalone task; otherwise surface them inside `Моё участие` and `Профиль`.

Avoid participant top-level items for context-bound entities:

- `Команды` as a global section, unless there are cross-competition team management tasks.
- `Кейсы` as a global section, because cases belong to a competition/team context.
- `Решения` as a global section, because submission belongs to a case; expose it as a CTA/status.
- A visible `Dashboard` item if the page is only a placeholder. Either remove it or make it a real participant home and label it by user value (`Моё участие`).

## Participant home contents

A real `Моё участие` page should answer: “what should I do next?”

Useful cards:

- active competitions;
- team name, role, captain/member state;
- selected case / case selection needed;
- next deadline;
- submission status: not started, draft/final submitted, locked, needs update;
- pending join requests / invite state;
- certificate status and download/generation action;
- completed competition history and achievements.

Primary CTAs should be contextual:

- `Открыть кейс`;
- `Открыть команду`;
- `Выбрать кейс` for captain;
- `Отправить решение`;
- `Скачать сертификат`.

## Review checklist

When auditing participant UX completeness, check:

- Does every nav item lead to a real useful outcome, not a disabled placeholder?
- Is the desktop nav consistent with mobile bottom nav?
- Are organizer-only entity panels absent from participant navigation?
- Are team/case/submission actions reachable from the competition/case context?
- Is the participant home built around next action and status, not generic stats?
- Are deprecated routes redirected without becoming visible nav destinations?
- Does copy describe the user's goal (`Моё участие`) rather than implementation terms (`Dashboard`)?

## Implementation correctness checks

For OrangeHack Platform code changes, treating the participant UX wording as “correct” means more than changing visible Russian text in one component:

- Keep participant-facing strings in locale JSON files for both `ru` and `en`; do not leave new Russian literals in React components, hooks, or model helpers.
- If a dashboard/helper currently returns user-facing labels from pure model logic, either return locale-independent state/kinds or pass localized copy from the UI layer; do not hardcode Russian fallback text in `deriveNextAction`, checklist builders, deadline builders, or aggregation hooks.
- After migrating hardcoded copy into locale files, run the hardcoded-copy check. If it reports stale allowlist entries because literals were removed intentionally, update the allowlist and rerun the check rather than leaving the gate red.
- Add a regression test that switches locale or mocks `next-intl` messages to prove dashboard chrome renders from locale keys, not embedded Russian strings.
- Validation for this class of fix should include focused dashboard tests, frontend typecheck, i18n/copy check, frontend architecture check, and the frontend test suite when practical.

## OrangeHack session note

In the OrangeHack Platform review, the useful distinction was:

- organizer: needs multiple console panels because they manage competition entities;
- participant: needs fewer top-level panels and stronger contextual CTAs.

The concrete critique was that public/participant nav exposed `Соревнования` and a placeholder `Дашборд`, while real participant functions lived across competition, team, case, profile, and certificate pages. The recommended correction was to turn `/dashboard` into `Моё участие` or remove it from nav until it becomes real, add `Профиль` to desktop nav for parity with mobile, and not add global `Команды` / `Кейсы` / `Решения` panels.