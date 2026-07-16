# OrangeHack local validation accounts

Use this when validating OrangeHack Platform participant/admin screens in local dev.

## Goal

Create durable local-only accounts so Kira can test participant and admin journeys through the real browser instead of anonymous API probes.

## Pattern

1. Create a participant account and an admin account in the local backend DB.
2. Document credentials as **public local validation fixtures** in the repo when Maxim wants agents to reuse them. Use one canonical runbook, e.g. `docs/runbooks/local-validation-accounts.md`, and link to it from `AGENTS.md`, `DEVELOPMENT.md`, docs index, demo-data runbook, and security policy.
3. Make the safety boundary explicit:
   - local/dev only;
   - not for stage/prod/customer demos/shared external environments;
   - treated as public fixtures, not secrets;
   - if DB reset removes rows, recreate the same fixture accounts.
4. Give the participant a real local participation context:
   - private visible competition;
   - activated invite code bound to participant email;
   - team membership, preferably captain for dashboard coverage;
   - selected case with materials and submission window.
5. Give the admin account RBAC access through the normal authz path:
   - ensure auth permissions/roles are seeded;
   - create an email-based `auth_role_assignments` row for `super_admin`;
   - let `materialize_email_role_assignments_to_user()` create the deterministic user-based assignment.

## Important RBAC pitfall

Do not create an arbitrary direct user assignment for the same role/scope when the resolver will also materialize an email assignment. The resolver uses a deterministic id based on `user_id:role_id:scope_type:scope_id`; a second user assignment for the same `(subject_type, subject_id, role_id, scope_type, NULL scope_id)` can trip the unique index and make `/api/admin/me` fail.

Safer local setup:

- keep the email assignment as the source row;
- delete any ad-hoc direct row such as `kira-local-admin-<user_id>`;
- call/materialize through the resolver or hit an admin endpoint after login.

## Verification gates

API gates:

- participant `POST /api/auth/login` returns `200`;
- admin `POST /api/auth/login` returns `200`;
- participant `GET /api/auth/me` returns `200`;
- participant `GET /api/competitions/my` returns `200` and includes the validation competition;
- participant `GET /api/certificates/my-competitions` returns `200`;
- admin `GET /api/admin/me` returns `200`.

Browser gates:

- login as participant;
- open `/ru/dashboard`;
- verify the dashboard shows the validation competition, team, and selected case;
- login as admin in an isolated browser context;
- verify `Админка` and `Консоль` appear in navigation.

If a protected participant endpoint returns `404` while the user is logged in, treat that as a product/API gap to fix, not as successful account setup.
