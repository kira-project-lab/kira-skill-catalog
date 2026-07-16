# Live bundle verification

Use this when a Hermes Web UI behavior appears to differ between the local repo and the live host after a merge, push, or restart.

## What to check

1. **Live HTML asset hash**
   - Fetch the host root page and record the JS/CSS bundle names.
   - Compare them with the bundle names produced by the candidate build.
   - If the filenames differ, you are not looking at the same build.

2. **Served source vs checked-out source**
   - Confirm the service unit `WorkingDirectory`, `ExecStart`, and active package path.
   - A restarted service can still point to a different install than the repo currently open in your terminal.

3. **Client-side state**
   - Re-open the site in a fresh tab or hard-refresh.
   - Clear or inspect `localStorage` when the UI uses persisted keys for auth or layout state.
   - Stale client state can make a fixed UI look broken or a broken UI look fixed.

4. **DOM/CSS for layout bugs**
   - For hover/hidden-control/layout issues, inspect the live DOM and CSS selectors on the deployed host.
   - Do not infer layout behavior only from source code.

## Useful pattern

When the live host “starts working after restart”, treat that as a clue that one of these changed:
- the active service package/worktree,
- the browser cache,
- localStorage/session state,
- the deployed bundle hash.

The right conclusion is not “restart always fixes it”; it is “the deployed artifact and the browser state needed revalidation.”
