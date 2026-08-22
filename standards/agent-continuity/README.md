# Agent Continuity & Authority

Vendor-neutral specifications and executable conformance checks for preserving operational continuity across context compaction, session restart, and cross-session handoff.

## RFC v0.1

[`RFC-001 — Verifiable Continuation Envelope`](./RFC-001-VERIFIABLE-CONTINUATION-ENVELOPE.md)

defines a bounded, structured envelope that carries the active operational tail without turning memory into hidden authority.

A separate restore-results document records which required reads and evidence checks were actually completed. The envelope declares the gate; restore results satisfy it.

## HRC-001 — Handoff Reachability & Causal Basis

[`HRC-001 — Handoff Reachability & Causal Basis`](./handoff-reachability/HRC-001-HANDOFF-REACHABILITY-CAUSALITY.md)
separates four facts that multi-agent coordination often conflates:

```text
ownership epoch
causal read basis
recipient reachability
predecessor CAS
```

Core boundaries:

> Ownership does not imply reachability.

> A diagnostic that exists but is not surfaced to the sender is not an operational signal.

> Unread predecessor and CAS conflict are different failure classes.

The executable reference uses a two-phase handoff: a target can become `HANDOFF_DELIVERABLE` only after current surfaced reachability is checked, and ownership may advance only after the target acknowledges the exact handoff occurrence and ownership epoch.

## ORC-001 — Orphan Cascade Revocation

[`ORC-001 — Orphan Cascade Revocation`](./handoff-reachability/ORC-001-ORPHAN-CASCADE-REVOCATION.md)
extends HRC ownership epochs into already-running parent/child execution trees.

Core boundaries:

```text
RUNNING != AUTHORIZED
KILL_REQUESTED != EXITED
```

When ownership advances, stale roots and descendants lose side-effect authority immediately through their inherited owner/epoch binding. Process-group cancellation remains a separate cleanup control, and quiescence is only reported after stale executions are observed non-running.

## Problem

Coding agents may lose task continuity after compaction or handoff. They can repeat completed work, violate recent constraints, forget rejected approaches, or confidently reconstruct an execution history that is not supported by durable evidence.

## Core boundary

> Continuity evidence may help an agent resume work, but it must not silently become authority or proof that an action occurred.

## Package

- RFC specification;
- JSON Schemas for the envelope and restore results;
- example envelope and restore results;
- reference validator;
- executable conformance tests;
- additive causal coordination contracts such as HRC-001 and ORC-001.

## Quick validation

```bash
python -m pip install -r standards/agent-continuity/conformance/requirements.txt

python -m unittest discover \
  -s standards/agent-continuity/conformance \
  -p 'test_*.py' -v
```

HRC-001 and ORC-001 can be run independently:

```bash
python -m pip install -r standards/agent-continuity/handoff-reachability/conformance/requirements.txt

python -m unittest discover \
  -s standards/agent-continuity/handoff-reachability/conformance \
  -p 'test_*.py' -v
```

## What the suite verifies

- published JSON Schema enforcement;
- canonical envelope digest integrity;
- trusted-source authority boundaries;
- independent digest/receipt evidence checks;
- required-read completion;
- fail-closed restore behavior;
- unresolved task verification remaining unresolved;
- ownership-epoch gating;
- unread-predecessor versus CAS-conflict separation;
- surfaced and time-bounded reachability;
- exact recipient acknowledgement before handoff commit;
- stale-root and stale-descendant side-effect revocation;
- inherited execution-authority lineage;
- kill-request versus observed-quiescence separation.

## Intended integrations

The specification is implementation-neutral. Codex, Claude Code, IDE agents, CLI agents, and multi-agent runtimes may store or transport the envelope differently while preserving the same observable guarantees.

## Status

Draft v0.1. Discussion and implementation feedback are welcome.
