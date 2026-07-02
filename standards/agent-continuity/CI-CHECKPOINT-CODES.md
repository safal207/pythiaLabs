# CI Operational Checkpoint v0.1 Outcome Registry

Consumers MUST branch on `outcome` and `reason_code`, not on `detail`.

## Outcomes

| Outcome | Meaning |
|---|---|
| `CONTINUE` | The checkpoint is valid, lineage is coherent, the workspace matches, and the next step may resume as context-only work. |
| `REVALIDATE_WORKSPACE` | Repository identity matches, but base, head, or dirty-state evidence changed and must be re-observed. |
| `RESTART_REQUIRED` | The checkpoint cannot safely resume in the current workspace or failed schema/digest validation. |
| `IDEMPOTENT_REPLAY` | The same checkpoint was already consumed; no duplicate work should be created. |
| `REJECT_LINEAGE_MISMATCH` | Parent, sequence, trajectory, or rejected-approach continuity is inconsistent. |
| `REJECT_UNVERIFIED_COMPLETION` | Verification was completed without durable evidence, disappeared, or conflicts with the required verification set. |
| `REJECT_INVALID_AUTHORITY` | Continuity material attempted to carry action authority or bypass fresh authorization. |

## Reason codes

| Outcome | Reason code |
|---|---|
| `CONTINUE` | `CONTINUE_OK` |
| `REVALIDATE_WORKSPACE` | `WORKSPACE_STATE_CHANGED` |
| `RESTART_REQUIRED` | `SCHEMA_INVALID`, `DIGEST_MISMATCH`, `WORKSPACE_IDENTITY_MISMATCH` |
| `IDEMPOTENT_REPLAY` | `CHECKPOINT_ALREADY_CONSUMED` |
| `REJECT_LINEAGE_MISMATCH` | `ROOT_HAS_PARENT`, `PARENT_REQUIRED`, `PARENT_NOT_FOUND`, `PARENT_MISMATCH`, `SEQUENCE_MISMATCH`, `TRAJECTORY_CHANGED`, `REJECTED_APPROACH_LOST` |
| `REJECT_UNVERIFIED_COMPLETION` | `VERIFICATION_ID_DUPLICATED`, `VERIFICATION_SET_MISMATCH`, `COMPLETION_EVIDENCE_MISSING`, `MEMORY_IS_NOT_VERIFICATION`, `COMPLETED_VERIFICATION_LOST` |
| `REJECT_INVALID_AUTHORITY` | `AUTHORITY_NOT_CONTEXT_ONLY`, `FRESH_AUTHORITY_REQUIRED` |

Within version `0.1`, existing reason codes MUST NOT change meaning.
