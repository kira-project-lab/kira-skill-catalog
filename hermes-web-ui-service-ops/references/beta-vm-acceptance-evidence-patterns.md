# Beta VM acceptance evidence patterns

Use when executing Hermes Web UI beta/cohort acceptance on a VM target, especially when moving from dummy tenant gates to a real trusted beta user.

## Repeatable negative matrix pattern

When a one-off browser/API negative check proves useful, convert it into a repo-owned smoke command before treating the gate as stable. The useful shape is:

1. Keep the smoke tenant-scoped and credential-safe: read tenant acceptance credentials from the tenant root without printing them.
2. Include positive controls so the tenant is known to be authenticated and usable:
   - `GET /api/auth/me -> 200`
   - `GET /api/hermes/profiles -> 200`
   - `GET /api/hermes/sessions?profile=<allowed> -> 200`
3. Include denied controls in the same run:
   - profile switching by path and query;
   - header-forced profile switching, e.g. `X-Hermes-Profile`;
   - config and credentials mutation;
   - MCP tools/reload;
   - provider/model mutation;
   - coding-agent install/run;
   - profile restart/session access for operator-like profiles.
4. Emit sanitized JSON with only method/path/status and a `bad: []` list; do not persist tokens, cookies, passwords, provider keys, or full response bodies.
5. Run the smoke on the VM acceptance checkout after syncing the exact Git ref, not only on the operator machine.
6. Record an evidence note that distinguishes: positive controls, denied controls, result, VM target, Git ref, and remaining gates.

## G10/G11 transition pattern

After dummy-tenant G10 passes, do not overclaim beta readiness. The next durable artifact should be a G11 real-user E2E checklist/runbook that names the required user/account input and stop conditions. This is useful even when G11 itself is blocked by missing real beta identity.

A G11 runbook should cover:

- production guard before/after;
- VM checkout Git ref and validation;
- tenant UID/auth binding/provider cap;
- browser-visible chat, memory recall, read-only research, upload summary, note write;
- repeatable negative matrix for the real tenant;
- backup/restore manifest or live drill;
- disable/re-enable with active-session denial;
- sanitized evidence paths and explicit residual risks.

## Reporting rule

When the dummy tenant gates pass but G11 is not run, report the state as: `dummy-tenant gates strengthened; full beta-10 still blocked on real trusted beta user identity/account and onboarding approval`.