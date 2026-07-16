# GitHub Actions artifact quota after successful tests

Use this when a Hermes Web UI `Playwright` workflow is red even though the test step itself completed successfully.

## Symptom

`gh run watch` or `gh run view --log-failed` shows the failed job step is `Upload Playwright report`, with an error like:

```text
Failed to CreateArtifact: Artifact storage quota has been hit. Unable to upload any new artifacts.
```

The preceding `Run Playwright tests` step is green.

## Interpretation

This is a CI artifact-storage failure, not an application/e2e test failure. Do not report it as broken product behavior.

For production auto-deploy decisions, keep the gates distinct:

1. Local relevant tests/build/e2e passed before push.
2. `Build` workflow on `main` succeeded for the target SHA.
3. `Deploy Hermes Prod` workflow succeeded for the target SHA.
4. Public and local `/health` report the deployed SHA.
5. Served bundle/source check contains the user-visible change when UI changed.

If these pass, prod can be correctly deployed even while `Playwright` is red from artifact quota. Report the CI caveat explicitly and include the failed step name.

## Useful commands

```bash
gh run view <playwright-run-id> --repo kira-project-lab/hermes-web-ui --log-failed | tail -80
gh run view <build-run-id> --repo kira-project-lab/hermes-web-ui --json status,conclusion,headSha,url
gh run view <deploy-run-id> --repo kira-project-lab/hermes-web-ui --json status,conclusion,headSha,url
```
