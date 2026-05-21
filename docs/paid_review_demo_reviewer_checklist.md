# Paid Review Demo Reviewer Checklist

This checklist helps a reviewer verify the paid review demo without reading the full codebase first.

## Run the demo

From the repository root:

```bash
make demo
```

Equivalent direct command, when available:

```bash
mix run examples/paid_review_demo.exs
```

Compare the terminal output with:

- [`../examples/paid_review_demo_expected_output.md`](../examples/paid_review_demo_expected_output.md)

## What to verify

Use this checklist during review:

- [ ] The demo starts with `PythiaLabs — Paid Review Demo`.
- [ ] The scenario set is printed as `paid_review_demo_2026_05`.
- [ ] The accepted transfer scenario returns `accepted / treasury_transfer_accepted`.
- [ ] The quorum failure scenario returns `rejected / quorum_not_met`.
- [ ] The timelock failure scenario returns `rejected / timelock_not_satisfied`.
- [ ] The transfer window scenario returns `rejected / transfer_expired`.
- [ ] Each scenario prints an evidence trace with `PASS` / `FAIL` checks.
- [ ] Each scenario prints a SHA-256 digest prefix.
- [ ] Each scenario reports `evidence : verified`.
- [ ] The counterfactual section shows `rejected -> accepted` or equivalent decision flip wording.
- [ ] The demo writes an artifact bundle to `examples/output/paid_review_demo_artifact.json`.
- [ ] The final result reports `PASS` when all scenarios match expectations.

## Evidence checks to inspect

A reviewer should be able to see these checks in the output across the scenarios:

- `proposal_match_check`
- `permission_check`
- `quorum_check`
- `voting_window_check`
- `timelock_check`
- `authorization_valid_time_check`
- `authorization_transaction_time_check`
- `transfer_expiration_check`

## What this demo should prove

The demo should show that PythiaLabs can:

1. evaluate multiple proposed actions through the real showcase engine,
2. produce deterministic accept/reject outcomes,
3. attach stop reasons to rejected actions,
4. produce evidence traces for each decision,
5. verify evidence digests,
6. show a counterfactual decision flip when a relevant evidence field changes,
7. write a reviewer-facing artifact bundle.

## What this demo does not claim

This demo does not claim:

- production security,
- regulatory compliance,
- certified safety,
- wallet integration,
- smart-contract execution,
- real identity verification,
- complete protection against malicious agents.

It is a deterministic local review artifact for evaluating the action-gate concept and current implementation behavior.
