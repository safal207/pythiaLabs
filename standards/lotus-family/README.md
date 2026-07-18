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

Remote identity verification, trusted materialization, and evidence attestation
remain follow-up work. Until then, `PASS` means conformance of the supplied
snapshot contents, not cryptographic proof that the snapshot came from the
claimed remote commit.

## Causal testing model

The primary test model lives in:

- `causality/lotus-family-causality-v0.1.json` — causes, controls, risks, evidence,
  outcomes, and authority boundaries;
- `causality/test-paths-v0.1.json` — executable end-to-end routes through that graph;
- `causality/TRACEABILITY.md` — a reviewable matrix derived from the routes.

Every new blocker must add or reuse a causal node and include an executable route.
This prevents isolated regression tests from hiding missing relationships between
workflow structure, command execution, test selection, evidence, and verdicts.

## Boundary

The auditor is read-only and `audit_only`. Its result does not grant ownership,
approval, execution, delivery, deployment, or merge authority.

It does not fetch repositories, call GitHub, merge pull requests, or deploy
software. An integration materializes the repository snapshot it wants audited.

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
