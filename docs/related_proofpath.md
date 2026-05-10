# Related prototype: ProofPath

ProofPath is a separate open-source repository that implements a small, runnable reference prototype of the PythiaLabs evidence-gate idea.

Repository:

https://github.com/safal207/ProofPath

## Relationship to PythiaLabs

PythiaLabs is the broader evidence-gate research/product framing:

```text
Should this high-risk AI-agent action be allowed, blocked, or escalated under current evidence?
```

ProofPath is a minimal protocol/gateway laboratory focused on HTTP/API actions:

```text
agent action -> ProofPath decision -> forward or block -> audit trail
```

They are not the same project.

ProofPath is useful as a runnable reference implementation and community lab for one concrete form of evidence gate.

## Why this matters

A model or agent can have valid tool access, credentials, and HTTPS transport while still proposing an invalid or unsafe action.

ProofPath demonstrates a pre-execution action boundary that checks:

- declared intent;
- causal parent;
- action scope;
- reversibility;
- human approval when required;
- gateway decision;
- auditability.

## Current ProofPath artifacts

ProofPath currently includes:

- protocol draft;
- Rust verifier;
- Axum gateway;
- upstream forwarding;
- dangerous AI-agent action demo;
- real-model-agent demo;
- hash-chained JSONL audit log;
- community experiment levels.

Core line:

> HTTPS protects the connection. ProofPath protects the meaning of the action.

## Positioning

Use ProofPath as:

```text
A runnable reference implementation of pre-execution action gates for AI agents.
```

Use PythiaLabs as:

```text
The broader deterministic evidence-gate framework for high-risk agentic actions.
```
