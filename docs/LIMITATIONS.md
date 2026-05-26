# PythiaLabs Limitations

Status: reviewer-facing scope note.

PythiaLabs is intentionally narrow.

## Current claim

```text
PythiaLabs is an open-source MVP for deterministic pre-execution evidence gates over high-risk AI-agent actions.
```

## What the current project demonstrates

PythiaLabs demonstrates:

- deterministic `ALLOW / BLOCK / ESCALATE` decisions;
- stable stop reasons;
- local demos;
- evidence artifact documentation;
- reviewer-facing traces;
- pre-execution review patterns for proposed agent actions.

## What it does not claim

PythiaLabs does not claim:

- full AI alignment;
- certified deployment readiness;
- universal prevention of bad outcomes;
- replacement of human review;
- replacement of domain-specific review tools;
- complete agent governance;
- broad real-world generalization from the current demos.

## Product category boundary

PythiaLabs is not primarily a Web3 transaction simulator.

Web3 treasury is one high-risk demo scenario, not the product category.

The general pattern is:

```text
proposed agent action -> evidence gate -> ALLOW / BLOCK / ESCALATE
```

## Demo limitation

Current demos are deterministic local artifacts.

They are useful as reviewer-facing seed evidence, but they do not prove broad deployment readiness.

## Correct funding framing

The strongest funding framing is:

```text
an applied open-source action-gate layer for making high-risk AI-agent proposed actions more inspectable before execution
```

Recommended expansion areas:

- deterministic scenario coverage;
- evidence artifact schemas;
- verifier and reporting paths;
- external validation;
- integrations with LTP and CML;
- reviewer-facing reproducibility.
