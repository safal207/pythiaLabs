# Lotus Family Conformance v0.1

A bounded, machine-readable audit surface for checking the shared Lotus contract
across Pythia, CML, and LS.

## Outcomes

- `PASS` — every configured invariant was verified for the supplied repository
  snapshot and exact commit SHA.
- `DRIFT` — the snapshot is available, but a required contract term, regression
  test, or CI discovery rule is missing.
- `UNKNOWN` — the repository snapshot, exact ref, commit SHA, or manifest could
  not be verified. `UNKNOWN` is never promoted to `PASS`.

## Boundary

The auditor is read-only and `audit_only`. Its result does not grant ownership,
approval, execution, delivery, deployment, or merge authority.

It does not fetch repositories, call GitHub, merge pull requests, or deploy
software. An integration must materialize a repository snapshot at the exact
commit it claims to audit.

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
  --snapshot-root /path/to/exact-snapshots \
  --repository-id pythia \
  --repository-ref refs/heads/main \
  --commit-sha 0123456789abcdef0123456789abcdef01234567 \
  --output artifacts/lotus-family/pythia.json
```

Exit codes are `0` for `PASS`, `2` for `DRIFT`, and `3` for `UNKNOWN`.

The evidence artifact records the exact repository identity, ref, commit SHA,
check outcomes, checked file paths, and SHA-256 hashes.
