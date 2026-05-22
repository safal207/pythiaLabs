# Grant Readiness Pack — PythiaLabs

## One-sentence pitch

PythiaLabs is an open-source prototype for deterministic pre-execution evidence gates for high-risk AI-agent actions. It evaluates whether proposed actions should be allowed, blocked, or escalated before tools are called, producing reviewer-facing evidence artifacts, stable stop reasons, and replayable traces.

## Problem statement

AI agents are moving from text generation into real actions: code changes, infrastructure operations, financial workflows, governance actions, and tool calls. Prompt instructions, informal review, and after-the-fact logs are weak safety boundaries when an action may affect money, infrastructure, permissions, or public-sector workflows.

Teams need a reproducible way to answer:

```text
Should this proposed AI-agent action be allowed to execute now,
blocked before execution,
or escalated to a human reviewer?
```

PythiaLabs explores this missing control layer between agent intent and execution.

## Why now

- AI-assisted operational workflows are moving into higher-impact settings.
- Grant programs increasingly prioritize transparency, risk controls, and measurable governance outcomes.
- Existing logs often explain what happened after the fact, not whether an action should have reached execution.
- A deterministic, local-first evidence gate can be reviewed without private infrastructure or production credentials.

## Current implemented demos

PythiaLabs currently ships deterministic local demos and tests demonstrating:

- agent action gating with stable stop reasons,
- decision-time evidence checks,
- bitemporal authorization reasoning,
- infrastructure-adjacent action safety checks,
- banking / financial-risk action checks,
- Web3 treasury governance checks,
- deterministic trace export,
- evidence packaging and SHA-256 verification,
- tamper-detection examples,
- reviewer-facing expected-output documentation,
- a single-command paid review demo via `make demo`.

Web3 treasury is one high-risk demo scenario, not the product category. The broader category is pre-execution evidence gates for AI-agent proposed actions.

## Target users and reviewers

- AI safety and AI governance researchers,
- agent framework / tool-calling developers,
- platform and DevOps teams adopting AI agents,
- grant programs and public-goods review committees,
- internet-freedom and civil-society tooling maintainers,
- financial, infrastructure, governance, and compliance-oriented teams,
- open-source maintainers experimenting with reviewer-facing action traces.

## Public-goods value

- Provides an inspectable safety pattern for pre-execution action review.
- Makes high-risk agent decisions easier to reproduce and audit.
- Gives small teams a local-first artifact they can fork, inspect, and adapt.
- Separates evidence-gate logic from downstream execution systems.
- Creates a path toward benchmarkable evaluation of action governance.

## Current limitations

PythiaLabs is still an MVP. It currently does not claim:

- production enforcement,
- production cryptography,
- wallet integration,
- smart-contract execution,
- RPC/indexer integration,
- cloud-provider integration,
- IAM enforcement,
- regulatory compliance,
- certified cybersecurity protection,
- replacement of human review,
- replacement of CI, transaction simulation, or runtime security tooling.

The current value is a reproducible evidence-gate prototype, not a production control product.

## Proposed grant scopes

### Scope A — Reviewer-Ready Evidence Gate Baseline

Goal: turn the current MVP into a clean reviewer-ready baseline.

Deliverables:

- final reviewer path table,
- updated documentation index,
- cleaned roadmap board,
- evidence artifact examples,
- stop-reason glossary,
- refreshed quickstart and demo notes,
- short final technical memo.

### Scope B — Benchmarkable Demo and Evaluation Pack

Goal: move from demos to a small benchmarkable evaluation pack.

Deliverables:

- versioned evidence artifact conventions,
- deterministic scenario fixtures,
- expected ALLOW / BLOCK / ESCALATE outcomes,
- negative-path examples,
- verifier / reviewer-report prototype plan,
- comparison plan against prompt-only guardrails and after-the-fact logging.

### Scope C — Open Evidence-Gate Toolkit

