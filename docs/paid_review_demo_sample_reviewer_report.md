# Paid Review Demo — Sample Reviewer Report

Status: reviewer-facing example report.

This document shows the kind of Markdown report a reviewer could produce after running the deterministic paid review demo.

It is based on the current expected demo behavior documented in:

- [`../examples/paid_review_demo_expected_output.md`](../examples/paid_review_demo_expected_output.md)
- [`paid_review_demo_reviewer_checklist.md`](paid_review_demo_reviewer_checklist.md)
- [`evidence_artifact_schema.md`](evidence_artifact_schema.md)

## Scope

This sample report covers the local deterministic paid review demo:

```bash
make demo
```

The demo evaluates four Web3 treasury scenarios through the real showcase engine and writes a deterministic artifact bundle to:

```text
examples/output/paid_review_demo_artifact.json
```

This report is a sample format only. It is not a production audit, compliance certification, security certification, wallet review, smart-contract audit, or legal/financial opinion.

## Input scenario set

```text
scenario_set=paid_review_demo_2026_05
schema=pythia.demo.input.v2
```

The scenario set contains:

1. accepted clean treasury transfer;
2. rejected transfer due to missing quorum;
3. rejected transfer due to unsatisfied timelock;
4. rejected transfer due to expired transfer window;
5. counterfactual patch showing a decision flip when quorum evidence changes.

## Decision summary

| Scenario | Expected decision | Observed decision | Stop reason | Evidence verified? |
|---|---:|---:|---|---|
| `accepted_transfer` | accepted | accepted | `treasury_transfer_accepted` | yes |
| `quorum_not_met` | rejected | rejected | `quorum_not_met` | yes |
| `timelock_not_satisfied` | rejected | rejected | `timelock_not_satisfied` | yes |
| `transfer_window_expired` | rejected | rejected | `transfer_expired` | yes |

Result:

```text
PASS — all scenarios matched expectations
```

## Evidence trace summary

Across the four scenarios, the demo exposes these checks:

- `proposal_match_check`
- `permission_check`
- `quorum_check`
- `voting_window_check`
- `timelock_check`
- `authorization_valid_time_check`
- `authorization_transaction_time_check`
- `transfer_expiration_check`

The accepted scenario should show all required checks passing.

Rejected scenarios should show a stable failing check and stop reason:

| Rejected scenario | Expected failing check | Expected stop reason |
|---|---|---|
| `quorum_not_met` | `quorum_check` | `quorum_not_met` |
| `timelock_not_satisfied` | `timelock_check` | `timelock_not_satisfied` |
| `transfer_window_expired` | `transfer_expiration_check` | `transfer_expired` |

## Counterfactual result

The demo applies a counterfactual patch to the quorum failure scenario:

```json
{"governance_record":{"quorum_met":true}}
```

Expected result:

```text
rejected -> accepted
```

Reviewer interpretation:

The decision changes when relevant evidence changes. This supports the narrow claim that the gate is evidence-driven in the deterministic demo, rather than only matching the action shape.

## Artifact bundle review

Expected artifact location:

```text
examples/output/paid_review_demo_artifact.json
```

Reviewer should confirm:

- the bundle exists after running `make demo`;
- it contains four evidence records;
- each record has a scenario identifier;
- each record has a decision/status field;
- each record has a stable stop reason;
- each record includes check/trace evidence;
- each record has a SHA-256 digest;
- each record reports successful verification;
- the counterfactual section is present;
- runtime-specific digest values are not hard-coded into this report.

## Reviewer interpretation

The demo supports this narrow interpretation:

```text
PythiaLabs can evaluate several proposed high-risk agent actions through deterministic pre-execution evidence gates and produce reviewer-facing evidence artifacts.
```

The demo does not support inflated claims such as:

- production security;
- regulatory compliance;
- certified safety;
- complete protection against malicious agents;
- wallet security;
- smart-contract execution or auditing;
- on-chain enforcement;
- production incident response.

## Limitations / non-claims

This is a deterministic local demo and sample reviewer report.

It does not use real customer data.
It does not prove real-world production safety.
It does not replace security review, governance review, legal review, or human approval workflows.

See:

- [`NON_CLAIMS.md`](NON_CLAIMS.md)
- [`positioning_vs_transaction_simulation.md`](positioning_vs_transaction_simulation.md)

## Reviewer conclusion template

```text
The paid review demo passed locally.
All four scenarios matched expected outcomes.
Evidence records were generated and verified.
The counterfactual changed the decision as expected.

Conclusion: the demo is a useful deterministic reviewer artifact for inspecting the PythiaLabs pre-execution evidence-gate concept.
```
