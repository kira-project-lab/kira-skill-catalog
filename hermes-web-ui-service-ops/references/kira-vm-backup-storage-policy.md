# Kira VM backup storage and retention policy

Use when Kira YC/VM disk usage grows because of `/data/kira/backups`, backup timers, restore-smoke artifacts, or backup/archive storage design.

## Diagnosis pattern

First separate the real storage layers:

- `/data/kira` may be on the root disk, not a dedicated data disk. Verify with `df -h / /data/kira` and `findmnt / /data/kira`.
- Measure both `/data/kira` and `/opt/kira`; backups may not be the only large consumer.
- Expected large classes seen on Kira VM:
  - `/data/kira/backups` — VM/full backup archives;
  - `/data/kira/profiles/kira/home/.cache/huggingface` — rebuildable cache;
  - `/data/kira/profiles/kira/home/.npm` — rebuildable npm/npx cache;
  - `/opt/kira/github-runners/*` — runner work/externals;
  - `/opt/kira/services/*/node_modules` — rebuildable service dependencies.

Useful read-only probes:

```bash
ssh kira-yc 'df -h / /data/kira; findmnt / /data/kira || true'
ssh kira-yc 'sudo du -xh --max-depth=2 /data/kira | sort -h | tail -40'
ssh kira-yc 'sudo du -xh --max-depth=2 /opt/kira | sort -h | tail -40'
ssh kira-yc 'sudo find /data/kira/backups -maxdepth 2 -type f -printf "%s %p\n" | sort -n | tail -30 | numfmt --field=1 --to=iec-i --suffix=B'
```

## Policy verdict

Do not solve backup bloat only by growing the root disk. Use a layered policy:

1. **Local working data disk**: attach a separate YC `network-hdd` disk for `/data/kira` (default target: 256 GiB). Prefer this over root resize because data becomes easier to migrate, snapshot, attach to a replacement VM, and monitor separately.
2. **Local retention window**: keep only fast rollback material locally.
3. **Object Storage archive**: copy older backups to a bucket with lifecycle rules and a cheaper storage class.
4. **Exclusions**: do not back up rebuildable caches/dependencies as state.

## Local backup frequency guard

Backups should be scheduled at most once per day. The backup script should refuse to run if the latest validated backup is younger than roughly 20–23 hours, unless an explicit override is passed.

Recommended behavior:

- default schedule: once daily, e.g. `03:10 UTC`;
- deploy scripts must **not** create a fresh backup automatically when `latest-vm` is missing or incomplete; in recovery mode they should report `BACKUP_SUSPENDED` and run health with an explicit maintenance flag instead of filling the disk again;
- allow deploy-time backup creation only behind an explicit operator flag such as `KIRA_DEPLOY_CREATE_BACKUP=1`;
- allow emergency manual backup only with an explicit `--force --reason <text>` or environment equivalent;
- health should check backup freshness (`latest valid age < 30h`) and completeness, but it must distinguish `BACKUP_SUSPENDED` from both `PASS backup` and unexpected `FAIL backup`.

## Disk-full recovery route pitfall

After deleting bloated `/data/kira/backups`, do not assume route `502` will clear by itself. Docker containers that tried to start while the disk was full can keep stale container state such as:

```text
failed to mount ... no space left on device
```

In the 2026-06-27 Kira VM recovery, public routes stayed `502` because Caddy could not resolve/reach `authentik-server:9000`: the `authentik-server` container looked present but was stuck with a stale mount failure. The fix was to recreate only that container after freeing disk:

```bash
cd /opt/kira/compose/ops
sudo docker compose --env-file /opt/kira/compose/ops/.env up -d --force-recreate --no-deps authentik-server
```

Then verify from both inside Caddy and outside:

```bash
docker inspect -f 'status={{.State.Status}} health={{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' kira-ops-authentik-server-1
docker exec kira-ops-caddy-1 sh -lc 'wget -S -O /dev/null --timeout=5 http://authentik-server:9000/-/health/live/'
for u in https://auth.kiraproject.ru/ https://app.vm.kiraproject.ru/ https://paperclip.vm.kiraproject.ru/; do curl -skI --max-time 8 "$u" | head -1; done
```

Use targeted `--force-recreate --no-deps` before broad stack restarts when only one upstream is stale; this preserves the rest of the preview contour.

## Local retention

Safe default:

- keep current valid `latest-vm`;
- keep one previous known-good daily backup;
- delete incomplete/failed backup directories older than 12 hours;
- after Object Storage archive is verified, delete local older daily backups;
- never delete the only valid Authentik-containing backup until a newer full backup and restore-smoke have passed.

## Remote/Object Storage retention

Use Object Storage for longer history, not the VM filesystem.

Suggested tiers:

