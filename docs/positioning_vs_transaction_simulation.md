# Positioning: PythiaLabs and Transaction Simulation Tools

> **Status:** Positioning note.
> **Scope:** Category clarification for PythiaLabs.
> **Non-goal:** This document does not claim production security, compliance certification, wallet protection, smart-contract auditing, or replacement of existing Web3 tooling.

## Short positioning statement

PythiaLabs evaluates AI-agent proposed actions before execution.

It produces deterministic `ALLOW` / `BLOCK` / `ESCALATE` decisions with reviewer-facing evidence.

Web3 treasury is one high-risk demo scenario, not the product category.

The broader category is:

```text
pre-execution evidence gates for AI-agent actions
```

---

## What transaction simulation tools do

Tools such as Tenderly, Safe transaction simulation, OpenZeppelin Defender, and related Web3 security/operations products are focused on important parts of the wallet, contract, transaction, monitoring, automation, and on-chain execution layers.

They help teams understand and manage what happens when a transaction is prepared, simulated, submitted, monitored, or automated in a blockchain environment.

This is a valuable and well-developed category. PythiaLabs should not be positioned as a replacement for it.

---

## What PythiaLabs does not claim

PythiaLabs does **not** replace:

- transaction simulation,
- wallet security,
- smart-contract auditing,
- on-chain monitoring,
- Defender-style operational automation,
- Safe-style wallet protections,
- formal verification,
- production incident response tooling.

PythiaLabs also does not claim production security, compliance certification, or complete prevention of unsafe actions.

---

## Where PythiaLabs sits in the stack

Transaction simulation tools ask:

```text
What will happen if this transaction is sent?
```

PythiaLabs asks an earlier question:

```text
Should the AI agent be allowed to reach the tool call, transaction, code change, or infrastructure action at all?
```

The distinction is not transaction outcome versus transaction outcome. The distinction is **agent permission and evidence before execution** versus **execution-layer simulation and monitoring**.

A simple stack view:

```text
AI agent proposes action
        ↓
PythiaLabs evidence gate
        ↓
ALLOW / BLOCK / ESCALATE
        ↓
Tool call / transaction simulator / CI / deployment system
        ↓
Execution layer
```

In this model, transaction simulation tools can still be downstream dependencies. PythiaLabs can use their outputs as evidence, but it is not the same layer.

---

## Why Web3 treasury is only a demo scenario

The Web3 treasury demo is useful because it is high-risk, concrete, and easy to understand:

- funds can move,
- governance records matter,
- authorization matters,
- timing matters,
- reviewer evidence matters.

But the demo should not define the product boundary.

The reusable pattern is:

```text
proposed action → evidence → ALLOW / BLOCK / ESCALATE
```

That pattern is broader than Web3.

---

## Generalized scope

The same pre-execution gate pattern applies to high-risk AI-agent workflows across:

- code changes,
- infrastructure operations,
- finance workflows,
- governance actions,
- Web3 treasury actions,
- multi-step agent workflows where tool calls need reviewable evidence.

The common question is:

```text
Do we have enough evidence to let this agent action proceed?
```

---

## Category boundary

PythiaLabs should be described as an upstream review/evidence layer, not as a transaction simulator.

A precise formulation:

```text
PythiaLabs does not replace transaction simulation, wallet security, or contract-monitoring tools; it sits earlier in the workflow, evaluating AI-agent proposed actions before tools are called.
```

This keeps the Web3 demo while avoiding an incorrect direct comparison with mature Web3 execution-layer tools.

---

## README / landing candidate

Candidate sentence for README or landing page:

```text
PythiaLabs does not replace transaction simulation, wallet security, or contract-monitoring tools; it sits earlier in the workflow, evaluating AI-agent proposed actions before tools are called.
```

Shorter variant:

```text
PythiaLabs sits before execution: it evaluates AI-agent proposed actions before tools are called.
```

---

## Practical implication

When presenting PythiaLabs, avoid leading with:

```text
Web3 treasury governance safety tool
```

Prefer:

```text
pre-execution evidence gate for AI-agent proposed actions
```

Then use Web3 treasury as one example of a high-risk workflow where the pattern is visible.