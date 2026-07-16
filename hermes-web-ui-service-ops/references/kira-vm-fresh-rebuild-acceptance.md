# Kira VM fresh rebuild acceptance rehearsal

Use this when Maxim asks whether the YC VM contour is ready to replace the home PC, or when proving beta/multi-user VM infra is reproducible.

## Acceptance shape

A convincing rehearsal is not just `systemctl active` on the existing VM. It should prove a fresh VM can be rebuilt from repo + backup artifacts:

1. Create or select a disposable YC rehearsal VM in the same intended network/security-group shape.
2. Put the ops repo state on the VM from a reproducible source. Preferred: deploy key or authenticated clone. If unavailable, `rsync` from a clean local checkout is acceptable only as a rehearsal workaround and must be reported as a caveat.
3. Run provisioning from the repo, including tenant/user creation and runtime dependency bootstrap.
4. Restore an explicit dated backup directory, not an ambiguous symlink, when the symlink may lag.
5. Deploy repo-owned runtime/service artifacts.
6. Apply Web UI account -> runtime profile/UID mapping.
7. Run service health, assistant-instance validation, tenant isolation validation, and browser-facing login checks where in scope.
8. Record evidence under `docs/evidence/` with VM name/IP, source commit, backup path, commands/validation summaries, and caveats.

Do not move `app.kiraproject.ru`, disable the PC contour, or enable duplicate Telegram gateway processing until Maxim explicitly accepts the VM rehearsal.

## Tenant isolation gates

The minimum beta isolation proof should include:

- stable UID-style tenant IDs as canonical identities; names are display/compatibility labels only;
- separate Linux users for beta tenants;
- `/data/kira/users` traversable enough for users to reach their own private UID roots, while individual UID roots remain private;
- each tenant can read/write only their own assistant/profile/workspace namespace;
- cross-tenant reads fail;
- shared docs/skills are read-only where intended;
- secrets and Maxim/admin namespaces deny tenant access.

Pitfall: making `/data/kira/users` too private can block tenants from traversing to their own `0700` UID roots. Validate traversal as the tenant user, not only as root.

## User systemd health from root

Root-run health checks cannot assume bare `systemctl --user` works; it may fail because there is no user bus in the root environment. When checking user services from a root health script, run as the runtime user with the correct `XDG_RUNTIME_DIR=/run/user/<uid>` and verify the user manager exists before declaring service failure.

Health should prove both layers:

```bash
systemctl --user is-active <unit>   # from the correct runtime user/session context
ss -ltnp                            # listener exists on expected localhost/port
curl -fsS http://127.0.0.1:<port>/health
```

For preview service sets, include Web UI, agentmemory, Paperclip, bridge/proxy, profile mapping, latest backup presence, and assistant-instance registry/layout checks.

## Backup/restore coverage

A fresh rebuild rehearsal should restore both state and runtime artifacts needed to make services executable. For this contour, treat these archive classes as important:

- service/runtime artifacts such as `/opt/kira/services`;
- users and per-tenant namespaces;
- shared read-only areas;
- Hermes profiles/workspaces;
- Web UI/runtime state;
- ops runtime metadata and manifests.

If Authentik is part of the acceptance claim, require an Authentik backup archive/restore path too. If the backup set lacks it, report Authentik restore as unverified instead of implying full SSO disaster recovery passed.

## Runtime dependency bootstrap

Do not rely on manually copied binaries for a rebuild claim. Capture required preview dependencies in a repo-owned bootstrap script and call it from provisioning. The durable lesson is the bootstrap step, not that a particular binary was missing in one rehearsal.

## Reporting standard

Use `PASS with caveats` when safe gates pass but reproducibility is not yet pure. Typical caveats:

- repo arrived via `rsync` instead of authenticated clone/deploy key;
- Authentik restore was not covered by the backup used;
- browser acceptance for real users was not run;
- the rehearsal VM remains running and incurring cost.

Keep the report short: VM identity, passed gates, caveats, and the one decision Maxim must make next (usually keep/delete rehearsal VM or approve cutover stage).
