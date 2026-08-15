# HRC-001 — Handoff Reachability & Causal Basis

**Status:** Draft v0.1  
**Scope:** framework-neutral multi-agent handoff and transition admission  
**Origin:** public Claude Code #24798 coordination discussion  
**Relationship:** complements responsibility-lane continuity and authority/consumption standards; does not replace them.

## 1. Problem

Multi-agent systems often collapse four different questions into one status field:

```text
who owns this lane?
what state did the writer actually observe?
is the intended recipient reachable now?
is this transition still based on the current predecessor?
```

That conflation produces two different failure classes:

1. a handoff records a new owner even though no running session/watcher can receive it;
2. a writer emits a transition without having read the predecessor it claims to extend.

The second failure is not automatically a compare-and-swap race. CAS only detects a predecessor changing after a writer has a basis to compare. It cannot repair a writer that never read the predecessor in the first place.

## 2. Core separation

HRC-001 keeps four facts distinct:

```text
Ownership epoch
= who may currently author the lane?

Causal basis
= what predecessor has the writer actually observed through?

Reachability
= is the intended recipient currently addressable through a surfaced diagnostic?

Transition CAS
= is the expected predecessor still the lane head now?
```

Core invariants:

> **Ownership does not imply reachability.**

> **Observed predecessor does not imply current predecessor.**

> **A diagnostic that exists but is not surfaced to the sender is not an operational signal.**

> **A handoff is not complete merely because a new owner was named.**

## 3. Transition admission

An ordinary status transition is admissible only when:

```text
writer_ref == current owner_ref
writer_ownership_epoch == current ownership_epoch
observed_through_event_id == expected_predecessor_id
expected_predecessor_id == current head_event_id
```

The two predecessor checks deliberately answer different questions.

### 3.1 Unread-predecessor failure

```text
observed_through_event_id != expected_predecessor_id
```

means the proposal is not causally based on the predecessor it claims to extend.

Reference result:

```text
BLOCKED_UNREAD_PREDECESSOR
```

### 3.2 CAS conflict

```text
observed_through_event_id == expected_predecessor_id
expected_predecessor_id != current head_event_id
```

means the writer had a coherent basis, but the lane advanced after that basis was obtained.

Reference result:

```text
BLOCKED_CAS_CONFLICT
```

These are not the same failure.

## 4. Handoff is two-phase

HRC-001 does not mutate ownership as soon as a target owner is written.

```text
current owner A
      ↓ proposes handoff E43
recipient reachability checked
      ↓
HANDOFF_DELIVERABLE
      ↓ recipient acknowledges E43
HANDOFF_COMMIT_ALLOWED
      ↓
ownership_epoch increments
owner becomes B
```

Until commit, A remains the current owner.

This prevents a durable record from claiming that B owns a lane while B has no reachable process/session capable of receiving it.

## 5. Reachability is operational only when surfaced

A runtime may already possess a watcher inventory, process table, session registry or message-bus diagnostic. That alone is insufficient.

A handoff proposal must bind the reachability signal to the diagnostic surface the sender was expected to use:

```text
reachability_surface_ref
```

The reachability signal must bind the same surface:

```text
surface_ref
```

If they differ, the reference contract returns:

```text
BLOCKED_REACHABILITY_NOT_SURFACED
```

This models the distinction:

```text
diagnostic exists internally
!=
diagnostic is part of the sender's decision path
```

## 6. Reachability freshness

A reachability signal binds:

```text
participant_ref
status = READY | UNAVAILABLE
observed_at_tick
valid_until_tick
surface_ref
```

A signal is not usable when:

```text
observed_at_tick > now_tick
now_tick > valid_until_tick
status != READY
participant_ref != target_owner_ref
```

Expired or unavailable reachability yields:

```text
PENDING_UNREACHABLE
```

Missing reachability yields:

```text
PENDING_REACHABILITY_UNCHECKED
```

The distinction matters: unknown reachability is not the same fact as known unreachability.

## 7. Recipient acknowledgement

A deliverable handoff still requires acknowledgement from the target owner.

The acknowledgement binds:

```text
recipient_ref
lane_id
accepted_handoff_event_id
accepted_ownership_epoch
observed_predecessor_id
```

The commit gate checks that the recipient accepted the exact proposed handoff occurrence and the exact ownership epoch while still observing the predecessor that the handoff extends.

Only then does the reference return:

```text
HANDOFF_COMMIT_ALLOWED
```

## 8. Conformance invariants

### HRC-I1 — Ownership epoch gates authorship

> A writer that is not the current owner at the current ownership epoch MUST NOT author a lane transition.

### HRC-I2 — Causal basis precedes CAS

> A proposal MUST prove that the writer observed the predecessor it claims to expect before CAS can establish whether that predecessor is still current.

### HRC-I3 — Unread predecessor != CAS conflict

> A writer that never observed the claimed predecessor MUST fail differently from a writer whose observed predecessor became stale after observation.

### HRC-I4 — Ownership != reachability

> Naming a target owner MUST NOT make a handoff complete when the target has no current reachable receiver.

### HRC-I5 — Internal diagnostic != operational signal

> A reachability diagnostic MUST be bound to the sender-visible protocol surface before it can satisfy handoff admission.

### HRC-I6 — Reachability is time-bound

> Future-dated, expired, mismatched or unavailable reachability MUST fail closed or remain pending.

### HRC-I7 — Deliverable != committed

> A reachable recipient MUST still acknowledge the exact handoff occurrence before ownership may advance.

### HRC-I8 — Honest non-reproduction narrows scope

> Absence of a reproduced CAS race under low concurrency MUST NOT be reported as evidence that unread-predecessor or higher-concurrency collision classes are universal.

HRC-I8 is a reporting boundary, not a runtime algorithm.

## 9. Reference results

The reference evaluator emits bounded statuses including:

```text
STATUS_TRANSITION_ALLOWED
BLOCKED_WRITER_NOT_OWNER
BLOCKED_OWNERSHIP_EPOCH_MISMATCH
BLOCKED_UNREAD_PREDECESSOR
BLOCKED_CAS_CONFLICT
PENDING_REACHABILITY_UNCHECKED
BLOCKED_REACHABILITY_NOT_SURFACED
PENDING_UNREACHABLE
HANDOFF_DELIVERABLE
PENDING_RECIPIENT_ACK
HANDOFF_COMMIT_ALLOWED
```

## 10. Evidence boundary

The motivating public thread contains two materially different observations:

- one contributor reported a live handoff assigned to a session with no running watcher, making the handoff undeliverable until manual startup;
- the same contributor did **not** reproduce the proposed CAS-race class in their low-concurrency logs and instead found mostly writers that had not read the thread to the end.

HRC-001 preserves both facts. It does not convert the non-reproduction into a universal safety claim, and it does not generalize one participant's logs into a population frequency.

## 11. Non-claims

HRC-001 does **not** claim:

- that an OS process or watcher is the only valid reachability mechanism;
- that a READY reachability signal guarantees successful message delivery;
- that acknowledgement guarantees the recipient will complete the task;
- that an `observed_through_event_id` is truthful unless backed by a trusted read/observation mechanism;
- that CAS races are common or universal;
- that a low-concurrency non-reproduction disproves higher-concurrency collision risk;
- transactional atomicity across arbitrary distributed systems;
- adoption by Anthropic or Claude Code.

The narrow executable claim is:

> Given a bounded lane state, transition proposal, reachability signal and recipient acknowledgement, the reference evaluator separates ownership authority, causal read basis, current predecessor, recipient reachability and handoff acknowledgement instead of conflating them into one status transition.
