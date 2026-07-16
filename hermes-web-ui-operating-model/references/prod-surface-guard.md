# Protected production surface guard

Use when working toward a beta/dev/user-contour goal while an existing browser-facing production Web UI must not be broken.

Pattern:

1. Add a read-only production guard command before deeper beta/runtime changes.
2. The guard should only perform HTTP checks; it must not restart services, rewrite config, deploy, or touch state.
3. Check at least:
   - public root returns expected success status;
   - `/health` returns expected success status;
   - protected API health returns the currently expected protected/healthy status, commonly `401` or `200` depending on auth model.
4. Run the guard before and after any beta-contour smoke/provisioning work.
5. Record the guard output in evidence, but do not claim the product goal is complete just because the guard and smoke checks pass.

Example command shape:

```bash
./bin/kira check prod-surface
./bin/kira validate all
./bin/kira smoke beta-all <uid>
```

This is a safety gate, not a deployment gate: it proves non-breakage of the protected surface at that moment, not tenant isolation or feature readiness.
