# OTF Reviewer Path: pythiaLabs-IF

This page is for reviewers of the submitted Open Technology Fund application:

```text
pythiaLabs-IF: Reproducible Evidence Gates for Internet Freedom Tooling (#22032)
```

## One-sentence summary

pythiaLabs-IF is an open-source evidence-gate layer for reviewing high-risk AI/agent actions before they affect internet-freedom tooling, infrastructure, workflows, or governance processes.

## Why this may matter for internet freedom tooling

Internet-freedom projects increasingly rely on automation, AI-assisted analysis, infrastructure tooling, moderation support, security workflows, and semi-autonomous agents.

Those systems may propose actions such as:

- modifying infrastructure or deployment configuration;
- changing access, routing, or operational policy;
- escalating or suppressing a workflow item;
- generating evidence summaries for sensitive decisions;
- preparing governance or treasury actions;
- handling security-sensitive artifacts or operator instructions.

The risk is not only that an action fails technically. The risk is that a high-impact action executes without enough evidence, authorization, context, freshness, or recovery assumptions.

pythiaLabs-IF explores a reusable open-source building block for asking:

```text
Should this proposed AI/agent action be allowed now,
blocked now,
or escalated to a human/operator before execution?
```

## Core idea

The core artifact is a deterministic evidence gate.

Instead of trusting only prompts, credentials, or successful tool calls, pythiaLabs evaluates a proposed action against structured evidence:

```text
proposed action
+ authorization chain
+ evidence freshness
+ environment context
+ credential/scope assumptions
+ recovery assumptions
+ risk level
-> ALLOW / BLOCK / ESCALATE
```

The expected output is not a vague recommendation. It is a reviewer-visible decision with stable stop reasons and replayable evidence artifacts.

## Internet-freedom fit

pythiaLabs-IF is relevant when internet-freedom tooling needs actions to be reviewable before they become irreversible or operationally sensitive.

Possible fit areas:

| Area | Example risk | Evidence-gate role |
| --- | --- | --- |
| Infrastructure operations | Agent proposes deployment or routing change without enough context. | Block or escalate until evidence and authorization are sufficient. |
| Security workflows | Agent handles sensitive artifacts and proposes follow-up actions. | Require scoped evidence and recovery assumptions before action. |
| Governance workflows | Agent prepares an action that affects funds, access, moderation, or policy. | Check authorization lineage and produce audit artifacts. |
| Research / OSINT support | Agent summarizes or links evidence for sensitive decisions. | Require grounded evidence and reject unsupported claims. |
| Civil-society tooling | Small teams need lightweight review gates without proprietary infrastructure. | Provide libre, inspectable, forkable decision artifacts. |

## What exists today

This repository is an open-source MVP with deterministic local demos and reviewer-facing documentation.

Useful entry points:

- One-page summary: [`PYTHIALABS_ONE_PAGE_SUMMARY.md`](PYTHIALABS_ONE_PAGE_SUMMARY.md)
- Documentation index: [`README.md`](README.md)
- ProofPath continuation for reviewers: [`PROOFPATH_CONTINUATION_FOR_REVIEWERS.md`](PROOFPATH_CONTINUATION_FOR_REVIEWERS.md)
- Related LS grant path: [`RELATED_LS_GRANT_PATH.md`](RELATED_LS_GRANT_PATH.md)
- Agent infrastructure action showcase: [`agent_infra_action_showcase_expected_output.md`](agent_infra_action_showcase_expected_output.md)
- Banking AI risk showcase: [`banking_ai_risk_showcase_expected_output.md`](banking_ai_risk_showcase_expected_output.md)
- Web3 treasury governance showcase: [`web3_treasury_full_showcase_expected_output.md`](web3_treasury_full_showcase_expected_output.md)

The current demos are not internet-freedom deployments. They are controlled examples showing the same class of safety problem:

```text
high-risk proposed action
-> insufficient or sufficient evidence
-> deterministic ALLOW / BLOCK / ESCALATE decision
-> replayable review artifact
```

## Current executable continuation

The most current executable evidence continuation for this research direction is ProofPath / Compute Witness.

Read:

- ProofPath: https://github.com/safal207/ProofPath
- ProofPath ecosystem graph: https://github.com/safal207/ProofPath/blob/main/docs/ECOSYSTEM_GRAPH.md
- Submitted application reviewer bridge: https://github.com/safal207/ProofPath/blob/main/docs/SUBMITTED_APPLICATION_REVIEWER_BRIDGE.md
- Compute Witness grant reviewer path: https://github.com/safal207/ProofPath/blob/main/docs/COMPUTE_WITNESS_GRANT_REVIEWER_PATH.md

Relationship:

```text
pythiaLabs-IF
  -> internet-freedom / evidence-gate application framing

ProofPath
  -> executable pre-action boundary and verifier layer

Compute Witness
  -> reviewable evidence for AI/agent compute results

LS / Liminal Stack
  -> broader governance and reviewer packet

CML
  -> causal-validity and why-allowed layer

LTP
  -> trace/replay/continuity layer
```

## What an OTF reviewer can inspect in 5 minutes

1. Read this file.
2. Open [`PYTHIALABS_ONE_PAGE_SUMMARY.md`](PYTHIALABS_ONE_PAGE_SUMMARY.md).
3. Open [`PROOFPATH_CONTINUATION_FOR_REVIEWERS.md`](PROOFPATH_CONTINUATION_FOR_REVIEWERS.md).
4. Open the ProofPath ecosystem graph.
5. Inspect the Compute Witness reviewer path if runnable evidence is the priority.

Fast interpretation:

```text
PythiaLabs explains the evidence-gate problem.
ProofPath / Compute Witness shows the current executable evidence path.
CML and LTP explain causal validity and trace/replay support.
LS provides the broad grant reviewer packet.
```

## Non-claims

This page does not claim that pythiaLabs-IF is production-deployed in internet-freedom tooling.

It also does not claim:

- certified regulatory compliance;
- legal advice;
- production enforcement readiness;
- complete security protection;
- censorship-resistance guarantees;
- model truthfulness;
- universal agent alignment;
- trusted execution environment attestation;
- zkML correctness;
- production key management.

The narrower claim is:

```text
The repository contains public, inspectable artifacts for deterministic evidence gates around high-risk AI/agent actions, with a connected executable continuation path through ProofPath / Compute Witness.
```

## Funding interpretation

OTF support would help turn the current MVP and related executable evidence path into a more focused internet-freedom tooling artifact.

A practical hardening path would include:

```text
internet-freedom threat model
-> evidence schema refinement
-> CLI / workflow prototype
-> OTF-relevant demo cases
-> reviewer report
-> documentation for small teams and civil-society maintainers
```

The value is not a single dashboard. The value is a small, reusable, libre evidence-gate primitive that internet-freedom projects can inspect, fork, and adapt before high-risk AI/agent actions execute.
