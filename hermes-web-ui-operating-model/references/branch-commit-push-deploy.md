# Feature branch, commit, push, and dev-deploy flow

Session note for Hermes Web UI work.

## Confirmed workflow

- Start from `origin/main`.
- Work on a short-lived feature branch.
- Make commits during feature creation once a logical step is complete; do not wait until the very end.
- Push the branch to `origin` before finishing the session.
- For preview/development verification on Kira home, deploy the branch to the isolated dev runtime rather than touching production.

## Verification pattern

- Build and test the branch locally first.
- Push after the branch is in a reviewable state.
- Deploy preview/dev to the `hermes.dev.ops.kiraproject.ru` runtime when the task is explicitly about the dev surface.
- Verify the live health endpoint after restart/deploy.

## Notes

- Keep production on the canonical runtime and branch unless the user explicitly asks for a production deploy.
- Do not mix unrelated cleanup into the feature branch just to make deployment easier.
