# OpenHands-compatible Evidence Gate Decision Event

Status: experimental interoperability note, not an OpenHands feature or endorsement.

## Purpose

This note defines an optional reviewer-facing event that can be emitted after an action has been assessed and before its tool call is dispatched.

It does not replace the OpenHands security analyzer, policy rails, confirmation policy, event log, sandboxing, or human review. It only packages the decision context into one exportable record.

## Why a separate event

The current OpenHands `ActionEvent` already records the action identity, tool call, summary, model reasoning, and `security_risk`. Deterministic policy rails can also produce stable rule names and reasons.

The missing reviewer-facing unit is a single record that binds together:

- the evaluated `ActionEvent`;
- the security assessment;
- matched deterministic rules;
- evidence that was present, missing, stale, or redacted;
- an authorization decision;
- the runtime interaction used to satisfy that decision;
- the policy version and replay digests.

## Decision versus interaction

These concepts should remain separate:

| Policy decision | Meaning | Runtime interaction |
|---|---|---|
| `ALLOW` | The current evidence and policy permit dispatch. | Usually `NONE`. |
| `BLOCK` | A hard rule denies dispatch and cannot be overridden by ordinary confirmation. | `DENY`. |
| `ESCALATE` | The action may be valid but requires an authorized reviewer. | OpenHands can use `CONFIRM` to satisfy the escalation. |

`ESCALATE` is the decision; `CONFIRM` is the interaction mechanism.

## Mapping to OpenHands SDK concepts

| Proposed field | OpenHands source |
|---|---|
| `action_event_id` | `ActionEvent.id` |
| `timestamp` | event timestamp or gate-evaluation timestamp |
| `tool_call_id` | `ActionEvent.tool_call_id` |
| `tool_name` | `ActionEvent.tool_name` |
| `action_summary` | `ActionEvent.summary` |
| `security_assessment.risk` | `ActionEvent.security_risk` |
| `matched_rules[].rule_id` | stable policy-rail ID, external policy ID, or evidence-check ID |
| `matched_rules[].reason` | `RailDecision.reason` or equivalent deterministic reason |
| `gate_decision.runtime_interaction` | result expected from the confirmation policy |

## Suggested emission point

```text
ActionEvent created
-> security analyzer and deterministic rails evaluated
-> optional external policy/evidence checks evaluated
-> EvidenceGateDecisionEvent emitted
-> ALLOW dispatches, BLOCK denies, ESCALATE requests confirmation
```

The event can remain outside the LLM-visible conversation and be stored as a reviewer/export artifact.

## Minimal fields

```json
{
  "schema_version": "pythia.openhands.evidence_gate_decision.v0.1",
  "event_type": "evidence_gate_decision",
  "event_id": "gate_evt_01",
  "timestamp": "2026-06-19T10:00:00Z",
  "source": "security",
  "action_event_id": "action_evt_01",
  "tool_call_id": "tool_call_01",
  "tool_name": "terminal",
  "action_summary": "modify production deployment workflow",
  "security_assessment": {
    "risk": "HIGH",
    "basis": "ensemble"
  },
  "gate_decision": {
    "decision": "ESCALATE",
    "runtime_interaction": "CONFIRM",
    "decision_basis": "hybrid",
    "stop_reasons": [
      "OWNER_APPROVAL_REQUIRED",
      "PRODUCTION_SCOPE_REQUIRES_REVIEW"
    ]
  },
  "matched_rules": [],
  "evidence_refs": [],
  "policy_context": {
    "policy_id": "repo-production-change-policy",
    "policy_version": "1",
    "policy_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "replay": {
    "replayable": true,
    "canonical_input_digest": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "decision_digest": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
  },
  "sensitive_data_redacted": true
}
```

## Concrete reviewer scenario

An agent proposes changing a production deployment workflow and rotating a secret reference.

A normal trajectory can show the command, reasoning, risk, and human confirmation. The decision event additionally answers:

1. Was the workflow in the authorized task scope?
2. Was only a secret reference changed, or was secret material read?
3. Which rule required approval?
4. Which evidence was missing at decision time?
5. Which policy version produced the decision?
6. Can the same normalized inputs be replayed against that policy version?

## Non-claims

This experimental event does not prove that an action is correct, secure, compliant, or safe. It does not define production authorization, identity verification, or cryptographic signing. It is a small interoperability proposal for structured review and replay.
