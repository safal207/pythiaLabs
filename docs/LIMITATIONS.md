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

## Lotus judgment boundary

The [`Pythia Lotus Layer`](../LOTUS.md) adds a human-readable judgment contract, not a new enforcement claim.

- A verdict must expose its evidence and uncertainty.
- `ALLOW` does not execute the proposed action and does not create missing authorization.
- A prior verdict does not remain valid after relevant inputs, policy, environment, credentials, recovery context, or code state change.
- `BLOCK` is a gate result, not punishment or proof of malicious intent.
- `ESCALATE` is an explicit outcome when configured policy cannot safely decide.
- Human reviewers must remain able to reproduce and challenge the decision.

These principles do not upgrade the MVP into a certified safety system, guarantee good outcomes, or replace domain-specific authorization and execution controls.

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
