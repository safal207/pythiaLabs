# ORC-001 — Orphan Cascade Revocation

**Status:** Draft v0.1  
**Scope:** framework-neutral execution-authority revocation for parent/child agent trees  
**Relationship:** extends HRC-001 ownership epochs into already-running execution trees; does not define process supervision or transport.

## 1. Problem

A multi-agent runtime can correctly transfer task ownership and still leave old execution processes alive.

Example:

```text
owner A @ epoch 4
  └─ execution A/root
       └─ child C
            └─ grandchild D

handoff commits to owner B @ epoch 5

A/C/D may still be RUNNING
```

Killing the old process group is useful cleanup, but it is not a sufficient authorization boundary. A delayed child may survive briefly, a cancellation signal may be dropped, or an orphan may continue after its parent exits.

The safety requirement is therefore stronger:

> When authority advances, every descendant bound to the superseded authority generation loses permission to create consequential side effects immediately, whether or not the operating-system process has terminated yet.

ORC-001 makes that boundary explicit.

## 2. Core separation

ORC-001 keeps three facts distinct:

```text
authority validity
process liveness
quiescence
```

They are not interchangeable:

```text
RUNNING != AUTHORIZED
KILL_REQUESTED != EXITED
EXITED != PROOF_NO_PRIOR_SIDE_EFFECT
```

HRC-001 establishes the current lane owner and ownership epoch. ORC-001 binds each execution tree to that authority generation and evaluates whether later side effects are still admissible.

## 3. Execution authority binding

Every consequential execution SHOULD carry a bounded authority binding:

```text
execution_id
authority_lane_id
authority_owner_ref
authority_epoch
root_execution_id
parent_execution_id (optional for root)
actor_ref
process_group_ref (optional)
```

A child MUST inherit the same:

```text
authority_lane_id
authority_owner_ref
authority_epoch
root_execution_id
```

from its parent.

A child cannot refresh or mint a newer authority epoch merely because the current lane state has advanced. New authority requires a new execution lineage admitted under the new owner/epoch.

## 4. Side-effect admission

A side-effect attempt is admissible only when the execution's authority binding still matches the current HRC lane state:

```text
execution.authority_lane_id == state.lane_id
execution.authority_owner_ref == state.owner_ref
execution.authority_epoch == state.ownership_epoch
```

When a parent execution is supplied, the evaluator also requires:

```text
child.parent_execution_id == parent.execution_id
child.root_execution_id == parent.root_execution_id
child.authority_lane_id == parent.authority_lane_id
child.authority_owner_ref == parent.authority_owner_ref
child.authority_epoch == parent.authority_epoch
```

This prevents a descendant of revoked owner A/epoch 4 from silently rebinding itself to owner B/epoch 5.

## 5. Cascade revocation

Suppose HRC-001 commits:

```text
owner A / epoch 4
        ↓
owner B / epoch 5
```

Every execution whose authority binding is still `(A, 4)` becomes revoked for consequential side effects, including all descendants.

The revocation does not require the runtime to discover or kill every process before enforcing the admission boundary. Process cleanup may happen concurrently.

Reference result for a superseded epoch:

```text
BLOCKED_REVOKED_AUTHORITY_EPOCH
```

Reference result for a superseded owner under an otherwise matching epoch:

```text
BLOCKED_REVOKED_AUTHORITY_OWNER
```

## 6. Process supervision is a separate control

A runtime MAY use process groups, job objects, cgroups, supervisors, containers or another mechanism to terminate obsolete descendants.

ORC-001 treats these as liveness/quiescence controls, not as proof of authority.

A stale execution that remains `RUNNING` after authority advances yields:

```text
REVOCATION_PENDING_LIVE_EXECUTIONS
```

Only when all executions bound to superseded authority are observed non-running may the reference report:

```text
REVOCATION_QUIESCENT
```

A cancellation request alone is insufficient to claim quiescence.

## 7. Conformance invariants

### ORC-I1 — Authority revocation is immediate

> After the current ownership epoch advances, an execution bound to the previous epoch MUST NOT be admitted for a consequential side effect, even if its process is still alive.

### ORC-I2 — Revocation cascades by inherited binding

> Descendants inherit the parent's authority owner, epoch, lane and root execution identity. Every descendant of a superseded authority generation is therefore revoked without requiring per-child ownership mutation.

### ORC-I3 — Descendants cannot self-refresh authority

> A child MUST NOT change its authority owner or epoch relative to its parent merely to match newer lane state.

### ORC-I4 — Process liveness is not authority

> A running process does not imply current execution permission.

### ORC-I5 — Kill requested is not quiescent

> A cancellation or kill request MUST NOT be reported as process termination without an observed non-running state.

### ORC-I6 — Quiescence and admission are independent

> The runtime SHOULD block revoked side effects immediately and MAY complete process cleanup later. Safety MUST NOT depend on cleanup winning a race against the next side effect.

### ORC-I7 — New owner requires new lineage

> Work under the new owner/epoch MUST begin in an execution lineage explicitly bound to that new authority; a revoked descendant cannot become valid by mutating its binding.

### ORC-I8 — Revocation does not erase evidence

> Revoking future side effects does not prove that the stale execution produced no earlier side effects. Existing execution/evidence receipts remain independently auditable.

## 8. Reference statuses

The reference evaluator emits bounded statuses including:

```text
SIDE_EFFECT_ALLOWED
BLOCKED_LANE_MISMATCH
BLOCKED_PARENT_EXECUTION_MISMATCH
BLOCKED_AUTHORITY_LINEAGE_ESCAPE
BLOCKED_REVOKED_AUTHORITY_EPOCH
BLOCKED_REVOKED_AUTHORITY_OWNER
REVOCATION_PENDING_LIVE_EXECUTIONS
REVOCATION_QUIESCENT
```

## 9. Minimum falsification scenarios

A conforming implementation should demonstrate at least:

1. current owner/current epoch root execution may perform a side effect;
2. current child with inherited binding may perform a side effect;
3. handoff advances epoch and immediately blocks the old root;
4. the same handoff immediately blocks a still-running child;
5. the same handoff immediately blocks a still-running grandchild;
6. a child cannot rewrite its binding to the new epoch while remaining in the old lineage;
7. a kill-requested but still-running stale descendant prevents quiescence;
8. observed exit of all stale descendants allows quiescence;
9. new owner/new epoch in a new root lineage is admissible;
10. revocation status does not claim absence of prior external effects.

## 10. Non-claims

ORC-001 does **not** claim:

- that process groups are the only valid cleanup primitive;
- that a successful kill request proves all descendants exited;
- that blocked future admission rolls back an external side effect already committed;
- that all tools currently expose an authority-admission hook;
- that Claude Code or another vendor has adopted this contract;
- that the motivating public discussion proves this failure class occurs at a particular frequency.

## 11. Governing principle

> Revoke authority before relying on cleanup: a stale process may remain alive, but it must not remain authorized.
