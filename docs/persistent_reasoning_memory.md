# Persistent Reasoning Memory Roadmap

## Current status

PythiaLabs currently returns trace data per run.
The current MVP does not require external storage services to run demos, tests, or the Agent Safety Showcase.

This document describes a roadmap for future versions. It is not an implementation claim.

## Roadmap intent

Future versions may add persistent reasoning memory to compare behavior across many runs and versions.

A minimal first step is:

- append-only step log for planner and executor traces
- hypothesis graph for linking related steps, constraints, and outcomes

## Why this roadmap exists

Single-run traces are useful for local debugging and explainability.
Persistent memory may later improve:

- replay and auditability across runs
- long-horizon failure analysis
- critic inputs for recurring error patterns
- evaluation across model or policy versions

## Scope notes

This roadmap is documentation-only for the current MVP.
No storage adapter, schema, or runtime persistence behavior is implemented here.

## Related roadmap

For a broader future architecture that includes fact memory, graph memory, bitemporal temporal memory, event streams, and metrics timelines, see:

docs/temporal_causal_memory_stack.md
