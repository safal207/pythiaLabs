# OpenHands-compatible Evidence Gate Receipt Protocol v0.2

Status: experimental interoperability note, not an OpenHands feature or endorsement.

## Purpose

This note defines an optional reviewer-facing, two-phase record for high-impact
agent actions:

1. a pre-action decision event emitted after security and policy evaluation but
   before tool dispatch;
2. a post-action verification event emitted after an observation or artifact is
   available;
3. a reviewer receipt projected from those append-only records.

It does not replace the OpenHands security analyzer, policy rails, confirmation
policy, event log, hooks, sandboxing, or human review. It packages decision and
verification context into exportable records that can be inspected without
reconstructing the full trajectory.

## Why two phases

Authorization and verification happen at different times.

```text
proposed action
-> security / policy / evidence evaluation
-> EvidenceGateDecisionEvent
-> ALLOW | BLOCK | ESCALATE
-> optional confirmation
-> tool dispatch
-> ObservationEvent or rejection
-> verification command / reviewer check
-> EvidenceGateVerificationEvent
-> reviewer receipt projection
```

The pre-action decision must not be rewritten after dispatch merely to attach a
test result. Keeping decision and verification as separate linked events
preserves an append-only audit model and makes the timing of each claim explicit.

## Decision versus interaction

These concepts remain separate:

| Policy decision | Meaning | Runtime interaction |
|---|---|---|
| `ALLOW` | Current evidence and policy permit dispatch. | Usually `NONE`. |
| `BLOCK` | A hard rule denies dispatch and cannot be overridden by ordinary confirmation. | `DENY`. |
| `ESCALATE` | The action may be valid but requires an authorized reviewer. | OpenHands may use `CONFIRM` to satisfy the escalation. |

`ESCALATE` is the policy decision. `CONFIRM` is the runtime interaction used to
resolve it.

## Record 1: EvidenceGateDecisionEvent

The decision event is emitted before the tool call is dispatched.

It binds:

- the evaluated action and tool-call identity;
- OpenHands security risk;
- matched deterministic rules;
- evidence that was present, missing, stale, or redacted;
- `ALLOW`, `BLOCK`, or `ESCALATE`;
- runtime interaction;
- stable stop reasons;
- policy version and hash;
- replay digests;
- a shared `receipt_id`;
- whether post-action verification is required.

Latest schema:

[`../../schemas/integrations/openhands_evidence_gate_decision_event.schema.json`](../../schemas/integrations/openhands_evidence_gate_decision_event.schema.json)

The previous v0.1 schema is retained for compatibility:

[`../../schemas/integrations/openhands_evidence_gate_decision_event.v0.1.schema.json`](../../schemas/integrations/openhands_evidence_gate_decision_event.v0.1.schema.json)

## Record 2: EvidenceGateVerificationEvent

The verification event is emitted only after the action has produced an
observation, rejection, or reviewable artifact.

It records:

- the `receipt_id` and gate event being verified;
- action, tool-call, and observation event IDs;
- verifier type, identity, and version;
- the verification command and its normalized digest;
- `PASS`, `FAIL`, `ERROR`, or `SKIPPED`;
- exit code and summary where applicable;
- output references and result digest;
- evidence references used during verification.

Schema:

[`../../schemas/integrations/openhands_evidence_gate_verification_event.schema.json`](../../schemas/integrations/openhands_evidence_gate_verification_event.schema.json)

A verification event is not proof that an action was safe or correct. It only
records that a named verification procedure produced a particular result.

## Reviewer receipt

The receipt is a projection joining the linked records. It is not the mutable
source of truth.

The receipt gives a reviewer one compact path:

```text
final diff / report / observation
-> verification event
-> executed action
-> pre-action decision
-> matched policy and checked evidence
```

It includes:

- action and final-artifact references;
- decision event ID and digest;
- policy ID, version, and hash;
- verification event ID and digest;
- verifier and result digest;
- an ordered trace chain;
- a `complete` flag.

Schema:

[`../../schemas/integrations/openhands_evidence_gate_receipt.schema.json`](../../schemas/integrations/openhands_evidence_gate_receipt.schema.json)

## Mapping to OpenHands SDK concepts

| Protocol field | OpenHands source or integration point |
|---|---|
| `action_event_id` | `ActionEvent.id` |
| `tool_call_id` | `ActionEvent.tool_call_id` |
| `tool_name` | `ActionEvent.tool_name` |
| `action_summary` | `ActionEvent.summary` |
| `security_assessment.risk` | `ActionEvent.security_risk` |
| `matched_rules[].rule_id` | stable policy-rail ID, hook rule ID, external policy ID, or evidence-check ID |
| `observation_event_id` | `ObservationEvent.id` or a rejection observation ID |
| verification observation link | `ObservationEvent.action_id` plus `tool_call_id` |
| runtime denial | `UserRejectObservation`, including hook or user rejection source |
| `runtime_interaction` | confirmation-policy or hook interaction result |
| final artifact reference | diff, log, report, or other exported artifact produced by the workflow |

## Example records

- [Decision event v0.2](../examples/openhands-evidence-gate-decision-v0.2.json)
- [Verification event v0.1](../examples/openhands-evidence-gate-verification-v0.1.json)
- [Reviewer receipt v0.1](../examples/openhands-evidence-gate-receipt-v0.1.json)

The examples describe an agent changing a production deployment workflow,
receiving an escalation decision, obtaining confirmation, running a test
command, and exporting a receipt that links the final diff back to the
pre-action evidence.

## Integrity semantics

The schemas use SHA-256-shaped digest fields to make the intended linkage
explicit. They do not define canonicalization, signing, key management,
identity assurance, or trusted timestamping.

A production implementation would still need to define:

- canonical serialization;
- digest scope;
- verifier identity and authorization;
- policy distribution and trust;
- secure storage;
- signature and timestamp semantics;
- redaction rules;
- failure handling for incomplete receipts.

## Versioning

- Decision event v0.1 remains available as a compatibility snapshot.
- Decision event v0.2 adds `receipt_id` and `verification_required`.
- Verification event v0.1 introduces the post-action record.
- Receipt v0.1 introduces the reviewer-facing projection.

Future versions should add fields rather than reinterpret existing decisions.
A receipt should never change the meaning of the original gate event.

## Non-claims

This experimental protocol does not prove that an action is correct, secure,
compliant, authorized in production, or safe. It does not define production
identity verification, cryptographic signing, enforcement, or certification.

It is a small interoperability proposal for structured review, traceability,
and replay around existing agent-security primitives.