- daily backups: 7–14 days in `cold` storage;
- weekly backups: 4–8 weeks in `cold` storage;
- monthly backups: 3–6 months; `ice` only if you are comfortable with the 12-month minimum-billable-storage penalty;
- do not use `ice` for short-lived daily backups that may be deleted within a year.

## Backup exclusions

State backup should include durable app/user/runtime state, not rebuildable build caches.

Exclude or split out:

```text
node_modules/
.pnpm-store/
.npm/_npx/
.npm/_cacache/
.cache/huggingface/
.cache/google-chrome/
.github-runner/_work/
.git/objects if source is already in Git and repo clone is part of rebuild
```

Include:

```text
/data/kira/users
/data/kira/profiles minus rebuildable caches
/data/kira/workspaces
/data/kira/state durable DB/session/upload state
Authentik postgres dump and manifest
ops runtime manifests, schema, and repo commit refs
Lockbox secret IDs/key schema references, not payload values
```

## YC disk sizing guidance

Use the YC Compute calculator for live prices. A recent calculation for the Kira VM showed approximate monthly disk costs:

- 80 GiB `network-hdd`: ~276 RUB/month;
- 256 GiB `network-hdd`: ~885 RUB/month;
- 256 GiB `network-ssd`: ~3668 RUB/month.

Therefore, for `/data/kira` backups/state, prefer **256 GiB `network-hdd`** unless latency evidence says otherwise. SSD is not justified for cold backups.

## Migration shape for `/data/kira`

Approval-gated because it is paid infrastructure and mount migration:

1. Create disk, e.g. `kira-main-data-01`, `network-hdd`, 256 GiB, same zone as VM.
2. Attach to `kira-main-ops-01`.
3. Format and mount temporarily.
4. Stop or quiesce services that write to `/data/kira`.
5. `rsync -aHAX --numeric-ids /data/kira/ <new-mount>/`.
6. Move old `/data/kira` aside, mount new disk at `/data/kira`, update `/etc/fstab` by UUID.
7. Start services and verify health, backup validator, restore-smoke, tenant isolation, Web UI/Paperclip/agentmemory health.
8. Keep old copy briefly; remove only after a bake window and a fresh validated backup.

## Emergency deletion / backup suspension

If Maxim explicitly asks to delete `/data/kira/backups` and pause backup creation, do it as an emergency storage-recovery operation, then make the degraded DR state explicit.

Execution pattern:

```bash
ssh kira-yc 'set -euo pipefail
printf "BEFORE_DISK\n"; df -h / /data/kira
printf "BACKUP_UNITS_BEFORE\n"; systemctl --user list-timers --all --no-pager | grep -E "kira-vm-backup|backup" || true
systemctl --user stop kira-vm-backup.timer kira-vm-backup.service 2>/dev/null || true
systemctl --user disable kira-vm-backup.timer 2>/dev/null || true
sudo rm -rf /data/kira/backups
test ! -e /data/kira/backups && echo backups_dir_absent
systemctl --user is-enabled kira-vm-backup.timer 2>/dev/null || true
systemctl --user is-active kira-vm-backup.timer 2>/dev/null || true
printf "AFTER_DISK\n"; df -h / /data/kira
sudo du -xhd1 /data/kira 2>/dev/null | sort -hr | head -12
'
```

Immediate reporting requirements:

- Say directly that **no local VM backups remain**.
- Report disk before/after and `kira-vm-backup.timer` enabled/active state.
- Do not imply production readiness or restore safety after deleting backups.
- Check public routes and failed units after freeing space, but do not silently expand into repair unless requested.
- If public routes still return `502`, list that as the next recovery blocker.

Post-deletion recovery sequence:

1. Record a maintenance/status artifact: backups intentionally suspended, not accidentally missing.
2. Fix route/runtime breakage (`502`) before changing storage architecture.
3. Update health logic so missing backups during intentional maintenance report `BACKUP_SUSPENDED` or equivalent, not a false PASS.
4. Implement backup frequency/retention/exclusion policy.
5. Only then create a fresh bounded backup and run restore-smoke.
6. Treat VM as not disaster-recoverable until fresh backup + restore-smoke pass.

## Health gates

Production readiness should check:

- latest backup is valid;
- latest backup age is below threshold (e.g. 30h);
- restore-smoke age is below threshold;
- local backup count/size is within retention policy;
- `/data/kira` free space is above threshold (at least 20–25% or an absolute minimum such as 30 GiB on a 256 GiB disk);
- Object Storage archive upload/lifecycle status is passing if remote archive is enabled.

After emergency backup deletion, health must not report backup readiness from stale assumptions. It should fail clearly or enter an explicit backup-suspended maintenance mode until a new valid backup and restore-smoke exist.
