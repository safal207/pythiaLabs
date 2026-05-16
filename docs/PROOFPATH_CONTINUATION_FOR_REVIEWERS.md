# ProofPath Continuation for Reviewers

This page is for reviewers who arrived at PythiaLabs from an already-submitted grant application or email inquiry.

PythiaLabs remains the evidence-gate project described in earlier materials: deterministic gates for high-risk agentic actions, replayable traces, stable stop reasons, and tamper-checkable evidence artifacts.

Since those applications were submitted, the strongest continuation evidence has moved into a focused companion repository:

- ProofPath: https://github.com/safal207/ProofPath
- Submitted application reviewer bridge: https://github.com/safal207/ProofPath/blob/main/docs/SUBMITTED_APPLICATION_REVIEWER_BRIDGE.md
- Compute Witness grant reviewer path: https://github.com/safal207/ProofPath/blob/main/docs/COMPUTE_WITNESS_GRANT_REVIEWER_PATH.md

## Relationship

PythiaLabs and ProofPath should not be treated as exact aliases.

A useful reviewer mapping is:

```text
PythiaLabs
  -> deterministic evidence gates for proposed AI-agent actions

ProofPath
  -> executable action-boundary and verifier layer

Compute Witness
  -> reviewable evidence for AI/agent compute results
```

The shared research direction is:

```text
high-risk AI-agent actions should not be trusted only because a model or service produced them;
they should carry inspectable evidence of intent, scope, authorization, commitments, and auditability.
```

## Why this matters for submitted applications

Some submitted applications may reference PythiaLabs, Liminal Stack, LTP+CML, deterministic oversight, or open evidence gates.

ProofPath / Compute Witness is the current executable evidence layer for that direction. It provides a more concrete review surface:

- root reviewer positioning;
- reviewer quickstart;
- committed job manifests, receipts, and audit fixtures;
- Python conformance validator;
- audit packet examples;
- broken-evidence challenge fixtures;
- Rust verifier adapter;
- Rust CLI path;
- expected Rust output fixture;
- Rust audit-hash verification primitive;
- CI regression checks.

## Fast route for reviewers

Start here:

1. Open ProofPath: https://github.com/safal207/ProofPath
2. Read the Submitted Application Reviewer Bridge.
3. Open the Compute Witness Grant Reviewer Path.
4. Run the reviewer quickstart commands from ProofPath.

Shortest ProofPath commands:

```bash
python3 scripts/validate_compute_witness.py
cargo run -q -p proofpath-verifier --bin proofpath-compute-witness -- examples/compute-witness/job_manifest.accept.json
```

## What this does not claim

This note does not claim that PythiaLabs and ProofPath are the same repository or the same exact product surface.

It also does not claim production cryptography, certified compliance, GPU hardware identity, trusted execution environment attestation, zkML correctness, model truthfulness, or production key management.

The intended claim is narrower:

```text
ProofPath / Compute Witness is the current executable continuation evidence for the same evidence-gate research direction described in earlier PythiaLabs-facing grant materials.
```
