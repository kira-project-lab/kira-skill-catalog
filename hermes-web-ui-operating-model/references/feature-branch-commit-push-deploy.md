# Feature branch, commit, push, and preview deploy notes

## What this session established

- For Hermes Web UI feature work, do not wait until the end of the task to create the first commit.
- Make small, coherent commits as soon as a logical milestone is complete.
- Push the feature branch before or alongside preview deployment so remote state is available for review/recovery.
- Keep preview/development runtime isolated from production by using a separate worktree, separate port, and separate state directories.
- A preview deploy may restart only the preview service; if the production connection drops at the same time, investigate shared client/proxy/browser state before assuming the prod service restarted.

## Verification pattern

- Verify production and preview separately:
  - service/unit status
  - listener port
  - health endpoint
- If one environment disconnects while another is being deployed, check whether the browser tab or proxy layer is shared before treating it as a backend outage.
- Do not infer a prod outage from a preview deployment unless the prod unit, port, or health endpoint also changed.
