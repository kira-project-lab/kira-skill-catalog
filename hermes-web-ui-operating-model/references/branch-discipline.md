# Hermes Web UI branch discipline

Session-derived workflow correction from Maxim.

## Rule

When work may change `/home/werserk/2-kira/hermes-web-ui`, do **not** edit `main` or `dev` directly.

Use a separate task/feature branch before making code, docs, or config changes in that checkout.

## Default assumption

For beta-10 VM acceptance or Kira ops work, changes to the `hermes-web-ui` repo are usually unnecessary. Prefer proving/adjusting the VM/runtime/ops layer first. Touch Web UI only when the acceptance issue is actually in Web UI source.

## Practical sequence

1. Re-check the current checkout and branch with `git status --short --branch`.
2. If the target is `/home/werserk/2-kira/hermes-web-ui` and branch is `main` or `dev`, create a dedicated branch before edits.
3. If changes are not clearly needed in Web UI source, stop and keep the repo read-only.
4. Report which repo/branch actually received edits; avoid vague “worked in Web UI” phrasing when multiple checkouts were inspected.

## Pitfall

Do not treat “I only need to inspect prod/main” as permission to patch it. Inspection is fine; edits require a task branch unless Maxim explicitly overrides this rule.
