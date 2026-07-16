# G12 prep-only stub cohort pattern

Use this when Maxim wants to prepare beta-10/G12 mechanics without running a real users 2–10 rollout.

## Key correction

Do not block prep-only work by asking Maxim for real user names, routing decisions, or handoff channels. If the task is preparation rather than live onboarding, generate deterministic stub tenants and run safe validation/dry-run checks.

Ask only when a step would create real external accounts, enable public access, install provider keys for live runtime, switch public routing, or onboard real users.

## Stub cohort shape

For beta-10 prep, use placeholders for rollout slots 2–10:

```text
uid: usr_stub_002 .. usr_stub_010
authentik_user_ref/web_account: beta-stub-002 .. beta-stub-010
cohort: beta-10-prep
status: planned
monthly_token_budget_usd: 2
runtime.linux_user: kira-u-stub002 .. kira-u-stub010
```

Keep all roots under `/data/kira/users/<uid>` and use `beta-10-user-restricted`.

Do not create Authentik accounts, provider keys, Web UI runtime services, or public-route access for these stubs unless Maxim explicitly changes the scope from prep-only to live rollout.

## Prep verification

Run from `kira-ops`:

```bash
./bin/kira validate tenants
./bin/kira validate all
for uid in usr_stub_002 usr_stub_003 usr_stub_004 usr_stub_005 usr_stub_006 usr_stub_007 usr_stub_008 usr_stub_009 usr_stub_010; do
  ./bin/kira tenant provision --dry-run "$uid" --base-dir /tmp/kira-g12-prep >/tmp/${uid}-dry-run.txt
done
./bin/kira check prod-surface
```

Expected evidence:

- tenant registry validates with 13 records when the two dummy tenants, `usr_polina`, and nine stubs exist;
- every dry-run provision plan stays under `/tmp/kira-g12-prep/<uid>` for local prep or `/data/kira/users/<uid>` in registry paths;
- production fallback remains `200 / 200 / 401`;
- evidence states `PREP PASS / REAL ROLLOUT NOT STARTED`.

## Reporting rule

For prep scope, align wording to Maxim's accepted scope:

- If Maxim says G12 should count as closed because only preparation/stub checks were in scope, say: `G12 is closed for the agreed prep/stub scope.`
- Still keep the factual caveat close by: `real users 2–10 were not onboarded/live-tested.`
- Do not block prep work by asking for real user lists, budgets, routing decisions, or handoff channels; use deterministic stubs and `$2/month` unless live rollout begins.

Do not say: `users 2–10 onboarded`, `real rollout complete`, or `multi-user concurrent routing proven` unless the live per-user checklist has actually run with real/approved accounts.
