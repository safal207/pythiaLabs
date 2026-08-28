# CI Operational Checkpoint v0.1 Outcome Registry

Consumers MUST branch on `outcome` and `reason_code`, not on `detail`.

## Outcomes

| Outcome | Meaning |
|---|---|
| `CONTINUE` | The checkpoint is valid, lineage is coherent, the workspace matches, and the next step may resume as context-only work. |
| `REVALIDATE_WORKSPACE` | Repository identity matches, but required workspace evidence is missing or base, head, or dirty-state evidence changed. |
| `RESTART_REQUIRED` | The checkpoint cannot safely resume in the current workspace or failed schema/digest validation. |
| `IDEMPOTENT_REPLAY` | The same checkpoint was already consumed; no duplicate work should be created. |
| `REJECT_LINEAGE_MISMATCH` | Parent, checkpoint identity, time, objective, constraints, sequence, trajectory, rejected-approach continuity, or parent integrity is inconsistent. |
| `REJECT_UNVERIFIED_COMPLETION` | Verification was completed without durable evidence, disappeared, or conflicts with prior proof or pending-work lineage. |
| `REJECT_INVALID_AUTHORITY` | Continuity material attempted to carry action authority or bypass fresh authorization. |

## Reason codes

| Outcome | Reason code |
|---|---|
| `CONTINUE` | `CONTINUE_OK` |
| `REVALIDATE_WORKSPACE` | `WORKSPACE_STATE_CHANGED`, `CURRENT_WORKSPACE_FIELD_MISSING` |
| `RESTART_REQUIRED` | `SCHEMA_INVALID`, `DIGEST_MISMATCH`, `WORKSPACE_IDENTITY_MISMATCH`, `CURRENT_WORKSPACE_FIELD_MISSING` |
| `IDEMPOTENT_REPLAY` | `CHECKPOINT_ALREADY_CONSUMED` |
| `REJECT_LINEAGE_MISMATCH` | `ROOT_HAS_PARENT`, `PARENT_REQUIRED`, `PARENT_NOT_FOUND`, `PREVIOUS_CHECKPOINT_REQUIRED`, `PREVIOUS_CHECKPOINT_SCHEMA_INVALID`, `PREVIOUS_CHECKPOINT_DIGEST_MISMATCH`, `PREVIOUS_CHECKPOINT_SEMANTIC_INVALID`, `CHECKPOINT_ID_REUSED`, `PARENT_MISMATCH`, `SEQUENCE_MISMATCH`, `TRAJECTORY_CHANGED`, `CREATION_TIME_REGRESSED`, `OBJECTIVE_CHANGED`, `CONSTRAINT_LOST`, `REJECTED_APPROACH_ID_DUPLICATED`, `REJECTED_APPROACH_LOST`, `REJECTED_APPROACH_CHANGED` |
| `REJECT_UNVERIFIED_COMPLETION` | `VERIFICATION_ID_DUPLICATED`, `VERIFICATION_SET_MISMATCH`, `COMPLETION_EVIDENCE_MISSING`, `MEMORY_IS_NOT_VERIFICATION`, `COMPLETED_VERIFICATION_LOST`, `COMPLETED_VERIFICATION_CHANGED`, `PENDING_VERIFICATION_LOST`, `PENDING_VERIFICATION_CHANGED` |
| `REJECT_INVALID_AUTHORITY` | `AUTHORITY_NOT_CONTEXT_ONLY`, `FRESH_AUTHORITY_REQUIRED` |

Within version `0.1`, existing reason codes MUST NOT change meaning.
