# Agent Continuity & Authority

Vendor-neutral specifications and executable conformance checks for preserving operational continuity across context compaction, session restart, cross-session handoff, and CI/CD phase transitions.

## RFC v0.1

[`RFC-001 — Verifiable Continuation Envelope`](./RFC-001-VERIFIABLE-CONTINUATION-ENVELOPE.md)

defines a bounded, structured envelope that carries the active operational tail without turning memory into hidden authority.

A separate restore-results document records which required reads and evidence checks were actually completed. The envelope declares the gate; restore results satisfy it.

## CI Operational Checkpoint v0.1

[`CI-OPERATIONAL-CHECKPOINT-V0.1.md`](./CI-OPERATIONAL-CHECKPOINT-V0.1.md)

specializes the continuity boundary for agentic CI/CD work. It records exact
workspace identity, goal, constraints, rejected approaches, verification state,
and the next action while fixing authority to `context_only`.

The profile deterministically returns:

```text
CONTINUE
REVALIDATE_WORKSPACE
RESTART_REQUIRED
IDEMPOTENT_REPLAY
REJECT_LINEAGE_MISMATCH
REJECT_UNVERIFIED_COMPLETION
REJECT_INVALID_AUTHORITY
```

A checkpoint may preserve the intent to merge or deploy, but it cannot authorize
that action. A fresh Action Envelope and current exact-target evidence remain
mandatory.

## Problem

Coding agents may lose task continuity after compaction or handoff. They can repeat completed work, violate recent constraints, forget rejected approaches, or confidently reconstruct an execution history that is not supported by durable evidence.

## Core boundary

> Continuity evidence may help an agent resume work, but it must not silently become authority or proof that an action occurred.

## Package

- RFC specification;
- CI operational checkpoint profile;
- JSON Schemas for envelopes, restore results, and CI checkpoints;
- complete examples;
- deterministic reference validators;
- executable conformance tests;
- stable CI checkpoint outcome registry.

## Quick validation

```bash
python -m pip install -r standards/agent-continuity/conformance/requirements.txt

python -m unittest discover \
  -s standards/agent-continuity/conformance \
  -p 'test_*.py' -v
```

## What the suite verifies

- published JSON Schema enforcement;
- canonical envelope and checkpoint digest integrity;
- trusted-source authority boundaries;
- independent digest/receipt evidence checks;
- required-read completion;
- fail-closed restore behavior;
- unresolved task verification remaining unresolved;
- CI workspace drift detection;
- lineage, replay, rejected-approach, and verification continuity;
- fresh authorization requirements for merge and deploy intent.

## Intended integrations

The specifications are implementation-neutral. Codex, Claude Code, IDE agents, CLI agents, CI bots, and multi-agent runtimes may store or transport the envelopes differently while preserving the same observable guarantees.

## Status

Draft v0.1. Discussion and implementation feedback are welcome.
