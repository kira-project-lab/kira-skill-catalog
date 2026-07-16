# Kira YC production-readiness planning

Use when Maxim asks to move Kira on Yandex Cloud from VM preview/beta to fully production-ready primary contour.

## Readiness states to keep separate

Do not collapse these into one “ready” claim:

1. **Repo controls ready** — scripts, IaC, runbooks, secret schemas, and evidence are committed.
2. **Main VM converged** — `kira-main-ops-01` runs the latest repo-owned runtime and passes health/isolation/backup/restore/egress checks.
3. **Fresh rebuild proven** — a disposable VM can be provisioned from repo + Lockbox + explicit backup and pass the same gates, including Authentik restore.
4. **Browser acceptance complete** — real accounts log in, see their own Kira instance, send messages, persist sessions, and fail cross-tenant access attempts.
5. **Operational readiness complete** — monitoring, alerting, logs, SLOs, incident runbooks, and rollback are tested.
6. **Production cutover complete** — `app.kiraproject.ru` points to the VM and duplicate home-PC processing is retired/demoted after approval and bake.

A safe wording before cutover is usually: “VM preview is ready for closed beta on `app.vm.kiraproject.ru`; production primary is pending browser acceptance, fresh rebuild proof, observability, and approved cutover.”

## Recommended phase order

1. **Baseline evidence**: source commit, deploy run, VM inventory, DNS/routes, health, backup validator, restore-smoke, tenant isolation.
2. **Source/runtime drift**: distinguish `/opt/kira/repos/kira-ops` source from `/opt/kira/ops` deployed runtime copy; add a drift checker or manifest allowlist rather than relying on manual `git status` interpretation.
3. **Security/IAM/network**: Lockbox access bindings, generated secret file modes, SSH alias/key path, security groups, public listeners, internal-vs-public decision for agentmemory/memory hostnames.
4. **Browser acceptance**: real Authentik/Web UI login for `werserk`, `sonya`, `polina`; visible assistant label `Кира`; account→instance mapping; chat send; reload persistence; console check; negative tenant access tests.
5. **Functional smoke**: Web UI send path through actual runtime, Paperclip, agentmemory, Codex CLI/egress, gateway-disabled state.
6. **Fresh VM rehearsal**: paid/approval-gated disposable VM; clone/bootstrap from repo without operator rsync; restore an explicit dated backup; include Authentik artifact; run health/isolation/browser checks; delete or document retained VM.
7. **Observability/SLOs**: alerts for service down, route failure, stale backup, restore-smoke failure, disk, Lockbox sync, Codex egress, Authentik route; log retention and incident runbook.
8. **Load/latency**: low-concurrency browser/API/provider tests, VM-vs-PC comparison only as diagnostic control, resize decision with cost if needed.
9. **Cutover dry-run**: DNS owner/TTL, Host-header or local-resolve probe for `app.kiraproject.ru`, cert readiness, rollback commands.
10. **Approved cutover and bake**: move DNS only after Maxim approval, smoke all target users, retain PC fallback for 24–72h, then decide demotion/rollback.

## Runtime drift gate pattern

For Kira YC production-readiness, do not use raw `git status /opt/kira/ops` as the cleanliness gate. `/opt/kira/ops` is an executable runtime copy and may contain legacy or generated top-level material. Instead, compare the source-of-truth checkout (`/opt/kira/repos/kira-ops`) to the repo-owned mirrored roots that the deploy script actually syncs, for example `scripts`, `templates`, `runbooks`, `config`, `deploy`, and `systemd/user`, with the root list declared in `deploy/runtime-manifest.yaml`. Wire this checker into deploy immediately after runtime sync and before health checks, so production cleanliness becomes machine-checkable and no one has to interpret noisy runtime git state manually.

## User timer privilege pitfall

Kira VM user timers may run as the `kira` systemd user, while their scripts perform root-required checks: tenant isolation uses `runuser`, assistant-instance checks traverse private tenant roots, backup reads root-owned service artifacts, and restore-smoke may need to clean root-owned smoke workdirs. If a timer fails with `runuser: may not be used by non-root users` or `Permission denied` under `/data/kira/users`, `/opt/kira/services`, or `/tmp/kira-restore-smoke`, fix the unit rather than weakening permissions: run the specific ops script through passwordless sudo from the user unit, then `daemon-reload`, `reset-failed`, manually start the service, and verify `systemctl --user --failed` is empty. Avoid forcing an extra full backup just to test the backup timer when disk is already tight; verify the sudo-read path and let the next scheduled backup exercise the same unit.

## Password reset for browser testing

If browser acceptance is blocked by missing credentials, use the VM test-access password reset flow rather than asking for old passwords. Generate temporary passwords, reset Authentik/Web UI accounts, verify natively, report only temporary values to Maxim, and mark them for rotation. Never commit temp credentials or hashes.

## Production readiness master gates

- `kira-ops` source clean and deployed from `origin/main`.
- VM repo and runtime manifest match the expected commit.
- Runtime drift checker PASS or documented generated-only drift.
- Lockbox check PASS; secret files `0600`; no placeholder fallback secrets.
- Security groups/public listeners audited.
- `check-kira-vm-health.sh` PASS.
- `check-kira-vm-backup.py --require-authentik` PASS.
- `restore-kira-vm-smoke.sh` PASS.
- `restore-kira-vm-state.sh --dry-run --require-authentik` PASS.
- Fresh disposable VM rebuild PASS with no blocking caveats.
- Browser acceptance PASS for all target users.
- Friend tenant negative isolation PASS through browser/runtime path.
- Web UI send, Paperclip, agentmemory, and Codex egress smokes PASS.
- Monitoring/alerts/timers PASS.
- `docs/00-status.md` is current and evidence-linked.
- Cutover dry-run PASS.
- Maxim explicitly approves production DNS/gateway cutover.
- Post-cutover bake PASS before PC fallback is demoted.

## Cutover boundaries

- Do not move `app.kiraproject.ru` while still planning or testing.
- Do not enable VM Telegram gateway while the PC gateway is active unless executing the approved gateway cutover.
- Treat fresh VM creation, destructive restore, DNS cutover, gateway cutover, and password reset as approval-gated execution steps.
- Keep evidence redacted: no `.env`, Lockbox payloads, OAuth tokens, hashes, or Telegram IDs.
