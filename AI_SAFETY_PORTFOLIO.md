# AI Safety Portfolio Map

Status: reviewer-facing map for grant, fellowship, and collaboration reviewers.

This file explains how the related repositories fit together. The goal is to make the portfolio look like one research program, not a scattered set of unrelated prototypes.

## One-line research program

Deterministic evidence, intent, and causal accountability layers for high-risk AI-agent actions before they create real-world effects.

## Main funding object

### PythiaLabs

**Role:** pre-execution evidence gates.

PythiaLabs evaluates whether a proposed high-risk AI-agent action has enough evidence, authorization, context, and recovery viability to proceed.

```text
AI agent proposes action -> evidence gate -> ALLOW / BLOCK / ESCALATE
```

Best reviewer framing:

```text
PythiaLabs is an open-source MVP for deterministic pre-execution evidence gates over high-risk AI-agent actions.
```

PythiaLabs is the best entry point for reviewers because it is narrow, reproducible, and directly tied to action governance.

## Related layers

### ProofPath

**Role:** verifiable intent and action-boundary audit.

ProofPath focuses on whether a critical action is causally authorized and auditable at the execution boundary.

```text
valid credential != valid action != valid scope != valid reversibility != valid approval
```

Use ProofPath when the reviewer cares about API boundaries, payment guards, CI evidence gates, or local approval rails for coding agents.

### CML — Causal Memory Layer

**Role:** causal permission and responsibility lineage.

CML records not only what happened, but why an action was allowed, blocked, or escalated. It is the causal accountability layer behind oversight decisions.

### LTP — Liminal Thread Protocol

**Role:** trace, replay, and admissibility path.

LTP structures multi-step agent traces so that decisions can be replayed, compared, and audited across sessions.

### LiminalQAengineer

**Role:** QA reliability substrate.

LiminalQAengineer applies causal and bi-temporal reasoning to CI/test workflows. It is not the main AI safety object, but it supports the engineering reliability background behind the portfolio.

## Recommended reviewer paths

### For AI safety / MATS / OpenAI-style reviewers

1. Read `README.md`.
2. Read `docs/REVIEWER_PATH.md`.
3. Read `docs/PYTHIALABS_ONE_PAGE_SUMMARY.md`.
4. Run `make demo`.
5. Read `docs/NON_CLAIMS.md`.
6. If interested in execution-boundary security, inspect ProofPath.

### For NLnet / open-source infrastructure reviewers

1. Start with PythiaLabs as the primary open-source action-gate toolkit.
2. Inspect the evidence artifact schema and deterministic demo cases.
3. Review limitations and non-claims.
4. Use LiminalQAengineer only as related infrastructure background.

### For OTF / internet freedom reviewers

1. Start with `docs/OTF_REVIEWER_PATH.md`.
2. Inspect how evidence gates apply to high-risk internet tooling workflows.
3. Review reproducibility, local execution, and non-claims.

## What this portfolio is not

This portfolio does not claim:

- full AI alignment;
- complete agent safety;
- production security certification;
- regulatory compliance;
- replacement of human review;
- universal prevention of unsafe actions.

The current contribution is narrower:

```text
make high-risk AI-agent actions inspectable before execution.
```

## Current strategy

Use PythiaLabs as the cleanest grant-facing entry point.

Use ProofPath as the security/action-boundary companion.

Use CML and LTP as the research architecture.

Use LiminalQAengineer as evidence of reliability engineering experience and causal QA tooling.

## Bottom line

The portfolio should be read as a layered safety stack:

```text
PythiaLabs -> evidence gate
ProofPath -> intent and audit boundary
CML -> causal accountability
LTP -> trace and replay protocol
LiminalQAengineer -> reliability substrate
```

The shared thesis:

```text
AI-agent actions should be reviewable, replayable, and evidence-backed before execution.
```
