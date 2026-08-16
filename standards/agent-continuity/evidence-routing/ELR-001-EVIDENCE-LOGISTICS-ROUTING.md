# ELR-001 — Evidence Logistics Routing

**Status:** Draft v0.1  
**Scope:** framework-neutral proof-path selection for consequential agent actions  
**Origin:** RESONANCE Issue 001, Article 11 — *Evidence Has a Route*  
**Relationship:** complements ACI-001 (current authority) and ACB-001 (authorization consumption); does not replace either.

## 1. Problem

Agent runtimes increasingly have more than one way to establish that an action may proceed:

```text
local synchronous check
cached evidence + freshness revalidation
independent verifier
human DEFER / resolve
fresh external evidence
composed multi-step verification
```

Treating one route as universally correct creates two symmetric failures:

1. **under-verification** — a cheap route is used even though it cannot satisfy the action's proof obligations;
2. **over-verification** — every action is sent through the strongest available path, even when a cheaper route is already sufficient, current and auditable.

ELR-001 models this as **evidence logistics**: route sufficient proof to the execution boundary at the point in state/time where the action becomes real.

## 2. Core rule

> **First filter by hard proof obligations. Then choose the lowest-cost admissible route.**

This ordering is load-bearing.

The optimizer MUST NOT convert a missing proof into a soft penalty. Required human approval, current authority, freshness, exact occurrence binding, state binding, policy binding or any other hard obligation cannot be bought away by lower latency or lower cost.

Formally:

```text
A = { p ∈ Paths | obligations ⊆ proofs(p) ∧ every edge condition holds now }

if A = ∅:
    BLOCK

else:
    choose argmin_{p ∈ A} Cost(p)
```

This is deliberately different from:

```text
argmin Cost(p) + SafetyPenalty(p)
```

because a sufficiently favorable cost term could otherwise make a forbidden path win.

## 3. Context is part of admissibility

A route can be admissible at one point and inadmissible later.

ELR-001 reference bindings include:

```text
action_scope_digest
authority_epoch
policy_version
state_version
risk_tier
reversibility
valid_until_tick
evidence_observed_tick
max_evidence_age_ticks
```

The router therefore answers:

> Which proof path is admissible **for this action, under this authority and state, at this time**?

It does not answer which route is globally best forever.

## 4. Sync and async are route profiles, not the policy itself

A low-risk reversible action may correctly use:

```text
START
  ↓
local sync check
  ↓
EXECUTE
```

A higher-risk irreversible action may require:

```text
START
  ↓
independent verifier
  ↓
human DEFER / resolve
  ↓
exact authorization occurrence binding
  ↓
one-shot consumption
  ↓
EXECUTE
```

The runtime should not assume `sync` or `async` is intrinsically safer. The policy determines hard proof obligations; the routing layer chooses among paths that satisfy them.

## 5. Graph model

The reference graph is a directed graph:

```text
G = (V, E)
```

Each edge carries:

```text
provides[]   # proof capabilities accumulated by traversing the edge
bindings{}   # contextual conditions that must hold now
cost{}       # latency / compute / coordination / monetary units
```

A routing request supplies:

```text
start_node
target_node
context
required_proofs[]
cost_weights{}
```

The reference algorithm runs Dijkstra over an expanded state:

```text
(node, accumulated_proofs)
```

not only over `node`.

That distinction matters because two paths can arrive at the same graph node with different proof sets.

## 6. Reference admissibility rules

An edge is unavailable when any declared binding fails.

Examples:

```text
bound authority_epoch != current authority_epoch
bound policy_version  != current policy_version
bound state_version   != current state_version
bound action digest   != current action digest
current risk          > edge max_risk_tier
reversible-only edge  used for irreversible action
now                   > valid_until_tick
evidence timestamp    is in the future
evidence age          > max_evidence_age_ticks
```

A complete path is admissible only when:

```text
target reached
AND
required_proofs ⊆ accumulated_proofs
```

Reaching `EXECUTE` without the required proof set is not success.

## 7. Determinism

For equal weighted cost, the reference implementation uses a deterministic lexical tie-break over the edge-id path.

This is not claimed to be the only valid production tie-break. It exists so conformance output is reproducible.

## 8. Route receipt and two different verification questions

A selected path produces a receipt that binds:

```text
request_id
request_digest
graph_digest
selected_edge_ids
accumulated_proofs
required_proofs
weighted_total_cost
evaluated_at_tick
receipt_digest
```

A route receipt creates two distinct verification questions.

### 8.1 Historical selection integrity

`verify_receipt(receipt, request, graph)` asks:

> **Was this receipt correctly produced from this exact request and graph at the recorded evaluation tick?**

It recomputes:

1. request and graph digests;
2. every selected edge and edge adjacency;
3. each edge binding against the **issuance context**;
4. accumulated proofs;
5. total weighted cost;
6. target reachability;
7. hard-obligation coverage;
8. reference optimality at issuance time;
9. receipt digest.

The strict equality:

```text
receipt.evaluated_at_tick == request.context.now_tick
```

is intentional for historical verification. Restamping the original request to a later time would change the object whose selection the receipt claims to prove.

### 8.2 Current applicability at consumption/use time

Historical correctness does not imply current applicability.

`revalidate_receipt_for_use(receipt, request, graph, current_context)` asks the separate question:

> **Does the already-selected route remain admissible under the current context now?**

