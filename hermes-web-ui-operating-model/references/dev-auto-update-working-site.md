# Dev Auto-Update Working Site

Use when Maxim asks to do Hermes Web UI work directly on `dev` or when local `dev` commits are created.

## Rule

For Hermes Web UI dev work, a committed change on `dev` should update the working dev site automatically unless Maxim explicitly says not to deploy.

Working site:

```text
https://hermes.dev.ops.kiraproject.ru/
```

Runtime:

```text
/home/werserk/2-kira/hermes-web-ui-dev
hermes-web-ui-dev.service
backend: 8647
frontend: 8649
```

## Default sequence after committing on `dev`

1. Confirm the checkout is `/home/werserk/2-kira/hermes-web-ui-dev` and branch is `dev`.
2. Push the commit(s):

```bash
git push origin dev
```

3. Restart live-dev so backend/server code and health metadata pick up the new commit:

```bash
systemctl --user restart hermes-web-ui-dev.service
```

4. Verify local and public health both report the new commit:

```bash
curl -fsS http://127.0.0.1:8647/health
curl -fsS https://hermes.dev.ops.kiraproject.ru/health
```

5. For browser-visible work, verify the public browser surface or served bundle after the restart.

## Pitfalls

- A local build is not enough; the working site can still serve an older commit.
- `origin/dev` update is not enough if the live-dev service has not restarted or reloaded the backend.
- Immediately after `systemctl --user restart hermes-web-ui-dev.service`, Vite/frontend health can return `502 Bad Gateway` and backend health can briefly refuse connections while the server finishes booting. Treat this as startup warmup: poll local backend/frontend and public dev health for a short bounded window before calling the restart failed.
- `/health` must show the committed `git_commit`; otherwise report source/runtime drift.
- Do not use branch-preview deploy for ordinary direct `dev` work unless Maxim asks for a pinned preview branch.
