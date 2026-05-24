# Portfolio Relationship

Status: reviewer-facing ecosystem note.

This document explains how PythiaLabs fits into the broader trustworthy-agent evidence architecture.

Central map:

```text
https://github.com/safal207/L-THREAD-Liminal-Thread-Secure-Protocol-LTP-/blob/main/docs/ECOSYSTEM_SPIDER_MAP.md
```

## Role of this repository

PythiaLabs is the pre-execution evidence gate layer.

It evaluates whether an AI-agent proposed action should be:

```text
ALLOW / BLOCK / ESCALATE
```

before the tool call, transaction, code change, infrastructure action, or governance action happens.

## Ecosystem position

```text
PythiaLabs — pre-execution evidence gates for high-risk agentic actions
LTP — path-level trace/replay/admissibility protocol
CML — causal permission and responsibility lineage
DMP — decision memory and irreversibility governance
LRI — living identity and relational invariants
```

## How PythiaLabs connects to the other layers

| Layer | Relationship |
|---|---|
| LTP | PythiaLabs can produce or consume action-gate evidence that should later be preserved as path-level trace/admissibility evidence. |
| CML | PythiaLabs can use causal permission signals to decide whether an action has a valid parent cause or responsibility chain. |
| DMP | PythiaLabs can escalate decisions that may become irreversible or require durable decision memory. |
| LRI | PythiaLabs can block or escalate actions that cross human identity, agency, revisability, or relational boundaries. |

## Reviewer interpretation

PythiaLabs should not be read as only a Web3 treasury demo.

Web3 treasury is one high-risk scenario. The broader role is:

```text
proposed agent action -> evidence gate -> ALLOW / BLOCK / ESCALATE
```

## Non-claims

PythiaLabs does not claim:

- production security certification;
- regulatory compliance certification;
- replacement of wallet security, transaction simulation, or contract-monitoring tools;
- complete agent safety;
- replacement of human review;
- universal prevention of unsafe actions.

The narrower claim is:

```text
PythiaLabs is an open-source MVP for deterministic pre-execution evidence gates over high-risk agentic actions.
```
