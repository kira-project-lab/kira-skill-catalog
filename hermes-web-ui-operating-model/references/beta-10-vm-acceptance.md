# Beta-10 VM acceptance execution pattern

Use this when turning Kira beta architecture into a real VM acceptance run for Hermes Web UI / Kira runtime.

## Core lesson

Do not treat the home PC / operator machine as the beta production target. Local work is for source edits, `/tmp` smoke tests, dev/live-dev, and fallback health. Real beta-10 tenant contours belong on the chosen Yandex Cloud VM, with evidence captured in `kira-ops/docs/evidence/`.

## Reporting pitfall

Never report “goal complete” when only a document, plan, local smoke test, or intermediate artifact is complete. Say which subtask/gate is complete and name the remaining acceptance gates. For beta-10 work, “ready” requires the full acceptance checklist, not partial VM scaffolding.

## Target selection gate

Before provisioning anything:

1. Verify the intended VM from current YC credentials and inventory.
2. Treat SSH host-key mismatch as a security gate, not a nuisance.
3. Do not use `StrictHostKeyChecking=no` to bypass it.
4. If the visible YC VM differs from the documented target, stop and get/record the target decision.
5. Update docs and inventory to the chosen target before provisioning.

Example evidence fields:

```text
VM name, ID, folder, public/private IP
SSH alias used
Ansible inventory used
`./bin/kira check vm-beta-readiness` output
whether the old target is stale
```

## VM acceptance sequence

Run gates in this order:

1. G0/G1: read-only VM identity/readiness.
2. Put accepted `kira-ops` ref on VM in a safe checkout.
3. `./bin/kira validate all` on VM.
4. Provision disabled dummy tenants under `/data/kira/users/<uid>`.
5. Check Linux ownership and `0700`/`0600` permissions.
6. Run operator-path and cross-tenant negative-read checks.
7. Bring up loopback-only Web UI runtimes per tenant; do not expose public routes yet.
8. Prove Web UI auth/state separation and cross-runtime credential denial.
9. Prove dangerous Web UI/API routes deny tenant credentials.
10. Run backup/restore drill on live dummy tenant state.
11. Test disable/re-enable marker before real users.
12. Only then build Authentik/Caddy public/allowlisted route.

## Useful implementation patterns

- Keep a VM acceptance checkout separate from existing ops/runtime checkouts, e.g. `/opt/kira/repos/kira-ops-beta-acceptance`.
- If GitHub auth on VM is not configured, transfer a git bundle from the operator machine instead of copying arbitrary source trees.
- For loopback tenant runtimes, use distinct ports and tenant Linux users, e.g. `usr_test_001 -> 127.0.0.1:28648`, `usr_test_002 -> 127.0.0.1:28649`.
- Harden tenant Web UI units with `UMask=0077`, `NoNewPrivileges=true`, `PrivateTmp=true`, `ProtectSystem=strict`, `ReadWritePaths=<tenant-root>`, `ReadOnlyPaths=<webui-repo>`.
- Generated credentials must be stored tenant-owned `0600` and never printed.
- If an auth DB and credential file drift, reset only the dummy tenant intentionally, backing up old DB/token files first; do not silently overwrite real user auth data.

## Acceptance evidence must say what is still pending

Even after partial PASS, keep pending items explicit:

- public/Auth route through Authentik/Caddy;
- browser-visible login proof;
- routed API cross-tenant denial;
- Hermes chat/memory separation;
- Hermes Agent tool-loop denial;
- full auth/session disable proof;
- first real trusted beta user E2E.
