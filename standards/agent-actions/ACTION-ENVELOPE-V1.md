# Action Envelope V1

**Status:** Experimental v1.0 protocol surface  
**Scope:** Pre-execution evaluation of one proposed high-risk agent action  
**Related ADR:** [`../../docs/adr/ADR-001-machine-verifiable-agent-interactions.md`](../../docs/adr/ADR-001-machine-verifiable-agent-interactions.md)

## 1. Problem

Natural-language intent is not a sufficient execution contract for high-risk
agent actions. Before a tool is called, a gate needs an explicit answer to:

- who is proposing the action;
- what capability and operation are requested;
- which target and environment are affected;
- what authorization applies at decision time;
- which preconditions and evidence support the action;
- whether the request is fresh, replayed, or recoverable;
- which state transition is expected;
- why the gate returned `ALLOW`, `BLOCK`, or `ESCALATE`.

Action Envelope V1 provides a minimal shape for that decision boundary.

## 2. Governing principle

> An agent explanation may accompany an action, but it must not replace the
> machine-verifiable contract required to decide whether the action may proceed.

## 3. Lifecycle

```text
proposed action
  -> schema/version validation
  -> envelope digest verification
  -> authorization binding and time checks
  -> evidence action-binding and freshness checks
  -> precondition checks
  -> idempotency/replay check
  -> recovery readiness check
  -> ALLOW / BLOCK / ESCALATE
```

The envelope is evaluated **before** external side effects. A successful
`ALLOW` result is permission from this bounded evaluator only; it is not proof
that the tool executed or that the external result was correct.

## 4. Required top-level fields

| Field | Purpose |
|---|---|
| `schema_version` | Selects the protocol contract. V1 requires `1.0`. |
| `envelope_id` | Identifies this serialized proposal envelope. |
| `action_id` | Identifies the intended action and binds evidence to it. |
| `created_at` | Records when the proposal envelope was created. |
| `decision_time` | Defines the time at which temporal checks are evaluated. |
| `actor` | Identifies the initiating actor and executing agent. |
| `request` | Declares capability, operation, target, and environment. |
| `authorization` | Declares the actor- and action-bound grant used for this decision. |
| `preconditions` | Declares passed, failed, or unresolved conditions. |
| `evidence` | Carries durable references, action binding, provenance, and freshness. |
| `idempotency` | Declares a caller-checkable replay key and rejection policy. |
| `recovery` | Declares whether rollback is mandatory and currently available. |
| `expected_state_transition` | Declares the intended before/after state. |
| `envelope_digest` | Protects canonical envelope integrity. |

## 5. Schema-version classification

The evaluator distinguishes malformed input from a well-formed but unsupported
protocol version:

- a missing or non-string `schema_version` is `BLOCK / SCHEMA_INVALID`;
- a string version other than `1.0` is `BLOCK / UNSUPPORTED_SCHEMA_VERSION`.

This distinction is part of the machine-readable decision contract.

## 6. Canonical digest

The digest is SHA-256 over UTF-8 JSON after:

1. removing the top-level `envelope_digest` field;
2. sorting object keys recursively;
3. using compact separators `,` and `:`;
4. preserving array order;
5. rejecting NaN and non-JSON values.

The identifier for this procedure is `json-sort-keys-utf8-v1`.

The digest protects the serialized proposal against accidental or malicious
mutation. It does not authenticate the author. Production authorship requires a
separate trustworthy signature and identity system.

## 7. Authorization binding

The evaluator requires the authorization grant to match all of:

- `actor.actor_id`;
- `actor.agent_id`;
- `request.capability`;
- `request.operation`;
- `request.target`;
- `request.environment`.

`decision_time` must fall inclusively between `valid_from` and `valid_until`.

This narrow equality model is intentionally conservative. Wildcards, role
resolution, hierarchical resources, and delegated scope reduction are outside
this first slice.

## 8. Evidence semantics

Every evidence row contains:

- a unique `evidence_id`;
- the exact `action_id` it supports;
- a durable locator and SHA-256 digest;
- `observed_at` and `expires_at`;
- source provenance.

At decision time:

- evidence bound to another action is blocked;
- evidence observed after `decision_time` is blocked;
- evidence expired before `decision_time` is blocked;
- a precondition referencing unknown evidence is blocked.

The current slice validates the declared digest shape but does not fetch the
locator and recompute the external artifact digest. Integrations must perform
that independent verification before treating the evidence as trustworthy.

## 9. Preconditions

Each precondition is one of:

- `passed` — eligible to continue;
- `failed` — deterministic `BLOCK`;
- `unknown` — deterministic `ESCALATE`.

Every precondition must reference at least one evidence row.

## 10. Idempotency and replay

The envelope declares an idempotency key with `reject_duplicate` policy. The
reference evaluator accepts a caller-provided set of previously observed keys.

Durable storage, atomic check-and-record behavior, expiry, and distributed
coordination are integration responsibilities. An in-memory test set is not a
production replay defense.

## 11. Recovery

When `rollback_required` is true but `rollback_available` is false, the
reference evaluator returns `ESCALATE / RECOVERY_NOT_READY`.

A rollback reference is required whenever rollback is declared available. The
evaluator does not execute or validate the rollback procedure itself.

## 12. Decision semantics

- `ALLOW` — every declared check in this bounded evaluator passed.
- `BLOCK` — a deterministic safety or integrity condition failed.
- `ESCALATE` — the proposal is structurally valid but requires human or
  external resolution.

Stable reason codes are defined in [`DECISION_CODES.md`](DECISION_CODES.md).

## 13. Relationship to continuation

The Verifiable Continuation Envelope may preserve:

- current objective;
- active constraints;
- rejected approaches;
- pending verification;
- durable artifact references.

It must not silently create an Action Envelope authorization grant. A resumed
agent still needs a separately constructed and evaluated Action Envelope before
performing a high-risk side effect.

## 14. Extension rule

Future domain-specific fields should be added through a versioned extension or
new schema version. Implementations must not silently ignore unknown fields;
the published schema therefore uses `additionalProperties: false`, and the
conformance suite contains regressions for both top-level and nested fields.

## 15. Non-goals

V1 does not define:

- production authentication or signatures;
- policy authoring;
- distributed replay storage;
- tool execution;
- post-execution receipts;
- compensation transactions;
- regulatory rules;
- a universal agent-to-agent transport.
