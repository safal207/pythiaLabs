# Reviewer Start Here

This is the shortest entry point for grant, fellowship, and external reviewers.

## One sentence

PythiaLabs is an open-source MVP for deterministic pre-execution evidence gates over high-risk AI-agent actions.

## Core flow

```text
AI agent proposes action -> evidence gate -> ALLOW / BLOCK / ESCALATE
```

PythiaLabs sits before tool calls, code changes, infrastructure actions, financial workflows, governance actions, or public-sector actions.

## Review in five minutes

1. Read [`docs/REVIEWER_FIRST_SCREEN.md`](docs/REVIEWER_FIRST_SCREEN.md).
2. Read [`docs/REVIEWER_PATH.md`](docs/REVIEWER_PATH.md).
3. Read [`docs/PYTHIALABS_ONE_PAGE_SUMMARY.md`](docs/PYTHIALABS_ONE_PAGE_SUMMARY.md).
4. Run:

```bash
mix deps.get
mix test
make demo
```

5. Read [`docs/NON_CLAIMS.md`](docs/NON_CLAIMS.md).
6. Read [`AI_SAFETY_PORTFOLIO.md`](AI_SAFETY_PORTFOLIO.md) for the broader research map.

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

## Bottom line

PythiaLabs makes one missing layer inspectable:

```text
Should this AI-agent proposed action be allowed before execution?
```
