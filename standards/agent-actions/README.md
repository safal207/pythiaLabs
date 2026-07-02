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

## Reference adapters and enforcement

- [`GITHUB-PR-MERGE-GATE.md`](GITHUB-PR-MERGE-GATE.md) — maps a bounded GitHub
  pull-request snapshot into Action Envelope V1 for an exact-head
  `merge_pull_request` decision;
- [`schema/github-pr-merge-gate-input.schema.json`](schema/github-pr-merge-gate-input.schema.json)
  — strict adapter input contract;
- [`adapters/github_pr_merge_gate.py`](adapters/github_pr_merge_gate.py) —
  reference adapter and evaluator;
- [`conformance/test_github_pr_merge_gate.py`](conformance/test_github_pr_merge_gate.py)
  — exact-head, freshness, replay, authorization, and recovery regressions;
- [`GUARDED-GITHUB-MERGE.md`](GUARDED-GITHUB-MERGE.md) — pre-execution
  orchestration that reserves the semantic action, rechecks the target, and only
  then reaches an injected merge executor;
- [`adapters/guarded_github_merge.py`](adapters/guarded_github_merge.py) —
  reference execution boundary with in-memory replay state;
- [`conformance/test_guarded_github_merge.py`](conformance/test_guarded_github_merge.py)
  — executor reachability, double head-check, replay, and failure regressions.

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

- explicit schema versioning with malformed-versus-unsupported classification;
- strict unknown-field and required-field validation;
- canonical SHA-256 envelope integrity;
- temporal ordering that rejects `decision_time` earlier than `created_at`;
- authorization binding to initiating actor, executing agent, capability,
  operation, target, and environment;
- authorization validity at `decision_time`, including both time-window bounds;
- evidence binding to the intended `action_id`;
- evidence freshness at `decision_time`, including both time-window bounds;
- unique evidence identifiers and valid precondition evidence references;
- deterministic `ALLOW`, `BLOCK`, and `ESCALATE` outcomes;
- duplicate idempotency-key detection supplied by the caller;
- rollback readiness when rollback is declared mandatory.

The GitHub merge-gate adapter additionally binds the action identity,
authorization target, evidence, idempotency key, and expected transition to one
exact pull-request head SHA. Checks or reviews from another head do not authorize
the proposed merge.

The guarded merge service adds an enforceable call-order property:

- missing required evidence blocks before external state is loaded;
- current GitHub head is checked before evaluation and before execution;
- the semantic idempotency key is reserved before the second head check;
- an injected merge executor is unreachable unless the gate returned `ALLOW`;
- repeated or concurrent execution is blocked.

## Non-claims

This is an experimental local conformance package. It is not:

- an internet standard;
- a production identity, IAM, or cryptographic system;
- a regulatory compliance certification;
- a universal policy language;
- a guarantee that an allowed action is safe;
- a production execution engine;
- a GitHub App, branch-protection replacement, or production merge queue.

The reference executor boundary uses injected interfaces and an in-memory store.
The caller remains responsible for production GitHub authentication, trustworthy
identity, durable atomic replay storage, policy correctness, conditional merge
execution, and post-execution verification.
