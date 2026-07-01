# Agent Action Protocol Surface

A bounded, vendor-neutral experimental contract for evaluating one proposed
high-risk agent action before a tool call.

## Boundary

This package is intentionally separate from
[`standards/agent-continuity`](../agent-continuity/):

- the **Verifiable Continuation Envelope** preserves a trustworthy operational
  tail across compaction, restart, or handoff;
- **Action Envelope V1** describes one proposed external side effect and the
  evidence needed to decide whether it may proceed.

A continuation envelope must not be treated as authorization to execute an
action. An action envelope must not be treated as durable memory of a session.

## Package

- [`ACTION-ENVELOPE-V1.md`](ACTION-ENVELOPE-V1.md) — protocol semantics and
  decision flow;
- [`schema/action-envelope-v1.schema.json`](schema/action-envelope-v1.schema.json)
  — JSON Schema draft 2020-12;
- [`examples/action-envelope-v1.example.json`](examples/action-envelope-v1.example.json)
  — complete valid example;
- [`conformance/action_envelope_reference.py`](conformance/action_envelope_reference.py)
  — deterministic reference evaluator;
- [`conformance/test_action_envelope_conformance.py`](conformance/test_action_envelope_conformance.py)
  — executable conformance checks;
- [`DECISION_CODES.md`](DECISION_CODES.md) — stable decision and reason-code registry.

## Quick validation

```bash
python -m pip install -r standards/agent-actions/conformance/requirements.txt

python -m unittest discover \
  -s standards/agent-actions/conformance \
  -p 'test_*.py' \
  -v
```

## Current guarantees

The reference slice checks:

- explicit schema versioning;
- strict shape validation;
- canonical SHA-256 envelope integrity;
- authorization binding to agent, capability, target, and environment;
- authorization validity at `decision_time`;
- evidence binding to the intended `action_id`;
- evidence freshness at `decision_time`;
- precondition evidence references;
- deterministic `ALLOW`, `BLOCK`, and `ESCALATE` outcomes;
- duplicate idempotency-key detection supplied by the caller;
- rollback readiness when rollback is declared mandatory.

## Non-claims

This is an experimental local conformance package. It is not:

- an internet standard;
- a production identity, IAM, or cryptographic system;
- a regulatory compliance certification;
- a universal policy language;
- a guarantee that an allowed action is safe;
- an execution engine.

The caller remains responsible for trustworthy identity, durable replay
storage, policy correctness, tool enforcement, and post-execution verification.
