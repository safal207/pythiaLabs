# ELR-I9 Candidate — Execution Binding Completeness

**Status:** candidate invariant for ELR-001  
**Scope:** executor-side binding after route use-time revalidation  
**Origin:** CrewAI #4877 verifier/executor boundary discussion

## Invariant

A successful use-time revalidation is not, by itself, proof that the state it attested was the state actually consumed by the eventual action.

For consequential execution, distinguish three identities:

```text
state_hash  -> content identity
generation  -> temporal/history identity
use_nonce   -> consumption identity
```

The executor-side boundary should fail closed unless:

```text
observed_state_hash == expected_state_hash
AND
observed_generation == expected_generation
AND
use_nonce is unused
```

The executor must then reserve/consume the nonce and release the effect under one concurrency boundary appropriate to that runtime.

## Why `state_hash` alone is insufficient

Content addressing can prove that the currently observed bytes equal the expected bytes. It cannot prove that the state did not move away and later return to the same content.

Synthetic ABA fixture:

```text
generation 41: permission = ALLOW
proof binds hash(ALLOW), generation=41

-> revoke
generation 42: permission = DENY

-> restore
generation 43: permission = ALLOW
```

At generation 43:

```text
observed_state_hash == expected_state_hash  # true
observed_generation == expected_generation  # false
```

The old attempt must be rejected even though the content hash matches.

This matters first in naturally cyclic, low-cardinality state spaces such as toggled permissions, rotating credentials or leases, round-robin ownership, and authorization flags that can be revoked and restored to byte-identical content.

## Replay is a separate failure mode

Even when content and generation still match, an already-consumed authorization occurrence must not silently become replayable:

```text
observed_state_hash == expected_state_hash
observed_generation == expected_generation
use_nonce already consumed
-> reject
```

Generation and nonce therefore close different gaps:

- `generation` prevents `A -> B -> A` from reviving stale authority;
- `use_nonce` prevents a still-fresh authority occurrence from being consumed twice.

## Ownership boundary

This invariant is executor-side by construction.

A verifier can attest to content and can explicitly state that execution binding is external. It cannot mint an authoritative generation without owning the caller's transition history, and it cannot authoritatively consume a nonce without owning the caller's consumption state.

Accordingly:

```text
verifier
  -> proof integrity / content commitment
  -> requires use-time revalidation

executor
  -> current content check
  -> generation check
  -> nonce replay check
  -> atomic reservation/consumption + effect release
```

## Reference conformance helper

`conformance/execution_binding.py` provides a deliberately narrow checker for the three caller-supplied facts.

It does **not** mutate nonce state and does **not** claim transactional atomicity with an external side effect. A production runtime must supply that primitive itself.

The conformance suite preserves two independent falsifiers plus one positive control:

1. matching hash + generation + unused nonce -> ready;
2. same hash after `ALLOW -> DENY -> ALLOW`, but newer generation -> reject;
3. same hash + same generation, but consumed nonce -> reject replay.

## Relationship to existing ELR invariants

```text
ELR-I7  route receipt is evidence, not authority
ELR-I8  historical verification != current applicability
ELR-I9  current applicability != proof of the exact state/occurrence consumed
```

This candidate intentionally does not change `verify_receipt()` semantics. Historical receipt verification remains historical. `revalidate_receipt_for_use(...)` remains a current-admissibility check. ELR-I9 describes the next boundary that only the executor can close.

## Non-claims

ELR-I9 does not claim:

- that ELR itself owns execution state;
- that a verifier can mint executor generations or consumption nonces;
- that the reference helper provides distributed compare-and-swap;
- that nonce checking alone makes an arbitrary external effect atomic;
- that every content-equal state transition is semantically unsafe;
- that a production ABA incident has already been observed in ELR.

The narrow claim is:

> When transition history or single-use consumption carries authority semantics, content equality alone is not execution identity. A consequential executor must additionally bind the authoritative generation and consumption occurrence, or explicitly accept the weaker semantics.
