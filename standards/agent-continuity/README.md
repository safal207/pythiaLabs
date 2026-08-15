# Agent Continuity & Authority

Vendor-neutral specifications and executable conformance checks for preserving operational continuity across context compaction, session restart, cross-session handoff, authority change, and delayed authorization.

## RFC v0.1

[`RFC-001 — Verifiable Continuation Envelope`](./RFC-001-VERIFIABLE-CONTINUATION-ENVELOPE.md)

defines a bounded, structured envelope that carries the active operational tail without turning memory into hidden authority.

A separate restore-results document records which required reads and evidence checks were actually completed. The envelope declares the gate; restore results satisfy it.

## Executable sibling contracts

### ACI-001 — Authority Causality Invariant

[`authority-causality/`](./authority-causality/)

makes authority itself causal and versioned. It separates state freshness from current mutation authority and mechanically rejects stale/split authority.

### ACB-001 — Authorization Consumption Boundary

[`authorization-consumption/`](./authorization-consumption/)

separates semantic decision identity, exact authorization occurrence, and concrete execution occurrence. It fails closed when consent is stale, ambiguous, cancelled, superseded, scope-mismatched, or already consumed.

The two contracts answer different questions:

```text
ACI: may this actor act now?
ACB: which exact permission may this exact execution consume now?
```

For consequential effects a runtime may require both.

## Problem

Coding agents may lose task continuity after compaction or handoff. They can repeat completed work, violate recent constraints, forget rejected approaches, or confidently reconstruct an execution history that is not supported by durable evidence. Long-lived or deferred approvals add another failure mode: a historically valid `ALLOW` can be replayed after arguments, authority, policy, state, cancellation status, or execution occurrence has changed.

## Core boundary

> Continuity evidence may help an agent resume work, but it must not silently become authority or proof that an action occurred.

And for authorization:

> Valid historical consent does not imply current execution authority.

## Package

- RFC specification;
- JSON Schemas for the envelope and restore results;
- example envelope and restore results;
- reference validator;
- executable conformance tests;
- ACI authority-causality contract;
- ACB authorization-consumption contract.

## Quick validation

Base continuation suite:

```bash
python -m pip install -r standards/agent-continuity/conformance/requirements.txt

python -m unittest discover \
  -s standards/agent-continuity/conformance \
  -p 'test_*.py' -v
```

ACB-001:

```bash
python -m pip install -r standards/agent-continuity/authorization-consumption/conformance/requirements.txt

python -m unittest discover \
  -s standards/agent-continuity/authorization-consumption/conformance \
  -p 'test_*.py' -v
```

## What the suites verify

- published JSON Schema enforcement;
- canonical digest integrity;
- trusted-source authority boundaries;
- independent digest/receipt evidence checks;
- required-read completion;
- fail-closed restore behavior;
- unresolved task verification remaining unresolved;
- exact authorization occurrence resolution;
- execution-scope binding;
- freshness revalidation;
- one-shot and explicit reusable consumption semantics;
- cancellation/supersession blocking;
- semantic-decision collision ambiguity rather than silent first-match resolution.

## Intended integrations

The specifications are implementation-neutral. Codex, Claude Code, CrewAI, AG2, IDE agents, CLI agents, and multi-agent runtimes may store or transport these records differently while preserving the same observable guarantees.

## Status

Draft v0.1. Discussion and implementation feedback are welcome.
