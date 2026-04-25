# Persistent Reasoning Memory Roadmap

## Current status

PythiaLabs currently returns traces directly from each run.
The current MVP does not persist traces into Datomic, Neo4j, or any external database.
The current MVP does not require persistent storage to run demos, tests, or the Agent Safety Showcase.

## Why persistence matters

A single trace explains one run.
Persistent reasoning memory would allow PythiaLabs to analyze many runs over time.

This would help answer:

- What happened?
- In what order?
- Which proposal was executed?
- Which constraint failed?
- Why did the loop stop?
- Which `stop_reason` appears repeatedly?
- Which actions or failure classes are connected?

## Append-only step log

A Datomic-style step log would store every reasoning step as an immutable event.

It would capture:

- run_id
- step_id
- timestamp
- proposal
- candidate
- score or confidence
- stop_reason
- trace entry
- version of rules or constraints

This is useful for:

- audit
- replay
- debugging
- comparing behavior across versions
- preserving decision history

## Hypothesis graph

A Neo4j-style hypothesis graph would connect entities such as:

- actions
- agents
- constraints
- proposals
- failures
- stop reasons
- successful paths
- rejected paths

This is useful for:

- discovering recurring failure patterns
- understanding relationships between actions and constraints
- finding which proposals often lead to rejection
- supporting future critic logic
- cross-run reasoning analysis

## Future architecture

Conceptual flow:

```text
Agent / Problem
↓
Planner loop
↓
Executor / SafetyGate
↓
Trace + stop_reason
↓
Append-only Step Log
↓
Hypothesis Graph
↓
Critic / Pattern Analysis / Replay
```

## Non-goals for current MVP

The current MVP does not include:

- Datomic adapter
- Neo4j adapter
- persistent database schema
- docker-compose database setup
- production storage layer

This document is a roadmap, not an implementation claim.
