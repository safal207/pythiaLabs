# PythiaLabs Non-Claims

Status: reviewer-facing scope boundary.

This document explains what PythiaLabs does not claim.

## Purpose

PythiaLabs is intentionally narrow.

It contributes one focused primitive:

```text
pre-execution evidence gates for high-risk AI-agent proposed actions
```

The project is strongest when its claims remain specific, deterministic, and reproducible.

## What PythiaLabs claims

PythiaLabs claims that proposed high-risk AI-agent actions can be evaluated before execution using deterministic evidence gates.

The current reviewer-safe pattern is:

```text
AI agent proposes action -> evidence gate -> ALLOW / BLOCK / ESCALATE
```

PythiaLabs can help inspect whether an action has enough evidence, authorization, context, and recovery viability to proceed.

## What PythiaLabs does not claim

PythiaLabs does not claim:

- full AI alignment;
- complete agent safety;
- production security certification;
- certified regulatory compliance;
- wallet security;
- smart-contract auditing;
- transaction simulation;
- on-chain monitoring;
- replacement of Safe, Tenderly, OpenZeppelin Defender, or similar tools;
- replacement of CI/CD systems;
- replacement of cloud IAM, backup, or incident-response systems;
- replacement of human review;
- universal prevention of unsafe actions;
- production-grade cybersecurity protection;
- medical, clinical, legal, or financial advice.

## Not a Web3 transaction simulator

PythiaLabs is not a Web3 transaction simulator.

Transaction simulation tools usually ask:

```text
What will happen if this transaction is sent?
```

PythiaLabs asks an earlier question:

```text
Should the AI agent be allowed to reach the tool call, transaction, code change, infrastructure action, or governance action at all?
```

Web3 treasury is one high-risk demo scenario, not the product category.

## Not a wallet or contract-security tool

PythiaLabs does not replace wallet security, smart-contract auditing, formal verification, on-chain monitoring, or transaction-simulation tooling.

Those tools can be downstream evidence sources.

PythiaLabs sits before execution and evaluates whether the proposed agent action should proceed.

## Not a production enforcement system

PythiaLabs is currently an open-source MVP with deterministic local demos.

It should not be represented as a production enforcement system, certified safety framework, or compliance product.

## Not a generic memory product

PythiaLabs is not primarily an organizational memory product.

It focuses on pre-execution action gates:

```text
proposed action -> evidence -> decision -> reviewer artifact
```

Memory, trace, and audit layers may support this process, but they are not the product boundary.

## Demo limitation

The current demos are deterministic local showcases.

They are useful for review and reproducibility, but they do not prove broad real-world safety performance.

Reviewer-safe demo statement:

```text
PythiaLabs includes deterministic local demos for pre-execution action-gate evaluation across high-risk scenarios.
```

Do not inflate this into production readiness or certified protection.

## Correct funding framing

The strongest funding framing is:

```text
PythiaLabs is an open-source MVP for deterministic pre-execution evidence gates over high-risk AI-agent actions.
```

It should be funded to expand:

- scenario coverage;
- reproducible fixtures;
- evidence artifact schemas;
- reviewer reports;
- benchmark harnesses;
- integration examples;
- external validation;
- safety-boundary documentation.

## Bottom line

PythiaLabs is not trying to replace downstream tools.

It is trying to make one missing layer inspectable:

```text
Should this AI-agent proposed action be allowed before execution?
```
