# CI Operational Checkpoint v0.1

- **Status:** Draft
- **Profile:** `pythia.ci_operational_checkpoint.v0.1`
- **Parent:** [RFC-001 — Verifiable Continuation Envelope](RFC-001-VERIFIABLE-CONTINUATION-ENVELOPE.md)
- **Scope:** Agentic CI/CD phase transitions, review waits, retries, restart, and handoff

## 1. Purpose

This profile defines a bounded checkpoint for resuming CI/CD work without
reconstructing state from a narrative summary and without inheriting authority
to merge, deploy, send, publish, or invoke another consequential tool.

```text
checkpoint context
  -> validate schema and digest
  -> validate lineage
  -> preserve rejected approaches
  -> preserve required verification
  -> compare current workspace
  -> CONTINUE | REVALIDATE | RESTART | REJECT
```

## 2. Core boundary

> Context may continue. Authority must be evaluated again.

`authority` is fixed to `context_only`. A checkpoint can carry an exact next
action, including the intent to merge or deploy, but those action classes MUST
set `requires_fresh_authority=true`. The checkpoint never replaces an Action
Envelope, current checks, current reviews, or an executor guard.

## 3. Required content

A conforming checkpoint records:

- trajectory, checkpoint, parent, and sequence identity;
- source agent and session;
- exact repository, working directory, base ref, head SHA, and optional
  dirty-state digest;
- goal and acceptance criteria;
- current delivery phase;
- active `must` and `must_not` constraints;
- rejected approaches with reasons;
- touched resources;
- required, completed, and pending verification;
- one exact next action;
- canonical SHA-256 digest.

The strict schema is
[`schema/ci-operational-checkpoint-v0.1.schema.json`](schema/ci-operational-checkpoint-v0.1.schema.json).

## 4. Verification boundary

A verification item may appear in `completed` only when it carries at least one
durable evidence reference. Narrative memory and agent summaries are not
verification evidence. The required verification set must equal the union of
completed and pending IDs.

A later checkpoint must not:

- drop a previously completed verification;
- drop a rejected approach;
- silently mark pending work completed without evidence;
- change trajectory or skip sequence;
- point at the wrong parent.

## 5. Workspace comparison

Repository or working-directory mismatch returns `RESTART_REQUIRED`.

Changes to base ref, head SHA, or dirty-state digest return
`REVALIDATE_WORKSPACE`. The resumed agent must inspect the changed workspace and
create a new checkpoint before consequential work continues.

## 6. Replay

A consumed checkpoint ID returns `IDEMPOTENT_REPLAY`. The caller should not
repeat completed work or create duplicate side effects.

## 7. Relationship to Action Envelope V1

The checkpoint answers:

```text
What context and verification state should the next agent restore?
```

Action Envelope V1 answers:

```text
May this exact consequential action execute now?
```

The two contracts are complementary and deliberately non-substitutable.

## 8. Reference implementation

- example checkpoint:
  [`examples/ci-operational-checkpoint-v0.1.example.json`](examples/ci-operational-checkpoint-v0.1.example.json);
- deterministic evaluator:
  [`conformance/ci_operational_checkpoint_reference.py`](conformance/ci_operational_checkpoint_reference.py);
- executable tests:
  [`conformance/test_ci_operational_checkpoint.py`](conformance/test_ci_operational_checkpoint.py);
- stable outcomes:
  [`CI-CHECKPOINT-CODES.md`](CI-CHECKPOINT-CODES.md).

## 9. Non-claims

This profile is not durable storage, a distributed lease, a workflow engine, an
identity system, proof that an action occurred, or permission to perform a tool
call. Durable coordination is tracked separately in issue #223.
