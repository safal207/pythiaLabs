# Agent Continuity & Authority

Vendor-neutral specifications and executable conformance checks for preserving operational continuity across context compaction, session restart, and cross-session handoff.

## RFC v0.1

[`RFC-001 — Verifiable Continuation Envelope`](./RFC-001-VERIFIABLE-CONTINUATION-ENVELOPE.md)

defines a bounded, structured envelope that carries the active operational tail without turning memory into hidden authority.

## Problem

Coding agents may lose task continuity after compaction or handoff. They can repeat completed work, violate recent constraints, forget rejected approaches, or confidently reconstruct an execution history that is not supported by durable evidence.

## Core boundary

> Continuity evidence may help an agent resume work, but it must not silently become authority or proof that an action occurred.

## Package

- RFC specification;
- JSON Schema for the envelope;
- example envelope;
- standard-library conformance tests.

## Quick validation

```bash
python -m unittest discover \
  -s standards/agent-continuity/conformance \
  -p 'test_*.py' -v
```

## Intended integrations

The specification is implementation-neutral. Codex, Claude Code, IDE agents, CLI agents, and multi-agent runtimes may store or transport the envelope differently while preserving the same observable guarantees.

## Status

Draft v0.1. Discussion and implementation feedback are welcome.
