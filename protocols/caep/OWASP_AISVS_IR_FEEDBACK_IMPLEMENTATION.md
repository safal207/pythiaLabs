# OWASP AISVS feedback implementation: gate path and recovery semantics

Status: implemented proposal refinement  
Related discussion: [OWASP/AISVS #1083](https://github.com/OWASP/AISVS/issues/1083)  
Related follow-up: [OWASP/AISVS #1111](https://github.com/OWASP/AISVS/issues/1111)  
Reference implementation: CAEP v0.1 OWASP IR validation profile

## Why this refinement exists

Community feedback on the AISVS AI Incident Response discussion identified two places where the original CAEP proposal was too implicit:

1. an investigator should be able to see which authorization gate path an action took, rather than infer it from multiple records;
2. recovery expectations must depend on the action's reversibility class.

The evidence trust boundary remains external to the executing agent runtime. A runtime-controlled log is useful operational telemetry, but it is not sufficient high-assurance incident evidence when the same runtime can omit, revise, or self-attest to its own records.

## Explicit gate path

Authorization records may now carry:

```json
{
  "decision": "ALLOW",
  "gate_path": "AUTO_EXECUTED"
}
```

Allowed values:

| Decision | Required gate path |
| --- | --- |
| `ALLOW` | `AUTO_EXECUTED` |
| `REQUIRE_APPROVAL` | `APPROVAL_GATED` |
| `DENY` | `BLOCKED` |
| `REVISE` | `ESCALATED` |

The OWASP IR validator:

- emits an evidence warning when `gate_path` is absent, preserving CAEP v0.1 compatibility;
- fails closed for an unknown gate path;
- rejects a gate path that conflicts with the authorization decision.

This makes denied-before-dispatch and approval-gated actions directly visible to incident responders.

## Reversibility-conditioned recovery

The recovery contract is conditioned on `reversibility_class`.

### `REVERSIBLE` and `EXTERNAL_REVERSIBLE`

When containment is required:

- one terminal recovery record is required;
- a failed recovery remains a structurally valid evidence packet;
- the validator emits an explicit security finding when the recovery objective was not met.

This separates **evidence validity** from **system safety**: a valid packet may truthfully prove that recovery failed.

### `IRREVERSIBLE`

An irreversible action does not falsely require a recovery record. Instead, the outcome must declare:

```json
{
  "incident_state": "NON_RECOVERABLE",
  "containment_status": "CONTAINED",
  "residual_effects": ["external effect cannot be rolled back"],
  "unresolved_dependencies": ["third-party confirmation"]
}
```

The validator requires:

- `incident_state = NON_RECOVERABLE`;
- an active or terminal containment status;
- at least one residual effect;
- an explicit unresolved-dependencies array.

Containment is still required and auditable. What is removed is the misleading claim that an irreversible consequence can be recovered.

## Candidate AISVS wording refinement

> Verify that each consequence-bearing AI-agent action records the authorization gate path taken, including whether the action was automatically executed, approval-gated, blocked, or escalated, and that this path is generated or attested outside the agent-controlled execution surface.

> Verify that recovery requirements are conditioned on the action's declared reversibility class. Reversible actions requiring containment must produce a terminal recovery result. Irreversible actions must instead record explicit non-recoverable incident state, containment status, residual effects, and unresolved dependencies.

> Verify that failure to recover a reversible action is reported as an incident finding and is not hidden by treating the evidence packet itself as invalid.

## Implementation

- companion schema: `schema/caep-ir-fields.schema.json`;
- validator: `tools/validate_caep_ir.py`;
- regression tests: `tests/test_owasp_ir_feedback.py`.

The companion schema keeps existing CAEP v0.1 packets compatible while making the new evidence fields independently testable before a future minor schema revision.

## AISVS placement

The refinement is intended to compose with:

- C09 action enforcement and execution-boundary controls, including the community reference to C9.5.3;
- the AI Incident Response appendix discussed in #1083;
- the C12.4.2 logging extension work referenced in #1111.

CAEP remains a vendor-neutral reference schema, offline validator, and test corpus. It is not proposed as a mandatory AISVS implementation.
