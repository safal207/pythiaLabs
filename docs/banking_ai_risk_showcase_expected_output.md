# Banking AI Risk Showcase — Expected Output Guide

Run:

```bash
mix run examples/banking_ai_risk_showcase.exs
```

This is a deterministic local showcase for reviewer walkthroughs. It does **not** claim production banking integration, regulatory compliance, or cybersecurity protection.

## Expected sections

The script prints the following deterministic section headers:

- `A. Accepted banking risk action`
- `B. Rejected action: missing operator approval`
- `C. Rejected action: stale evidence`
- `D. Rejected action: valid authorization but unknown at decision time`
- `E. Evidence export`
- `F. Evidence digest`
- `G. Evidence verification`
- `H. Tampered evidence rejection`

## Expected shape by section

### A) Accepted banking risk action

Expected lines include:

- `status: accepted`
- `stop_reason: banking_risk_action_accepted`
- deterministic `trace_event_count`

### B) Missing operator approval

Expected lines include:

- `status: rejected`
- `stop_reason: missing_operator_approval`

### C) Stale evidence

Expected lines include:

- `status: rejected`
- `stop_reason: stale_evidence`

### D) Authorization unknown at decision time

Expected lines include:

- `status: rejected`
- `stop_reason: authorization_unknown_at_decision_time`

### E) Evidence export

Expected lines include:

- `export_status: accepted`
- `export_stop_reason: banking_risk_action_accepted`

### F) Evidence digest

Expected lines include:

- `algorithm: sha256`
- `digest: <64-char lowercase hex>`

### G) Evidence verification

Expected lines include:

- `verification_status: verified`
- `algorithm: sha256`

### H) Tampered evidence rejection

Expected lines include:

- `verification_status: rejected`
- `reason: digest_mismatch`

## Reviewer note

Banking AI risk is not only about model outputs. This deterministic demo focuses on whether high-risk AI-enabled actions should proceed **before** execution, with stable stop reasons and replayable evidence for audit/review.
