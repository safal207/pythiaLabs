# Web3 Treasury Full Showcase — Expected Output

## Command

```bash
mix run examples/web3_treasury_full_showcase.exs
```

## What this demo proves

This full showcase demonstrates the complete deterministic Web3 treasury reasoning flow:

- accepted treasury action
- rejected treasury action when quorum is not met
- rejected treasury action when authorization was valid but unknown at decision time
- structured trace export
- SHA-256 digest generation
- evidence verification
- tamper rejection
- unsigned evidence envelope verification
- signed_demo envelope generation
- signed_demo verification
- tampered signed_demo rejection

Clarification: The `signed_demo` flow is deterministic local demo logic only and is not production cryptography.

## Expected high-level output

The exact digest values may differ if payload structure changes, but the decision outcomes and rejection reasons should remain stable.

Expected sections:

### 1. Accepted treasury action

- `status: accepted`
- `stop_reason: treasury_transfer_accepted`
- `final_decision: accept`

### 2. Rejected treasury action: quorum_not_met

- `status: rejected`
- `stop_reason: quorum_not_met`
- `failed_check: quorum_check`

### 3. Rejected treasury action: authorization_valid_but_unknown_at_decision_time

- `status: rejected`
- `stop_reason: authorization_valid_but_unknown_at_decision_time`

### 4. Evidence export

- `export_status: accepted`
- `export_stop_reason: treasury_transfer_accepted`
- `trace_length` should be greater than `0`

### 5. Evidence digest

- `algorithm: sha256`
- `digest`: 64-character lowercase hex string

### 6. Evidence verification

- `verification_status: verified`
- `algorithm: sha256`

### 7. Tampered evidence rejection

- `verification_status: rejected`
- `reason: digest_mismatch`

### 8. Unsigned evidence envelope

- `schema: pythia.evidence.envelope.v1`
- `verification_status: verified`

### 9. Signed demo envelope

- `signature_status: signed_demo`
- `algorithm: sha256-demo`
- `signer_id: demo_dao_reviewer`

### 10. Signed demo verification

- `verification_status: verified`
- `signer_id: demo_dao_reviewer`

### 11. Tampered signed demo envelope rejection

- `verification_status: rejected`
- `reason: digest_mismatch`

### 12. Final marker

- `Full showcase completed.`

## Why this matters for reviewers

This output shows that PythiaLabs can produce not only a decision, but also a replayable explanation and integrity-checkable evidence artifact.

A reviewer can see:

- why an action was accepted
- why unsafe actions were rejected
- which governance check failed
- whether an evidence payload was modified
- whether an unsigned or signed_demo envelope verifies
- where production cryptography would later fit

## Non-goals

This showcase does not claim:

- production cryptography
- wallet integration
- smart contract execution
- RPC/indexer integration
- on-chain enforcement
- real identity verification

It is a deterministic local showcase for reasoning, auditability, and grant review.
