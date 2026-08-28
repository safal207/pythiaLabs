# Lotus Family Conformance v0.1

A bounded, machine-readable audit surface for checking the shared Lotus contract
across Pythia, CML, and LS.

## Outcomes

- `PASS` — every configured content and executable-CI invariant passed for the
  supplied snapshot and the caller-provided repository, ref, and commit claims.
- `DRIFT` — the snapshot is available, but a required contract term, regression
  test, or CI discovery rule is missing.
- `UNKNOWN` — the repository snapshot, ref claim, commit claim, or manifest could
  not be evaluated safely. `UNKNOWN` is never promoted to `PASS`.

## Identity assurance

Version 0.1 does not fetch a remote repository and does not prove commit
reachability or a clean working tree. Repository, ref, and commit values are
caller-provided claims recorded in evidence. Results expose
`identity_assurance.mode = caller_claim_only` so consumers cannot mistake these
claims for verified provenance.

SHA-256 evidence binds each check to the exact bytes read and evaluated from the
supplied snapshot. It does **not** prove that those bytes came from the claimed
remote repository, ref, or commit. Independent trusted materialization and
provenance verification are required before evidence may be called fresh for an
exact head.

Until that verification exists, `PASS` means conformance of the supplied
snapshot contents, not cryptographic proof that the snapshot came from the
claimed remote commit.

Workflow action prerequisites are accepted only when the repository adapter
lists the exact `owner/repository@<40-hex-SHA>` identity. This is an explicit,
immutable trust input for structural CI reachability, not local execution or a
claim that the action cannot mutate runner state. Unlisted, local, expression-
selected, tag-selected, or branch-selected actions fail closed. Earlier shell
steps are limited to closed literal prerequisite forms. That allowlist is also
a structural reachability assumption, not proof of side-effect freedom;
arbitrary commands or direct writes to audited inputs never establish a later
test gate.

The configured Python and Elixir contract-test sources must match pinned
SHA-256 values, so retaining required phrases in a replacement no-op test cannot
produce `PASS`. Pytest discovery also fails closed on repository-local pytest,
pytest-dependency, sourceless-bytecode, native-extension, or Python-startup
shadows that could preempt the installed runner before contract collection.

## Causal spacetime testing model

The test model has two compatible layers:

- `causality/lotus-family-causality-v0.1.json` and
  `causality/test-paths-v0.1.json` preserve the original causal routes;
- `causality/lotus-family-system-v0.1.json` and
  `causality/system-routes-v0.1.json` add spatial, temporal, hierarchical, and
  trajectory views.

The system graph separates bounded snapshot `PASS` from independently verified
exact-head freshness and merge eligibility. Centrality means review priority and
blast radius only; it never grants ownership, approval, execution, delivery, or
merge authority.

Every new blocker must add or reuse a graph node and include an executable route
when runtime behavior is involved. This prevents isolated regression tests from
hiding missing relationships between workflow structure, inherited execution
context, test selection, evidence, and verdicts.

## Boundary

The auditor is read-only and `audit_only`. Its result does not grant ownership,
approval, execution, delivery, deployment, or merge authority.

It does not fetch repositories, call GitHub, merge pull requests, or deploy
software. An integration materializes the repository snapshot it wants to audit.

## Snapshot layout

```text
snapshot-root/
  safal207__pythiaLabs/
  safal207__Causal-Memory-Layer/
  safal207__LS/
```

Each directory must contain the files named by
[`manifest/lotus-family-v0.1.json`](manifest/lotus-family-v0.1.json).

## Run one audit

```bash
python standards/lotus-family/conformance/lotus_family_auditor.py \
  --manifest standards/lotus-family/manifest/lotus-family-v0.1.json \
  --snapshot-root /path/to/snapshots \
  --repository-id pythia \
  --repository-ref refs/heads/main \
  --commit-sha 0123456789abcdef0123456789abcdef01234567 \
  --output artifacts/lotus-family/pythia.json
```

Exit codes are `0` for `PASS`, `2` for `DRIFT`, and `3` for `UNKNOWN`.

The evidence artifact records the caller-provided repository identity claims,
check outcomes, checked file paths, SHA-256 hashes, identity-assurance limits,
and the audit-only authority boundary.
