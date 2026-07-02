# Action Envelope V1 Decision Codes

The reference evaluator returns:

```json
{
  "decision": "ALLOW | BLOCK | ESCALATE",
  "reason_code": "STABLE_MACHINE_CODE",
  "detail": "human-readable context"
}
```

The guarded GitHub merge service additionally returns `reason_codes`, currently
a one-element array containing the same stable code. Consumers should branch on
`decision` and `reason_code`, not on `detail`.

## Action Envelope V1 codes

| Decision | Reason code | Meaning |
|---|---|---|
| `ALLOW` | `ALLOW_OK` | Every declared check in the bounded evaluator passed. |
| `BLOCK` | `UNSUPPORTED_SCHEMA_VERSION` | `schema_version` is not supported. |
| `BLOCK` | `SCHEMA_INVALID` | The document violates the published schema or a uniqueness invariant. |
| `BLOCK` | `DIGEST_MISMATCH` | Canonical envelope digest verification failed. |
| `BLOCK` | `DECISION_BEFORE_CREATION` | `decision_time` is earlier than `created_at`. |
| `BLOCK` | `AUTHORIZATION_MISMATCH` | The grant is not bound to the proposed actor, agent, capability, operation, target, or environment. |
| `BLOCK` | `AUTHORIZATION_NOT_YET_VALID` | The grant begins after `decision_time`. |
| `BLOCK` | `AUTHORIZATION_EXPIRED` | The grant ended before `decision_time`. |
| `BLOCK` | `EVIDENCE_ACTION_MISMATCH` | Evidence is bound to another `action_id`. |
| `BLOCK` | `EVIDENCE_NOT_YET_VALID` | Evidence was observed after `decision_time`. |
| `BLOCK` | `EVIDENCE_STALE` | Evidence expired before `decision_time`. |
| `BLOCK` | `UNKNOWN_EVIDENCE_REF` | A precondition references evidence absent from the envelope. |
| `BLOCK` | `PRECONDITION_FAILED` | A declared precondition failed. |
| `BLOCK` | `REPLAY_DETECTED` | The caller reports that the idempotency key was already observed. |
| `ESCALATE` | `PRECONDITION_UNRESOLVED` | A declared precondition remains unknown. |
| `ESCALATE` | `RECOVERY_NOT_READY` | Rollback is mandatory but unavailable. |

## GitHub merge-gate adapter codes

| Decision | Reason code | Meaning |
|---|---|---|
| `BLOCK` | `GITHUB_INPUT_INVALID` | The GitHub snapshot violates the strict adapter schema or a semantic uniqueness invariant. |

The adapter can also return Action Envelope V1 codes after constructing and
evaluating the envelope.

## Guarded GitHub merge execution codes

| Decision | Reason code | Meaning |
|---|---|---|
| `BLOCK` | `REQUIRED_EVIDENCE_MISSING` | A required check or required reviewer is absent. |
| `BLOCK` | `EVIDENCE_TARGET_MISMATCH` | A workflow or review locator belongs to another repository or pull request. |
| `BLOCK` | `HEAD_SHA_MISMATCH` | The current pull-request head differs from the proposed exact head before evaluation. |
| `BLOCK` | `ACTION_ALREADY_IN_PROGRESS` | The semantic idempotency key is already reserved by another execution. |
| `BLOCK` | `ACTION_ALREADY_EXECUTED` | The semantic idempotency key is already in a terminal state. |
| `BLOCK` | `TARGET_CHANGED_BEFORE_EXECUTION` | The pull-request head changed after `ALLOW` and before the executor call. |
| `ESCALATE` | `CURRENT_STATE_UNAVAILABLE` | Current GitHub state could not be retrieved or revalidated. |
| `BLOCK` | `EXECUTION_FAILED` | The injected merge executor failed and the action was recorded as failed. |

The guarded service can also return adapter or Action Envelope V1 codes when a
lower layer rejects the action.

## Compatibility rule

Within schema version `1.0`, existing reason codes must not change meaning.
Adding a code requires:

1. documenting it here;
2. adding a conformance test;
3. preserving fail-closed behavior for consumers that do not recognize it.
