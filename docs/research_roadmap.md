# Research Roadmap: PythiaLabs, LTP, and CML

PythiaLabs is the product-facing pre-execution gate.

LTP and CML are the broader research stack for deterministic oversight of agent traces.

This document explains how they relate without collapsing them into one message.

## Short version

> PythiaLabs decides before the agent acts.
>
> LTP + CML explain how agent failures enter the trace.

PythiaLabs should remain easy to understand from the landing page:

```text
proposed action → evidence → ALLOW / BLOCK / ESCALATE
```

The research track can go deeper:

```text
agent trace → causal memory → deterministic replay → failure localization → benchmark evidence
```

## Why keep the messages separate?

PythiaLabs has a practical market-facing promise:

- evaluate one risky agent workflow,
- identify required decision-time evidence,
- return ALLOW / BLOCK / ESCALATE criteria,
- produce reviewer-facing artifacts,
- support paid pre-execution safety reviews.

LTP + CML have a research-facing promise:

- represent agent traces deterministically,
- preserve causal memory over decisions,
- make failures reproducible,
- compare trace-based oversight against behavior-only evaluation,
- produce benchmarks and evaluation reports.

If both messages are mixed too early, visitors may not know whether they should:

- run a demo,
- request a paid review,
- fund research,
- read a protocol spec,
- or inspect an evidence artifact.

The clean split is:

- **PythiaLabs** — product entry point and runnable proof.
- **LTP + CML** — research depth and grant track.

## Relationship between the layers

| Layer | Role | Primary question |
|---|---|---|
| PythiaLabs | Pre-execution action gate | Should this agent action run? |
| Evidence Artifact | Reviewer-facing output | Why was the decision made? |
| LTP | Deterministic trace protocol | What happened in the agent trace? |
| CML | Causal memory layer | Where did the failure enter the causal chain? |
| LTP-Bench | Evaluation corpus | Can oversight methods find the failure reproducibly? |

## Positioning formula

```text
PythiaLabs = gate before action
LTP = trace protocol after/between actions
CML = causal memory over decision history
```

Or:

```text
PythiaLabs controls execution.
LTP records execution context.
CML explains causal validity.
```

## Related funding track

The broader research direction is represented by the Manifund proposal:

**Deterministic Oversight for Agent Traces — LTP + CML**

Reference:

<https://manifund.org/projects/deterministic-oversight-for-agent-traces--ltp--cml>

The proposal track is about research funding and benchmark development. It should not replace the PythiaLabs paid-review offer.

## What this research track aims to ship

### 1. LTP-Bench

A small benchmark suite of adversarial or failure-prone agent traces.

Expected properties:

- labeled trace failures,
- replayable examples,
- deterministic expected outcomes,
- failure classes that can be compared over time,
- evidence suitable for grant review and research reports.

### 2. LTP + CML reference library

A minimal reference implementation for:

- trace event representation,
- causal memory records,
- decision lineage,
- deterministic replay hooks,
- integrity/digest metadata,
- failure localization.

### 3. Evaluation report

A report comparing:

- behavior-only evaluation,
- unstructured logging,
- trace-based oversight,
- causal-memory-based oversight.

The central research question:

> Can deterministic trace and causal-memory methods expose failure modes that behavior-only evaluation misses?

## How this supports PythiaLabs

The research track strengthens PythiaLabs by giving it:

- stronger theory of failure localization,
- reusable trace/evidence formats,
- benchmark credibility,
- grant-facing language,
- deeper technical moat,
- a path from paid reviews to rigorous evaluation infrastructure.

But PythiaLabs should keep the public conversion path simple:

```text
Run the demo.
Inspect the evidence.
Request a paid review.
```

## Recommended landing-page treatment

Do not place the Manifund proposal in the hero.

Add a small related-research block below `#demo-proof` or near `#support`:

```text
Related research track

PythiaLabs is the runnable pre-execution gate: it evaluates risky AI-agent actions before tools run.

It is connected to a broader research roadmap on deterministic oversight for agent traces: LTP + CML.

The product surface is simple:
proposed action → evidence → ALLOW / BLOCK / ESCALATE.

The research question is deeper:
where did the failure enter the agent’s decision trace?
```

Recommended CTA order:

1. Run PythiaLabs demo
2. Request paid review
3. Read research proposal

## Non-goals

For the PythiaLabs landing page, avoid:

- making Manifund the primary CTA,
- adding long protocol explanations above the paid-review offer,
- presenting LTP/CML as required to understand the PythiaLabs demo,
- turning the landing page into a grant proposal page.

For now, PythiaLabs should not become a general research portal.

## Final framing

PythiaLabs is the doorway.

LTP + CML are the deeper research foundation.

The doorway must stay clear enough for a CTO, security reviewer, or design partner to act.

The foundation must stay rigorous enough for researchers and grantmakers to trust.
