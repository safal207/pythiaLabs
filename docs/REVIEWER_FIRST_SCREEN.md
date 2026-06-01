# Reviewer First Screen

Status: shortest entry point for grant, fellowship, and external reviewers.

## One sentence

PythiaLabs is an open-source MVP for deterministic pre-execution evidence gates over high-risk AI-agent actions.

## Core flow

```text
AI agent proposes action -> evidence gate -> ALLOW / BLOCK / ESCALATE
```

PythiaLabs sits before tool calls, code changes, infrastructure actions, financial workflows, governance actions, or public-sector actions.

## Review in five minutes

1. Read `docs/REVIEWER_PATH.md`.
2. Read `docs/PYTHIALABS_ONE_PAGE_SUMMARY.md`.
3. Run:

```bash
mix deps.get
mix test
make demo
```

4. Read `docs/NON_CLAIMS.md`.
5. Read `AI_SAFETY_PORTFOLIO.md` if you want the broader research map.

## What PythiaLabs is

PythiaLabs is a deterministic action-gate layer. It asks whether a proposed high-risk action has sufficient evidence, authorization, context, and recovery viability to proceed.

It produces:

- explicit `ALLOW / BLOCK / ESCALATE` decisions;
- stable stop reasons;
- replayable traces;
- tamper-checkable evidence artifacts;
- local deterministic demos.

## What PythiaLabs is not

PythiaLabs is not:

- a Web3 transaction simulator;
- a wallet security tool;
- a smart-contract auditor;
- a production enforcement system;
- a certified safety framework;
- a compliance product;
- a replacement for human review.

Web3 treasury is one demo scenario, not the product boundary.

## Best current funding framing

```text
Fund PythiaLabs to expand deterministic, reproducible, open-source evidence gates for high-risk AI-agent actions.
```

Near-term work:

- expand scenario coverage;
- harden evidence schemas;
- improve local demo reproducibility;
- add benchmark-style fixtures;
- publish reviewer reports;
- clarify safety boundaries and non-claims;
- gather external technical feedback.

## Bottom line

PythiaLabs makes one missing layer inspectable:

```text
Should this AI-agent proposed action be allowed before execution?
```
