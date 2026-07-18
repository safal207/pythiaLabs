# CI Causal Memory v0.1

CI Causal Memory records one immutable observation for each Lotus Family conformance run. It connects execution space and run time without allowing learned state to modify protected CI.

## Safety boundary

The observation layer is advisory and append-only.

It may:

- record exact run identity and execution location;
- normalize a stable failure signature;
- link later observations to prior runs;
- support human-reviewed regression proposals.

It may not:

- rewrite workflows, tests, policies, or protected branches;
- approve, merge, deploy, deliver, or close findings;
- mark a causal hypothesis confirmed from correlation alone;
- store secrets, raw environment values, or unbounded logs.

`PASS != APPROVED != MERGED`.

## Spacetime coordinates

Every observation has a stable spatial path:

```text
repository
  → ref
  → exact commit
  → workflow
  → job
  → step
  → command/test target
```

Every observation also has a temporal identity:

```text
workflow run ID
  → run attempt
  → observed timestamp
  → optional predecessor observation
```

## Causal states

The first slice supports these deterministic learning states:

- `observed_once`
- `repeated`
- `reproduced`
- `fix_correlated`
- `fix_validated`
- `regression_protected`

A single CI run always starts at `observed_once`. Promotion requires a separate trusted aggregator and explicit evidence.

## Failure signature

For non-success conclusions, the emitter computes SHA-256 over a canonical tuple:

```text
schema version
repository
workflow
job
step
command
conclusion
reason code
```

The signature deliberately excludes timestamps, run IDs, secrets, and raw logs so equivalent failures can be linked across runs.

## Artifact

The workflow writes:

```text
artifacts/lotus-ci-memory/ci-causal-observation-v0.1.json
```

The artifact is uploaded with `if: always()` after the conformance step. The conformance step remains failure-gating; artifact generation cannot turn a failed test into a successful job.

## Trust model

The PR workflow can emit only its own immutable observation artifact. Durable cross-run aggregation belongs in a later default-branch `workflow_run` workflow that does not execute PR code.

The initial artifact may contain caller/platform claims for repository, ref, and commit. Trusted repository/tree binding remains the responsibility of Lotus Family v0.2 materialization.
