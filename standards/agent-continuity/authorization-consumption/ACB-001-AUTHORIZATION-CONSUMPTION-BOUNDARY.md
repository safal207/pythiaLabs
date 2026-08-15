# ACB-001 — Authorization Consumption Boundary

**Version:** 0.1  
**Status:** Draft / executable reference contract  
**Scope:** Framework-neutral authorization-to-execution binding

## Abstract

A historical `ALLOW` is not by itself proof that a later execution is currently authorized.

ACB-001 separates:

```text
semantic decision identity
        !=
authorization occurrence identity
        !=
execution occurrence identity
```

and defines a fail-closed boundary where a concrete authorization occurrence is checked and consumed by a concrete execution occurrence.

Core invariant:

> A consequential execution may cross the Authorization Consumption Boundary only when the exact authorization occurrence is recoverable, its execution scope still matches, all declared freshness conditions still hold, its authority/policy state remains admissible, and its usage policy permits this execution to consume it.

## Objects

### AuthorizationOccurrence

An authorization occurrence is a concrete issued decision event. It carries both the semantic `decision_ref` and the occurrence-specific `decision_event_id`.

Required fields include:

- `decision_ref`
- `decision_event_id`
- `status`
- `issuer_ref`
- `policy_version`
- `logical_operation_id`
- `execution_scope_digest`
- `revalidate_if`
- `bound_conditions`
- `usage_policy`
- `use_count`
- `consumed_by_execution_ids`

A semantic decision may have multiple distinct occurrences. Therefore `decision_ref` alone is insufficient when more than one occurrence exists.

### ProposedExecution

A proposed execution is a concrete execution attempt.

The scope digest is recomputed from a fixed preimage:

```text
logical_operation_id
tool_name
normalized_args
actor_ref
policy_version
authority_ref
authority_epoch
relevant_state_refs
```

`execution_id` is deliberately excluded from the scope digest. Retries may have a new execution occurrence under the same frozen logical operation, while authorization reuse remains governed separately by usage policy.

### ConsumptionReceipt

A receipt binds the exact `decision_event_id` to the exact `execution_id` and records either:

```text
CONSUMED
```

or:

```text
BLOCKED
```

with an explicit reason.

## Boundary algorithm

A conforming reference decision should fail closed unless all required checks succeed:

```text
resolve exact authorization occurrence
        ↓
check semantic decision_ref
        ↓
status == resolved_allow
        ↓
logical operation matches
        ↓
recompute execution_scope_digest
        ↓
compare declared freshness conditions
        ↓
check cancellation / supersession
        ↓
check one-shot / reusable usage policy
        ↓
consume authorization
        ↓
emit receipt binding decision_event_id -> execution_id
```

## Occurrence resolution

If an exact `decision_event_id` is supplied, resolution MUST verify that it belongs to the supplied `decision_ref`.

If no occurrence id is supplied:

- one matching occurrence may be resolved;
- multiple matching occurrences MUST return `OCCURRENCE_AMBIGUOUS`;
- zero matching occurrences MUST return `OCCURRENCE_NOT_FOUND`.

Implementations MUST NOT silently choose the first occurrence in storage order.

## Freshness

`revalidate_if` names conditions whose values must still equal the values recorded in `bound_conditions`.

Missing current values fail closed.

Examples:

```text
policy_generation
authority_epoch
recipient_binding
account_snapshot
deployment_revision
```

This contract does not prescribe which conditions a product must bind. It prescribes how declared conditions are checked.

## Usage policy

### One-shot

For:

```json
{"mode":"one_shot","max_uses":1}
```

the first successful consumption transitions the occurrence to `consumed`.

Any later execution attempt using the same occurrence MUST be blocked.

### Reusable

Reusable authorization is explicit, never inferred from missing consumption state.

A reusable occurrence may remain `resolved_allow` until `max_uses` is reached. When the limit is reached it transitions to `consumed`.

## Cancellation and supersession

A proposed execution carrying:

```text
cancelled = true
```

or:

```text
superseded = true
```

MUST NOT consume authorization.

Likewise an authorization whose status is `cancelled`, `superseded`, `revoked`, `expired`, `stale`, `denied`, or `consumed` is not currently consumable.

## Composition with authority causality

ACB-001 does not replace ACI-001.

ACI asks:

> Does this actor currently have authority over the resource/effect?

ACB asks:

> Which exact authorization occurrence permits this exact execution to cross the side-effect boundary?

A system may require both:

```text
ACI(current authority) == ADMISSIBLE
AND
ACB(current consent) == CONSUMED
```

before a consequential effect is released.

## Required falsification cases

The executable suite covers at least:

1. exact scope match succeeds;
2. normalized arguments change after approval;
3. actor changes after approval;
4. authority epoch changes after approval;
5. declared freshness condition changes;
6. declared freshness condition is missing;
7. one-shot authorization is replayed by a retry;
8. reusable authorization respects its explicit use limit;
9. cancellation blocks consumption;
10. supersession blocks consumption;
11. two occurrences share one semantic `decision_ref` and remain independently addressable;
12. semantic-only lookup becomes ambiguous when multiple occurrences exist;
13. wrong `decision_event_id` / `decision_ref` pairing fails closed;
14. an already non-active authorization cannot be consumed.

## Non-goals

ACB-001 does not claim:

- transactional atomicity with arbitrary external systems;
- distributed consensus;
- Byzantine fault tolerance;
- that every approval must be one-shot;
- that a digest alone eliminates all TOCTOU races;
- vendor-native adoption by CrewAI, AG2, or another framework.

The narrow guarantee is inspectability and fail-closed reference behavior at the authorization-to-execution seam.

## Operational principle

> Valid historical consent does not imply current execution authority.

and:

> A system should be able to prove not only why an action was allowed, but which exact permission was consumed when the action became real.
