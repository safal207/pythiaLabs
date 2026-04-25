# Temporal-Causal Memory Stack Roadmap

## Current status

PythiaLabs currently returns traces directly from each run.
The current MVP does not persist traces into external databases.
The current MVP does not require Datomic, Neo4j, XTDB, EventStoreDB, TimescaleDB, or any other storage service to run demos, tests, or the Agent Safety Showcase.

This document is a roadmap, not an implementation claim.

## Why another memory roadmap?

A single trace explains one run.
Persistent reasoning memory explains many runs over time.

The Temporal-Causal Memory Stack separates five questions:

- What was asserted?
- How is it connected?
- When was it valid?
- What happened in sequence?
- How did operational signals change over time?

Together, these questions help explain not only one agent decision, but patterns across many decisions.

## Layer 1: Fact memory — Datomic-style fact log

**Purpose:**
Stores immutable facts and assertions.

**Main question:**
What did the system assert or record?

**Examples:**
- agent_alpha proposed delete_user_data
- required_permission was user_data.delete
- stop_reason was missing_authorization
- confidence was 1.0
- trace entry was recorded

**Useful for:**
- audit
- immutable reasoning history
- replay
- comparing behavior across versions
- preserving decision records

**Status:**
Roadmap only. Not implemented in the current MVP.

## Layer 2: Graph memory — Neo4j-style relationship graph

**Purpose:**
Stores relationships between entities.

**Main question:**
How are actions, agents, constraints, failures, and decisions connected?

**Examples:**
- agent_alpha -> proposed -> delete_user_data
- delete_user_data -> requires -> user_data.delete
- missing_authorization -> caused -> reject
- action_type -> associated_with -> failure_class

**Useful for:**
- causal topology
- relationship analysis
- recurring failure discovery
- critic support
- explainability across related runs

**Status:**
Roadmap only. Not implemented in the current MVP.

## Layer 3: Temporal memory — XTDB-style bitemporal timeline

**Purpose:**
Stores when facts are valid and when the system learned them.

**Main question:**
When was a fact true, and when did the system know it?

**Use two time axes:**
- valid_time: when a fact is true in the domain
- transaction_time: when the system recorded or learned the fact

**Examples:**
- permission user_data.delete was valid from 10:00 to 10:30
- the system learned about that permission at 11:00
- a future grant becomes valid tomorrow at 09:00
- an action was rejected because permission was not valid at the action time

**Useful for:**
- past / present / future reasoning
- retroactive correction
- proactive future validity
- temporal audit
- authorization windows
- time-aware safety decisions

**Status:**
Roadmap only. Not implemented in the current MVP.

For a deterministic in-memory demo of this idea, see: `docs/bitemporal_authorization_showcase.md`.

## Layer 4: Event memory — EventStoreDB-style event stream

**Purpose:**
Stores event sequences in order.

**Main question:**
What happened, in what order?

**Examples:**
- run_started
- proposal_created
- candidate_executed
- constraint_checked
- decision_rejected
- run_stopped

**Useful for:**
- event sourcing
- replay
- debugging
- state reconstruction
- deterministic sequence analysis

**Status:**
Roadmap only. Not implemented in the current MVP.

## Layer 5: Metrics memory — TimescaleDB-style metrics timeline

**Purpose:**
Stores time-series operational signals.

**Main question:**
How did scores, confidence, latency, retries, failures, and drift change over time?

**Examples:**
- score per step
- confidence per run
- latency per executor
- retry count per action type
- failure rate per constraint
- drift across versions

**Useful for:**
- observability
- SLOs
- regression detection
- trend analysis
- operational dashboards
- critic trigger thresholds

**Status:**
Roadmap only. Not implemented in the current MVP.

## Summary table

| Layer | Style | Stores | Answers |
|---|---|---|---|
| Fact memory | Datomic-style | immutable facts/assertions | What was recorded? |
| Graph memory | Neo4j-style | relationships | How is it connected? |
| Temporal memory | XTDB-style | valid_time + transaction_time | When was it true / known? |
| Event memory | EventStoreDB-style | ordered events | What happened next? |
| Metrics memory | TimescaleDB-style | time-series signals | How did behavior change? |

## Conceptual flow

```text
Agent / Problem
↓
Planner loop
↓
Executor / SafetyGate
↓
Trace + stop_reason
↓
Fact memory
↓
Graph memory
↓
Temporal memory
↓
Event memory
↓
Metrics memory
↓
Critic / Pattern Analysis / Replay / Dashboards
```

## Relation to existing docs

`docs/persistent_reasoning_memory.md` describes the first roadmap step: append-only step log + hypothesis graph.

This document expands that roadmap into a broader five-layer memory architecture.

Both documents are roadmap docs, not implementation claims.

## Non-goals for current MVP

The current MVP does not include:

- Datomic adapter
- Neo4j adapter
- XTDB adapter
- EventStoreDB adapter
- TimescaleDB adapter
- persistent schema
- docker-compose storage services
- production storage layer

This document should not be read as a claim that these storage layers are implemented.
