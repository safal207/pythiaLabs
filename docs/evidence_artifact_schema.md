# Evidence Artifact Schema

This page summarizes the shape of PythiaLabs evidence artifacts as they appear in the current deterministic local demos.

The goal is reviewer clarity: a reviewer should understand what information is recorded, how decisions can be inspected, and which claims are intentionally not being made.

## Purpose

An evidence artifact captures the decision-time record for a proposed action.

It is meant to answer:

```text
What action was proposed?
What evidence was available when the gate decided?
Which checks passed or failed?
What decision was returned?
Why was the action allowed, blocked, or escalated?
Can the evidence payload be checked for tampering?
```

## Common fields

Current artifacts vary by demo, but reviewers should expect the following conceptual fields.

| Field | Meaning |
|---|---|
| `schema` / `version` | Identifies the artifact or envelope format. |
| `scenario` / `scenario_id` | Names the scenario or trace being evaluated. |
| `proposed_action` | Describes the action the AI agent wanted to perform before execution. |
| `decision_time_evidence` / `payload` | Structured evidence available to the gate at decision time. |
| `checks` / `trace` | Ordered check results, often with `PASS` / `FAIL` status and check names. |
| `decision` / `status` / `final_decision` | The gate outcome, such as accepted/rejected or ALLOW/BLOCK/ESCALATE depending on the demo layer. |
| `stop_reason` | Stable reason explaining why a decision was accepted, rejected, blocked, or escalated. |
| `digest` | SHA-256 digest over the canonical evidence payload. |
| `algorithm` | Digest or demo-signing algorithm, such as `sha256` or `sha256-demo`. |
| `verification_status` | Whether the artifact or envelope verified successfully. |
| `signature_status` / `signer_id` | Demo-only envelope fields used by the signed_demo flow. |

## Paid review demo artifact

The paid review demo runs with:

```bash
make demo
```

It writes a deterministic artifact bundle to:

```text
examples/output/paid_review_demo_artifact.json
```

The expected output reference is:

- [`../examples/paid_review_demo_expected_output.md`](../examples/paid_review_demo_expected_output.md)

The demo reports:

- per-scenario evidence traces,
- accepted and rejected decisions,
- stable stop reasons,
- SHA-256 digest prefixes,
- evidence verification status,
- a counterfactual decision flip,
- and a final `PASS` result when all scenarios match expectations.

### Minimal example shape

The artifact bundle contains one record per scenario. A shortened
reviewer-facing record for the accepted transfer scenario has this shape:

```json
{
  "scenario": "accepted_transfer",
  "headline": "Clean 25,000 USDC treasury transfer",
  "expected_status": "accepted",
  "expected_stop_reason": "treasury_transfer_accepted",
  "evidence": {
    "artifact_type": "pythia.web3_treasury_action.decision_trace.v1",
    "algorithm": "sha256",
    "digest": "0000000000000000000000000000000000000000000000000000000000000000",
    "payload": {
      "status": "accepted",
      "stop_reason": "treasury_transfer_accepted",
      "trace": [
        {
          "event": "proposed_action",
          "result": "observed",
          "action_id": "dao_act_001",
          "action_type": "treasury_transfer",
          "proposal_id": "prop_001",
          "actor": "agent_treasury_alpha"
        },
        {
          "event": "quorum_check",
          "result": "pass",
          "quorum_met": true
        },
        {
          "event": "decision",
          "result": "accept",
          "stop_reason": "treasury_transfer_accepted"
        }
      ]
    }
  },
  "self_verify": "verified"
}
```

The all-zero digest value above is a placeholder. Running `make demo`
generates runtime-specific SHA-256 digests and fuller traces for each
scenario. In the written bundle, records like this appear under the
`scenarios` list alongside the bundle-level `schema`, `scenario_set_id`,
and `counterfactual` fields.

## Web3 treasury showcase artifact

The Web3 treasury showcase runs with:

```bash
mix run examples/web3_treasury_full_showcase.exs
```

The expected output reference is:

- [`web3_treasury_full_showcase_expected_output.md`](web3_treasury_full_showcase_expected_output.md)

The showcase demonstrates:

- accepted treasury action,
- rejected treasury actions,
- structured trace export,
- SHA-256 digest generation,
- evidence verification,
- tampered evidence rejection,
- unsigned evidence envelope verification,
- signed_demo envelope generation,
- signed_demo verification,
- and tampered signed_demo rejection.

## Decision and stop-reason examples

Current demos include outcomes such as:

| Scenario | Decision/status | Stop reason |
|---|---|---|
| Clean treasury transfer | accepted | `treasury_transfer_accepted` |
| Quorum not met | rejected | `quorum_not_met` |
| Timelock not satisfied | rejected | `timelock_not_satisfied` |
| Transfer window expired | rejected | `transfer_expired` |
| Authorization valid but unknown at decision time | rejected | `authorization_valid_but_unknown_at_decision_time` |

## Verification model

The current demo verification model is intentionally conservative:

1. The evidence payload is encoded canonically by the demo engine.
2. A SHA-256 digest is generated for the payload.
3. Verification recomputes the digest and compares it with the recorded digest.
4. If the payload is modified, verification rejects the artifact with a mismatch reason.

This is useful for deterministic review and tamper-checkable local artifacts.

## What this is not

Current PythiaLabs evidence artifacts are not presented as:

- production cryptography,
- regulatory compliance evidence,
- certified security controls,
- wallet protection,
- smart-contract auditing,
- on-chain enforcement,
- real identity verification,
- a complete safety framework,
- or a guarantee that an AI agent is safe.

They are deterministic local demo artifacts designed to make action-gate decisions inspectable, replayable, and reviewable.

## Related docs

- [`paid_review_demo_reviewer_checklist.md`](paid_review_demo_reviewer_checklist.md)
- [`web3_treasury_full_showcase_expected_output.md`](web3_treasury_full_showcase_expected_output.md)
- [`../examples/paid_review_demo_expected_output.md`](../examples/paid_review_demo_expected_output.md)
- [`architecture_diagram.md`](architecture_diagram.md)
