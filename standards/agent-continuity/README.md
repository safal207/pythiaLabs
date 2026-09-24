# Agent Continuity & Authority

Vendor-neutral specifications and executable conformance checks for preserving operational continuity across context compaction, session restart, and cross-session handoff.

## RFC v0.1

[`RFC-001 — Verifiable Continuation Envelope`](./RFC-001-VERIFIABLE-CONTINUATION-ENVELOPE.md)

defines a bounded, structured envelope that carries the active operational tail without turning memory into hidden authority.

A separate restore-results document records which required reads and evidence checks were actually completed. The envelope declares the gate; restore results satisfy it.

## Problem

Coding agents may lose task continuity after compaction or handoff. They can repeat completed work, violate recent constraints, forget rejected approaches, or confidently reconstruct an execution history that is not supported by durable evidence.

## Core boundary

> Continuity evidence may help an agent resume work, but it must not silently become authority or proof that an action occurred.

## Package

- RFC specification;
- JSON Schemas for the envelope and restore results;
- example envelope and restore results;
- reference validator;
- executable conformance tests.

## Quick validation

```bash
python -m pip install -r standards/agent-continuity/conformance/requirements.txt

python -m unittest discover \
  -s standards/agent-continuity/conformance \
  -p 'test_*.py' -v
```

## What the suite verifies

- published JSON Schema enforcement;
- canonical envelope digest integrity;
- trusted-source authority boundaries;
- independent digest/receipt evidence checks;
- required-read completion;
- fail-closed restore behavior;
- unresolved task verification remaining unresolved.

## ELR-001 — Evidence Logistics Routing

[`ELR-001 — Evidence Logistics Routing`](./evidence-routing/ELR-001-EVIDENCE-LOGISTICS-ROUTING.md)
adds a contextual proof-path router above individual authorization mechanisms.

Core rule:

> First filter by hard proof obligations. Then choose the lowest-cost admissible route.

The executable reference uses Dijkstra over `(graph node, accumulated proofs)` so a cheap path cannot compensate for missing mandatory evidence. The suite covers sync/async route choice, freshness, authority/state/policy drift, risk/reversibility constraints, deterministic tie-breaks and tamper-evident route receipts.

## Intended integrations

The specification is implementation-neutral. Codex, Claude Code, IDE agents, CLI agents, and multi-agent runtimes may store or transport the envelope differently while preserving the same observable guarantees.

## Status

Draft v0.1. Discussion and implementation feedback are welcome.
