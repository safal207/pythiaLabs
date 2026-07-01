# Action Envelope V1 Decision Codes

The reference evaluator returns:

```json
{
  "decision": "ALLOW | BLOCK | ESCALATE",
  "reason_code": "STABLE_MACHINE_CODE",
  "detail": "human-readable context"
}
```

Consumers should branch on `decision` and `reason_code`, not on `detail`.

| Decision | Reason code | Meaning |
|---|---|---|
| `ALLOW` | `ALLOW_OK` | Every declared check in the bounded evaluator passed. |
| `BLOCK` | `UNSUPPORTED_SCHEMA_VERSION` | `schema_version` is not supported. |
| `BLOCK` | `SCHEMA_INVALID` | The document violates the published schema or a uniqueness invariant. |
| `BLOCK` | `DIGEST_MISMATCH` | Canonical envelope digest verification failed. |
| `BLOCK` | `AUTHORIZATION_MISMATCH` | The grant is not bound to the proposed agent, capability, target, or environment. |
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

## Compatibility rule

Within schema version `1.0`, existing reason codes must not change meaning.
Adding a code requires:

1. documenting it here;
2. adding a conformance test;
3. preserving fail-closed behavior for consumers that do not recognize it.
