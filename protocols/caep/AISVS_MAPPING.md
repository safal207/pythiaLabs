# CAEP mapping to OWASP AISVS discussion areas

This note is an implementation-oriented mapping, not an assertion of formal OWASP endorsement.

## C05 — Authentication and authorization

CAEP complements external policy-decision-point controls by carrying the exact authorization forward to dispatch:

- policy version;
- authorized target;
- parameter hash;
- boundary identifier;
- credential class;
- permitted network destinations;
- expiry and single-use nonce.

The semantic validator rejects dispatch drift instead of treating authorization as a detached log event.

## C09 — Orchestration and agentic action

CAEP makes an agent action testable as a complete episode:

- intent is content-bound;
- dispatch is compared with the authorization immediately before execution;
- outcomes record observable side effects rather than only model-generated summaries;
- causal-parent links reconstruct multi-step trajectories;
- reversibility is represented independently from impact.

Suggested verification language:

> Verify that every consequence-bearing agent action preserves an independently auditable binding from exact intent and authorization through actual dispatch and terminal outcome, and that any target, parameter, credential, destination, or execution-boundary mismatch fails closed or escalates before execution.

## C12 / AI Incident Response appendix

CAEP adds incident-specific evidence beyond general runtime logs:

- a dispatched action without a terminal outcome becomes an incident signal;
- `valid_time` and `transaction_time` preserve what was true versus what was known;
- recovery records distinguish procedure execution from achieved recovery;
- residual external effects and unresolved dependencies remain visible;
- supersession records correct history without rewriting it.

Suggested recovery language:

> Verify that containment, credential revocation, rollback, or quarantine emits a recovery record binding the recovery objective, resulting state digest, residual effects, and unresolved dependencies. The presence or invocation of a recovery mechanism alone must not be treated as evidence that recovery succeeded.

## Minimal adversarial tests

An implementation should fail or escalate when:

1. parameters change after approval;
2. an internal target redirects to an unauthorized external destination;
3. the runtime switches credential class;
4. authorization expires before dispatch;
5. a dispatched action has no outcome;
6. a child action has no admissible causal parent;
7. rollback runs but the recovery objective is not met;
8. a prior record is replaced rather than superseded.
