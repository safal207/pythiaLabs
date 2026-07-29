# Pilot runner entrypoint

Run the first empirical pilot through the manual GitHub Actions workflow:

```text
Actions → CAEP Authority Boundary Pilot → Run workflow
```

The default settings request 60 runs and require provider API keys in repository Actions secrets.

Start with:

- `.github/workflows/caep-authority-boundary-pilot.yml`;
- `PILOT_RUN_STATUS.md`;
- `LAUNCH_CHECKLIST.md`;
- issue #252.

The workflow produces raw evidence only. Use `RESULTS_POLICY.md` before publishing any comparative claim.
