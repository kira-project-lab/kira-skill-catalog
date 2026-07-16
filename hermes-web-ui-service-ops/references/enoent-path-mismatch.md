# ENOENT path mismatch triage

Use this when a Hermes Web UI session or agent tool reports `Error: [Errno 2] No such file or directory` and the visible message is truncated or generic.

## What to check

1. Open the current profile logs, especially:
   - `~/.hermes/profiles/kira/logs/errors.log`
   - `~/.hermes-web-ui/logs/server.log`
   - `~/.hermes-web-ui/logs/bridge.log`
2. Search for the exact session id and the `read_file returned error` / `File not found:` line.
3. Recover the full path from the log line, not from memory or the UI toast.
4. Compare the failed path against the live vault / repo tree and the actual filename casing.
5. If the parent folder exists but the file does not, treat it as a stale reference, typo, or renamed note, not as a service crash.

## Strong signals of a stale path reference

- path prefix is valid, but the leaf filename is only partially visible in the log
- the error appears during content lookup, not startup or port binding
- the same host still passes `/health`
- nearby files exist with similar names, but not the exact one requested
- the filesystem is case-sensitive and the note name in the request differs by capitalization or punctuation

## Safe next step

- locate the canonical file name with a search over the target directory,
- update the request / note link to the canonical filename,
- rerun the action.

## Do not mistake this for

- service startup failure
- SQLite read-only failure
- bridge socket failure
- port-binding failure

This pattern is about *bad path resolution* in a live, otherwise healthy service.
