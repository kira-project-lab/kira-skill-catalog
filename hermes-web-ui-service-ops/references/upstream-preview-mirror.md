# Upstream preview mirror for Hermes Web UI

Use this pattern when the user wants a separate preview of the upstream/original Hermes Web UI repository that tracks `upstream/main` continuously and stays isolated from the primary deployment.

## Intent
- Keep the upstream mirror separate from the production/main Hermes Web UI install.
- Follow the original author’s `main` branch directly, even when no release exists yet.
- Expose the mirror on a dedicated host/subdomain.
- Preserve independent runtime state, profile, and storage.
- Make freshness and provenance visible via build metadata.

## Recommended shape
1. **Separate working tree**
   - Clone the upstream repository into its own directory.
   - Keep it outside the main app working tree.

2. **Separate runtime state**
   - Use a distinct Hermes home/profile root for the preview.
   - Do not reuse the primary install’s storage, sessions, or caches.

3. **Dedicated service + timer**
   - Run the preview as its own service.
   - Add a refresh timer that periodically fetches `upstream/main`, rebuilds, and restarts the preview.

4. **Build metadata**
   - Persist repo, remote, branch, commit SHA, build timestamp, and runtime paths.
   - Expose this info in logs or a metadata file so it is obvious what revision is running.

5. **Reverse proxy host**
   - Map the preview to a dedicated subdomain such as `upstream.<domain>`.
   - Keep proxy rules separate from the primary host entry.

## Operational checks
- Confirm the timer is active.
- Confirm the service is listening on its own port.
- Check `/health` before trusting the UI.
- Verify the metadata file after refresh to ensure the SHA changed as expected.

## Pitfalls
- Do not mix preview state with the primary installation.
- If the upstream repo has no lockfile, a refresh script may need a fallback install path.
- If builds rely on devDependencies, ensure environment settings do not strip them during install/build.
- Make sure the proxy host and service port are aligned after every rebuild.

## What to look for in logs
- Current commit SHA.
- Whether the refresh timer fetched new upstream changes.
- Whether the build completed successfully and the service restarted cleanly.
