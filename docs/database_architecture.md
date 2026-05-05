# PythiaLabs Database Architecture

PythiaLabs uses a three-layer memory architecture:

> **Postgres for product state, TimescaleDB for temporal observability, and LiminalDB as a native adaptive causal-memory substrate for agentic systems.**

This document defines the intended database responsibilities for the PythiaLabs stack.

## Architecture summary

```text
PythiaLabs
  ├─ Postgres
  │  └─ product state: users, projects, auth, configs, permissions, billing
  │
  ├─ TimescaleDB
  │  └─ temporal observability: metrics, runs, latency, benchmarks, time-series traces
  │
  └─ LiminalDB
     └─ adaptive causal memory: transitions, replay, mirror timelines, salience, seeds, reflexes
```

## Layer responsibilities

| Layer | Database | Responsibility |
|---|---|---|
| Product state | Postgres | Accounts, projects, settings, grants, auth, billing, permissions |
| Temporal observability | TimescaleDB | Agent runs, benchmark metrics, latency, time-series telemetry, trace metrics |
| Adaptive causal memory | LiminalDB | Agent transitions, replayable history, causal traces, seed lifecycles, salience, reflex loops |

## Why this split exists

PythiaLabs should not treat every type of memory as the same kind of data.

Traditional SaaS state, time-series observability, and agentic causal memory have different invariants:

- **Product state** needs transactional reliability and mature operational tooling.
- **Temporal observability** needs efficient time-window queries, aggregation, and trend analysis.
- **Causal memory** needs replay, append-only traces, transition semantics, and explainable state evolution.

Therefore, PythiaLabs separates business truth, temporal evidence, and adaptive memory into distinct layers.

## Canonical mapping

### Postgres

Postgres is the operational database for the product layer.

Use it for:

- users,
- organizations,
- projects,
- grants,
- API keys,
- permissions,
- billing state,
- configuration,
- stable product entities.

Postgres is not the causal-memory engine. It stores normal product state.

### TimescaleDB

TimescaleDB is the observability and time-series layer.

Use it for:

- agent run metrics,
- latency measurements,
- benchmark results,
- event rates,
- time-window analytics,
- performance trends,
- operational telemetry.

TimescaleDB is not the source of causal meaning. It stores temporal measurements and observability signals.

### LiminalDB

LiminalDB is the native adaptive memory substrate.

Use it for:

- agent transitions,
- causal traces,
- replayable decisions,
- mirror timelines,
- seed lifecycles,
- variant paths,
- salience-aware memory,
- reflex loops,
- adaptive runtime memory.

LiminalDB is where PythiaLabs models memory as an active participant in decision-making, not as passive storage.

## Future adapters and baselines

The following systems may be added later as adapters, projections, or research baselines:

| System | Future role |
|---|---|
| Neo4j | Graph projection for visualizing agents, decisions, traces, claims, policies, and causal links |
| XTDB | Bitemporal research baseline and possible adapter for valid-time/system-time comparisons |
| Datomic | Reference architecture for immutable facts and Datalog-style reasoning |

These systems are not the MVP source of truth.

## Source-of-truth rule

PythiaLabs should avoid having multiple competing sources of truth.

The intended rule is:

```text
Postgres = product truth
TimescaleDB = temporal measurement truth
LiminalDB = adaptive causal-memory truth
```

Derived projections may be rebuilt from their source layers. Projections must not silently mutate causal history.

## Positioning

PythiaLabs is not just integrating existing databases.

It uses conventional databases where they are strongest, and uses LiminalDB where agentic systems need a different memory model:

> **PythiaLabs combines mature product storage, temporal observability, and a native adaptive causal-memory substrate for safe agentic systems.**

This makes the stack understandable to engineers while preserving the original research contribution of LiminalDB.
