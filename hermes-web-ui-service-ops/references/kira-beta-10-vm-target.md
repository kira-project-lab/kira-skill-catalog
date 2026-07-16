# Kira beta-10 runtime target: Yandex VM, not home PC

Use this when working on Kira beta-10, multi-user contours, tenant provisioning, or `/data/kira/users/<uid>`.

## Durable decision

Live beta-10 access targets the Yandex Cloud VM contour. The architectural/provider name may be `kira-app-01`, but before execution verify the actual running VM from live YC inventory and SSH aliases (for example a current VM may be `kira-main-ops-01` with a different public IP). Do not rely on stale docs, generated Ansible inventory, or old IPs as identity proof.

The home PC / `werserk-tachka` / current `pc` is a development, operator, fallback, and temp-smoke surface. Do not treat it as the live multi-user beta host.

## Practical rule

- Local/home PC work is allowed for source edits, `kira-ops` scripts, docs, dev/live-dev Web UI, read-only health checks, and temp-only smoke tests under `/tmp`.
- Real beta tenant roots such as `/data/kira/users/<uid>` belong on `kira-app-01`.
- Do not run live tenant provisioning on the home PC unless Maxim explicitly asks for a local staging experiment.
- If a previous local `/data/kira/users/<uid>` attempt exists in notes, treat it as a staging/blocked attempt, not as the target path for beta-10.

## Required sequence for beta-10 tenant work

1. Keep `app.kiraproject.ru` protected as PC fallback.
2. Resolve the actual VM target from live YC inventory plus SSH alias evidence: VM name, ID, public IP, hostname, login user, and Git/runtime paths.
3. Confirm VM identity and SSH/Ansible access. A host-key mismatch is a security gate, not a nuisance.
4. Run a read-only VM readiness probe before mutating VM state.
5. Deploy or update `kira-ops` on the VM as the source of operational scripts.
6. Run live tenant provisioning only on the VM.
7. Record evidence under `kira-ops/docs/evidence/`.

If a command is blocked by the runtime as destructive or consent-gated, stop immediately and report the exact intended path/action. Do not retry, rephrase, or attempt the same outcome through bundle/scp/ssh workarounds until the user explicitly confirms that exact mutation.

## Host-key pitfall

If SSH/Ansible reports `REMOTE HOST IDENTIFICATION HAS CHANGED`, do not bypass with `StrictHostKeyChecking=no`.

Verify the new host key through Yandex Cloud console/CLI or another trusted channel, then update `known_hosts` deliberately. Only then continue to tenant provisioning.

## Evidence language

Do not say multi-user beta is configured if only local docs, temp smoke tests, or scripts exist. Say exactly what passed: local tooling smoke, VM readiness probe, live VM tenant provisioning, or browser-facing acceptance.
