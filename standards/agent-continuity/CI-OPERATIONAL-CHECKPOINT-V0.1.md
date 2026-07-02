# CI Operational Checkpoint v0.1

- **Status:** Draft
- **Profile:** `pythia.ci_operational_checkpoint.v0.1`
- **Parent:** [RFC-001](RFC-001-VERIFIABLE-CONTINUATION-ENVELOPE.md)
- **Scope:** CI/CD phase transitions, retries, restart, and agent handoff

## Purpose

This profile defines a bounded checkpoint for resuming delivery work without
reconstructing state from narrative memory and without inheriting authority for
a consequential action.

```text
validate schema and digest
  -> check replay
  -> validate parent checkpoint and lineage
  -> preserve objective, constraints, rejected rationale, and verification proof
  -> compare current workspace
  -> CONTINUE | REVALIDATE | RESTART | IDEMPOTENT_REPLAY | REJECT
```

## Core boundary

> Context may continue. Authority must be evaluated again.

`authority` is fixed to `context_only`. Merge and deploy intent MUST set
`requires_fresh_authority=true`. A checkpoint never replaces an Action Envelope,
current checks, current reviews, or an executor guard.

## Required content

A conforming checkpoint records trajectory and parent identity, source agent and
session, repository and workspace identity, objective, phase, constraints,
rejected approaches, touched resources, verification state, the next action,
and a canonical SHA-256 digest. `dirty_state_digest` is optional.

The strict schema is
[`schema/ci-operational-checkpoint-v0.1.schema.json`](schema/ci-operational-checkpoint-v0.1.schema.json).

## Active-state continuity

Within one trajectory:

- child creation time MUST NOT precede parent creation time;
- objective and acceptance criteria MUST remain unchanged;
- every prior `must` and `must_not` constraint MUST remain active;
- every rejected approach row and rationale MUST remain unchanged;
- every completed verification target and prior evidence reference MUST remain;
- every pending verification MUST remain with the same target or move to
  completed with durable evidence.

Constraints and evidence may be added. Existing active state and proof may not be
silently removed or rewritten. A changed objective requires a new trajectory.

## Verification boundary

Completed verification requires durable evidence. Memory and agent summaries
are not verification evidence, regardless of URI-scheme letter case. Additional
evidence may be appended, but existing evidence cannot be removed or replaced.

## Parent-checkpoint integrity

Every non-root resume requires the full previous checkpoint. A known parent ID
alone is insufficient because it cannot prove active-state or verification
continuity.

Before comparison, the previous checkpoint MUST pass schema validation,
canonical digest verification, identifier uniqueness, verification-set
consistency, and the memory-evidence boundary. Invalid or missing parent material
returns `REJECT_LINEAGE_MISMATCH`.

Durable lookup and storage remain follow-up work in issue #223.

## Workspace comparison

A repository or working-directory mismatch returns `RESTART_REQUIRED`. Changes
to base ref, head SHA, or a declared dirty-state digest return
`REVALIDATE_WORKSPACE`.

When the checkpoint declares `dirty_state_digest`, the resumed runtime MUST
explicitly report it, including `null` for an observed clean workspace. Missing
observation returns `CURRENT_WORKSPACE_FIELD_MISSING`. If the checkpoint omits
the field, it is outside the comparison boundary.

## Replay

A consumed checkpoint ID returns `IDEMPOTENT_REPLAY`; completed work must not be
repeated.

## Relationship to Action Envelope V1

The checkpoint says what context and verification state to restore. Action
Envelope V1 decides whether an exact consequential action may execute now. The
contracts are complementary and non-substitutable.

## Reference files

- example: [`examples/ci-operational-checkpoint-v0.1.example.json`](examples/ci-operational-checkpoint-v0.1.example.json)
- evaluator: [`conformance/ci_operational_checkpoint_reference.py`](conformance/ci_operational_checkpoint_reference.py)
- tests: [`conformance/test_ci_operational_checkpoint.py`](conformance/test_ci_operational_checkpoint.py)
- codes: [`CI-CHECKPOINT-CODES.md`](CI-CHECKPOINT-CODES.md)

## Non-claims

This profile is not durable storage, a distributed lease, proof of execution, or
permission for a tool call.