Goal: build a reusable open-source toolkit around schemas, fixtures, replay checks, reviewer reports, and integration guidance.

Deliverables:

- evidence artifact and replay specification,
- multi-domain scenario corpus,
- local verifier / report prototype,
- contributor and maintainer workflow hardening,
- adapter notes for CI, MCP/tool-calling, coding-agent, and human review workflows,
- final grant report and demo package.

## Budget ladder

These are illustrative scopes for grant design and can be adapted to a specific program.

### Example plan — 20k USD

Best fit: small foundation grant, ecosystem microgrant, rapid research support, public-goods grant.

- Milestone 1 — reviewer path hardening: 5k USD
- Milestone 2 — evidence schema refinement: 6k USD
- Milestone 3 — small deterministic scenario pack: 6k USD
- Milestone 4 — final report and demo refresh: 3k USD

Expected outcome: a reviewer can clone the repository, run the demo, inspect artifacts, and understand the research direction in under 30 minutes.

### Example plan — 35k USD

Best fit: AI safety research grant, open-source infrastructure grant, internet-freedom tooling grant, governance tooling grant.

- Milestone 1 — trace and artifact schema hardening: 8k USD
- Milestone 2 — deterministic scenario benchmark: 10k USD
- Milestone 3 — reviewer report prototype: 7k USD
- Milestone 4 — adapter/readiness documentation: 5k USD
- Milestone 5 — final evaluation memo: 5k USD

Expected outcome: PythiaLabs becomes a reusable open-source evaluation artifact for deterministic pre-execution action gates.

### Example plan — 50k USD

Best fit: serious seed grant, AI governance / safety grant, civil-society tooling grant, public-goods infrastructure program.

- Milestone 1 — evidence artifact and replay specification: 10k USD
- Milestone 2 — multi-domain scenario corpus: 12k USD
- Milestone 3 — local verifier / report prototype: 10k USD
- Milestone 4 — contributor and maintainer workflow hardening: 5k USD
- Milestone 5 — comparative evaluation plan: 7k USD
- Milestone 6 — final grant report and demo package: 6k USD

Expected outcome: the repository becomes credible as a follow-on candidate for larger funding because the research object is clear, reproducible, and measurable.

### Larger follow-on path — 75k to 100k+ USD

A larger follow-on grant can fund:

- formal schema and conformance tests,
- replay and regression suite,
- multi-agent / multi-tool workflow cases,
- adapter prototypes,
- independent review package,
- longer technical report and benchmark results.

Expected outcome: PythiaLabs becomes a public, inspectable, extensible evidence-gate layer for high-risk AI-agent action governance.

## Recommended ask positioning

For a first serious external grant, the strongest ask is usually:

```text
35k–50k USD for 3–5 months
```

Why this range is credible:

- large enough to produce real artifacts beyond documentation,
- small enough to be plausible for an independent maintainer,
- scoped around reproducible open-source deliverables,
- expandable into a larger follow-on grant if benchmark and reviewer artifacts land.

A conservative first ask:

```text
20k–25k USD for reviewer-ready baseline + small scenario pack
```

An ambitious but still defensible first ask:

```text
50k USD for an open evidence-gate toolkit with schemas, fixtures, verifier/report prototype, and evaluation plan
```

## Suggested grant reviewer checklist

A reviewer can ask:

- Can I run a demo locally without private infrastructure?
- Does the system produce stable decisions and stop reasons?
- Is there an explicit evidence path from input to decision?
- Are current limitations stated clearly?
- Is the category boundary clear: pre-execution evidence gate, not downstream execution simulation?
- Is there a plausible path from prototype to benchmarkable research infrastructure?

## Current strongest positioning

Use this formulation in applications:

```text
PythiaLabs is an open-source prototype for deterministic pre-execution evidence gates for AI-agent actions. It evaluates whether proposed high-risk actions should be allowed, blocked, or escalated before tools are called, producing reviewer-facing evidence and replayable traces.
```
