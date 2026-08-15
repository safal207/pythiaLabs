# ACI-001: Authority Causality Invariant

- **Status:** Draft
- **Version:** 0.1
- **Scope:** Multi-agent coordination, work-stealing, ownership transfer, delegated mutation, recovery after interruption or compaction

## 1. Abstract

A valid state transition requires more than current knowledge of state. The actor must also hold **current causal authority** to perform the transition.

ACI-001 treats write authority as a stateful, versioned object with its own predecessor, transition, epoch and evidence. Authority may be assigned, transferred, delegated, revoked or expire. A stale actor can therefore possess correct data and still be forbidden to mutate it.

> **Authority itself has causal state.**

For consequential mutation, both the state predecessor and authority predecessor must be current and provable:

```text
CAS(state) ∧ CAS(authority) → mutation admissible
```

## 2. Failure class

Static ownership is cheap when a key can be permanently partitioned:

```text
key X → owner A
key Y → owner B
```

No write-time arbitration is needed because two loops cannot hold write authority over the same key.

The failure appears when ownership becomes dynamic: work-stealing, failover, runtime-dependent routing, delegation, restart, compaction/recovery, delayed retries, revocation or expiration.

Example:

```text
epoch 17:
  key X → worker A

handoff:
  A → B
  epoch 17 → 18

late write:
  worker A proposes mutation with epoch 17
```

Worker A may have fresh state and a semantically correct patch. The mutation is still invalid because its authority predecessor is stale.

## 3. Coordination ladder

```text
static ownership
    ↓ when dynamic reassignment appears
CAS ownership transfer
    ↓ when genuine concurrent mutation remains
causal-CAS shared state
```

The system should pay coordination cost only when the workload requires it.

## 4. Authority state

A canonical authority state contains:

- `resource_ref`
- `owner_ref`
- `authority_epoch`
- `status`
- `scope`
- `predecessor_digest`
- `authority_digest`

`authority_epoch` is monotonic per resource. It is not a wall clock and does not claim global ordering across unrelated resources.

## 5. Authority transitions

Supported transition kinds:

- `assign`
- `transfer`
- `delegate`
- `revoke`
- `expire`

A non-genesis transition binds:

```text
expected_previous_authority_digest
expected_previous_epoch
from_owner_ref
transition
new_owner / status
new_epoch
```

An accepted ownership-changing transition advances the epoch exactly once:

```text
new_epoch = expected_previous_epoch + 1
```

Wrong predecessor digest, stale epoch, wrong current owner or invalid epoch increment MUST fail closed.

## 6. Mutation admission

A consequential mutation carries:

- `actor_ref`
- `resource_ref`
- `effect_ref`
- `presented_authority_epoch`
- `presented_authority_digest`
- optional `expected_previous_state_digest`
- optional `new_state_digest`

Authority admission requires:

1. current authority state exists;
2. status is `active`;
3. actor matches current owner;
4. resource matches;
5. presented epoch equals current epoch;
6. presented authority digest equals current authority digest;
7. mutation effect is inside authority scope.

If state CAS is requested, the expected state predecessor must also match current state.

## 7. Normative invariants

### ACI-001 — Authority is stateful
Execution authority MUST be represented as current state, not a timeless actor attribute.

### ACI-002 — Authority has a causal predecessor
Every non-genesis authority transition MUST identify the authority state it replaces.

### ACI-003 — Epoch monotonicity
Per-resource `authority_epoch` MUST increase by exactly one on accepted authority transition.

### ACI-004 — Stale authority is rejected
Correct state knowledge does not compensate for a stale authority epoch or digest.

### ACI-005 — Ownership transfer is separate from state mutation
**Who may write?** MUST remain distinguishable from **is this state transition based on the expected predecessor?**

### ACI-006 — Revocation dominates cached context
Revoked or expired authority MUST reject mutation even if an actor recovers an older checkpoint claiming ownership.

### ACI-007 — Scope survives transfer explicitly
A transfer MUST explicitly preserve or replace mutation scope. Scope MUST NOT be silently inferred from a previous owner.

### ACI-008 — Split authority fails closed
If different active authority states claim the same resource and epoch, the resource is conflicted and mutation MUST be blocked.

### ACI-009 — Static ownership is a valid optimization
A statically partitioned key is conformant when exactly one active owner exists and dynamic transfer is unnecessary.

### ACI-010 — Combined causal admission
Where state CAS is enabled:

```text
authority predecessor current
AND
state predecessor current
→ mutation admissible
```

Neither proof subsumes the other.

## 8. Relation to Responsibility-Lane Continuity

Responsibility-Lane Continuity asks:

> Which lane owns this action after recovery?

ACI-001 asks:

> By what causal transition did that lane or actor become the current owner?

The composed recovery path is:

```text
recover task state
→ recover responsibility lane
→ recover authority state
→ verify authority epoch/digest
→ verify state predecessor
→ admit mutation
```

This blocks a resumed or work-stolen agent that remembers the correct task but holds stale execution authority.

## 9. Machine-readable contract

```text
authority-causality/schema/authority-state.schema.json
authority-causality/schema/authority-transition.schema.json
authority-causality/schema/mutation-request.schema.json
authority-causality/conformance/aci_reference.py
authority-causality/conformance/test_aci_conformance.py
```

Fixtures cover static ownership, valid transfer, stale-writer rejection and split-authority rejection.

## 10. Minimum conformance suite

A conforming implementation demonstrates schema validation, canonical authority digests, static-owner acceptance, valid transfer, exact epoch increment, stale epoch/digest rejection, wrong-actor rejection, revoke/expire rejection, scope enforcement, split-authority rejection, state-CAS enforcement and tamper detection.

## 11. Closing principles

> **Correct knowledge does not imply current authority.**

> **No consequential mutation is valid unless both its state predecessor and its authority predecessor are current and causally provable.**
