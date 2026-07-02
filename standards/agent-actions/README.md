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
  pull-request snapshot into Action Envelope V1 for an exact-target
  `merge_pull_request` decision;
- [`schema/github-pr-merge-gate-input.schema.json`](schema/github-pr-merge-gate-input.schema.json)
  — strict adapter input contract;
- [`adapters/github_pr_merge_gate.py`](adapters/github_pr_merge_gate.py) —
  reference adapter and evaluator;
- [`conformance/test_github_pr_merge_gate.py`](conformance/test_github_pr_merge_gate.py)
  — base/head identity, freshness, replay, authorization, and recovery regressions;
- [`GUARDED-GITHUB-MERGE.md`](GUARDED-GITHUB-MERGE.md) — pre-execution
  orchestration that reserves the semantic action, rechecks base and head, and
  only then reaches an injected merge executor;
- [`adapters/guarded_github_merge.py`](adapters/guarded_github_merge.py) —
  reference execution boundary with retryable pre-execution reservations;
- [`conformance/test_guarded_github_merge.py`](conformance/test_guarded_github_merge.py)
  — executor reachability, double target-check, retry, replay, and failure tests.

## Quick validation

```bash
python -m pip install -r standards/agent-actions/conformance/requirements.txt

python -m unittest discover \
  -s standards/agent-actions/conformance \
  -p 'test_*.py' \
  -v
```

## Current guarantees

The reference slice checks schema versioning, strict shape, canonical digest,
temporal ordering, full authorization binding, evidence action/freshness,
preconditions, replay detection, recovery readiness, and deterministic
`ALLOW / BLOCK / ESCALATE` outcomes.

The GitHub merge-gate adapter binds action identity, authorization target,
idempotency, and expected transition to the exact repository, PR, base ref, and
head SHA. Checks and reviews remain exact-head bound.

The guarded merge service additionally guarantees:

- missing or cross-target evidence blocks before external state lookup;
- current GitHub base and head are checked before evaluation and execution;
- the semantic idempotency key is reserved before the second target check;
- transient second-read outages release the reservation for retry;
- an injected merge executor is unreachable unless the gate returned `ALLOW`;
- repeated, concurrent, or retargeted execution is blocked.

## Non-claims

This is not an internet standard, production identity system, compliance
certification, universal policy language, GitHub App, branch-protection
replacement, production merge queue, or safety guarantee.

The caller remains responsible for production GitHub authentication,
trustworthy identity, durable atomic replay storage, policy correctness,
conditional merge execution, and post-execution verification.