The function first requires the historical receipt to verify unchanged, then traverses the exact selected edges again using `current_context` for:

```text
valid_until_tick
max_evidence_age_ticks
authority_epoch
policy_version
state_version
action_scope_digest
risk_tier
reversibility
```

If any selected edge is stale or drifted, use-time validation returns:

```text
BLOCKED_ROUTE_STALE_OR_DRIFTED
```

The caller may then issue a fresh routing request and run `select_route()` again.

Use-time revalidation intentionally does **not** re-optimize the route. A historically selected route can remain safe and admissible even if another route has become cheaper. Current admissibility and current optimality are different questions.

A receipt therefore records **which route was selected from which graph for which contextual request**. It is evidence about selection, not execution authority and not a timeless permission to use that path later.

## 9. Conformance invariants

### ELR-I1 — Admissibility before optimization

> An inadmissible path MUST NOT become selectable by being cheaper.

### ELR-I2 — No-route fail closed

> If no path satisfies all hard proof obligations under current bindings, selection returns `BLOCKED_NO_ADMISSIBLE_ROUTE`.

### ELR-I3 — Contextual freshness

> A route that depended on stale, future-dated or expired evidence MUST be excluded before optimization.

### ELR-I4 — Authority/state/policy causality

> A route bound to older authority, state, policy or action scope MUST NOT remain silently admissible after those values change.

### ELR-I5 — Proof accumulation is path-dependent

> Proof obligations may be satisfied across multiple edges; the router MUST preserve the accumulated proof set while searching.

### ELR-I6 — Reproducible selection

> Given the same request, graph and tie-break rule, the reference selection and receipt MUST recompute identically.

### ELR-I7 — Route receipt is evidence, not authority

> A valid routing receipt proves a selection result under a bound request/graph snapshot. It does not prove that the tool executed or that current authority still exists later.

### ELR-I8 — Historical verification != current applicability

> A receipt that verifies at its issuance tick MUST NOT be treated as proof that the selected route remains admissible at a later consumption tick. Current use requires explicit revalidation against current context.

This distinction is the temporal counterpart of ACB's separation between authorization occurrence and authorization consumption.

## 10. Conformance suite

The v0.1 suite now includes **30 tests**.

The original 24 cover:

- published schema validation;
- cheap sync selection for low-risk actions;
- composed independent + human + consumption route for high-risk actions;
- zero-cost unsafe shortcut rejection;
- target-reached-without-proof rejection;
- stale cached evidence rerouting;
- future evidence rejection;
- authority epoch drift;
- policy version drift;
- state version drift;
- action-scope drift;
- risk ceiling enforcement;
- reversible-only route enforcement;
- multi-edge proof accumulation;
- cost-weight changes among admissible routes;
- deterministic tie-break;
- negative cost schema rejection;
- invalid graph endpoint rejection;
- duplicate edge-id rejection;
- request/graph digest binding;
- receipt tamper detection;
- path tamper detection even after receipt re-signing;
- no-route fail-closed behavior;
- zero-cost cycle termination.

Six additional use-time tests cover the counterexample raised against the first executable draft:

- historical verification remains bound to the issuance tick;
- a selected route remains usable before its declared expiry;
- `valid_until_tick` is re-evaluated at use time;
- `max_evidence_age_ticks` is re-evaluated at use time;
- authority drift invalidates an old route before consumption;
- a current-time context earlier than receipt issuance fails closed.

## 11. Non-claims

ELR-001 does **not** claim:

- that the supplied policy obligations are correct;
- that the chosen cost model captures every production concern;
- that Dijkstra is the right algorithm for every dynamic or probabilistic system;
- that a selected path remains admissible after the bound context changes without use-time revalidation;
- that a routing receipt proves execution or settlement;
- that all proof edges are equally trustworthy merely because they share a graph;
- that use-time revalidation makes an external side effect transactionally atomic;
- formal global safety or liveness;
- adoption by CrewAI, AG2 or another framework.

The narrow claim is testable:

> Given a finite graph, a bounded contextual request, hard proof obligations and non-negative edge costs, the reference router selects the deterministic lowest-cost admissible proof path at evaluation time or fails closed; a later use of that receipt can be separately revalidated against the current context without falsifying the original historical receipt.

## 12. Relationship to the RESONANCE stack

```text
ACI
Who may act now?
        ↓
ACB
Which exact permission may this execution consume?
        ↓
ELR selection
Which admissible proof path should be chosen at T?
        ↓
ELR use-time revalidation
Is that selected proof path still admissible at T+n?
```

The separation is intentional.

Authority, authorization consumption, route selection and later route applicability are different decisions. A production runtime may compose all four.

## 13. Reader falsification

The originating article includes a live `Agree / Partially agree / Disagree` poll:

https://github.com/safal207/RESONANCE/issues/58

Votes are reader judgment, not proof. A reproducible counterexample that breaks one of the invariants is stronger evidence than agreement.

The first external falsification after publication identified exactly such a gap: `verify_receipt()` could prove issuance-time correctness but there was no API for asking whether the old route remained admissible at a later use tick. ELR-001 preserves that counterexample in the design by separating historical verification from use-time revalidation rather than weakening the original receipt binding.

## 14. Run the reference suite

```bash
python -m pip install -r standards/agent-continuity/evidence-routing/conformance/requirements.txt

python -m unittest discover \
  -s standards/agent-continuity/evidence-routing/conformance \
  -p 'test_*.py' \
  -v
```
