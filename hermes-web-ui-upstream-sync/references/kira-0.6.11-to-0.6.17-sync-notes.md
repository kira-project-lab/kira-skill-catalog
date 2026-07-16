# Kira Hermes Web UI upstream sync notes: 0.6.11 → 0.6.17

Use this as a concrete example of the downstream-fork update workflow, not as permanent truth. Re-check refs every time.

## Observed state in the first delta review

- Kira production reported `webui_version: 0.6.11` from `/health`.
- Upstream `main` package version was `0.6.17`.
- Production ran from `origin/main`.
- Upstream changed repository metadata from `hermes-web-ui` toward `hermes-studio`.
- The branches were divergent, not a simple fast-forward.

## User preference confirmed

Maxim explicitly expects updates to be built on `dev`/integration first. He suggested the correct shape himself: create a separate branch based on the author's latest version, then roll Kira changes into it before merging toward `dev`.

## Important lesson

Do not describe Kira's changes as “mostly cosmetic” without checking. In this case, Kira had many UI/design commits, but also meaningful product/runtime layers:

- server-authoritative session row state;
- read receipts/read status sync;
- committed session card snapshots;
- realtime session row sync catch-up;
- draft-first new chat lifecycle;
- session tags/filtering/pins/browser prefs;
- activity rail user preferences;
- title generation/settings;
- Paperclip entrypoint;
- YOLO bridge routing;
- custom/local STT safety and probe logic;
- Codex profile OAuth/global model defaults;
- Kira deploy topology and scripts.

## Practical recommendation for this class of update

For a large upstream jump, prefer `integration/upstream-<version>` from `upstream/main` and then reapply Kira layers by contract. Avoid a blind `merge upstream/main` into Kira `dev`, because older Kira chat/session/runtime files can accidentally override newer upstream fixes.

## Reporting stance

When Maxim asks “or is it mostly design?”, answer from evidence:

1. commit counts and touched files;
2. semantic layer map;
3. which layers are cosmetic vs architecture/runtime;
4. recommended adoption strategy.

Keep the response compact, but do the git inspection before the verdict.
