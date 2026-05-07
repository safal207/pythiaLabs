# Agent Action Audit Kit

Status: sales-facing pilot wedge.

Scope: this document describes a narrow, sellable entry point for the Liminal Evidence Stack: auditing one AI-agent workflow, action class, incident class, or CI/autofix path and producing a reviewer-ready evidence report.

## One-sentence offer

Agent Action Audit Kit helps teams prove why an AI agent acted, whether the action was allowed, what happened after, and whether the action was causally valid.

## The customer pain

AI agents are starting to perform consequential work:

- editing code,
- changing CI/CD configuration,
- opening pull requests,
- calling internal tools,
- touching infrastructure,
- triaging incidents,
- recommending remediations,
- interacting with customer or financial workflows.

But most teams cannot easily answer:

```text
What exactly did the agent decide?
Why was it allowed?
Which evidence supported it?
What changed after the action?
Can we replay the path?
Was the action causally authorized?
```

A final successful output is not enough.

```text
Functional correctness is not enough.
Agentic systems need causal accountability.
```

## Product wedge

The first product is not the whole Liminal Stack.

The first product is a bounded audit engagement:

```text
One workflow.
One action class.
One trace/log sample.
One evidence report.
```

Examples:

- coding agent PR/autofix audit,
- CI remediation audit,
- incident-response agent audit,
- workflow automation audit,
- high-risk tool-call audit,
- agent memory/action-boundary audit.

## What the kit does

Agent Action Audit Kit takes an existing agent workflow and turns it into an evidence chain:

```text
signal / proposed action
  -> care-case or gate decision
  -> decision record
  -> consequence memory
  -> pre-action gate
  -> side-effect lifecycle
  -> execution trace
  -> causal audit
  -> reviewer report
```

The output is not just a dashboard or narrative.

The output is a structured evidence report showing:

- what action was proposed,
- what policy/gate applied,
- what decision was made,
- what evidence supported that decision,
- whether the action was reversible,
- whether the action reached side effects,
- whether the trace is replayable,
- whether authorization/causal lineage is valid,
- what gaps or missing parents were detected,
- what the team should harden next.

## Core chain

```text
Signal
→ Guardian Layer
→ Care-Case
→ DRP
→ DMP
→ PythiaLabs
→ CaPU
→ T-Trace / LTP
→ CML
→ TTM DB / LiminalDB
→ Reviewer / Operator
```

## Layer roles

| Layer | Customer question | Output |
| --- | --- | --- |
| Signal | What happened or what action was proposed? | input event / workflow sample |
| Guardian Layer | Should this become a care-case instead of immediate action? | gate, explanation, recommended action |
| DRP | What decision was made and why? | decision record |
| DMP | What happened after the decision? | consequence / reversibility memory |
| PythiaLabs | Should the proposed action proceed before tool call? | allow / block / escalate evidence gate |
| CaPU | May this proceed to side effects? | gate/incubate/commit/execute lifecycle |
| T-Trace / LTP | Can we replay and inspect the execution path? | trace / replay / admissibility result |
| CML | Was the action causally valid? | causal audit finding |
| TTM DB / LiminalDB | Where does evidence live? | trace/evidence substrate and projections |
| Reviewer / Operator | Can a human inspect the chain? | final report |

## Pilot package

A practical paid pilot can be scoped as:

```text
Duration: 1-2 weeks
Input: one agent workflow or trace/log bundle
Output: one evidence report + hardening recommendations
```

### Included

- intake call / workflow scoping,
- trace/log review,
- action-boundary classification,
- evidence-chain mapping,
- causal-validity analysis,
- missing-authorization / missing-parent findings,
- reversibility risk review,
- reviewer-ready report,
- recommended next controls.

### Not included in first pilot

- production deployment,
- full continuous monitoring,
- replacing the customer's observability system,
- replacing security/compliance review,
- autonomous remediation,
- full incident response ownership.

The point is to start with a low-friction audit, not a platform migration.

## Buyer personas

Best early buyers:

- AI safety teams evaluating agentic workflows,
- enterprise AI governance teams,
- platform engineering teams using coding agents,
- QA/reliability teams testing CI/autofix agents,
- infra teams exploring agentic incident response,
- regulated teams that need reviewable AI-agent evidence.

## Sales message

Use this as the plain-English pitch:

```text
Your AI agent may produce the right output.
But can you prove it was allowed to do what it did?
```

Use this as the technical pitch:

```text
We build the evidence layer for agentic AI: decision records, trace replay, causal audit, and side-effect accountability for high-risk agent actions.
```

Use this as the enterprise pitch:

```text
We help teams turn opaque agent behavior into reviewer-ready evidence chains so they can audit decisions, replay traces, and detect causally invalid actions before agentic workflows scale.
```

## Deliverable: reviewer-ready report

The pilot report should include:

1. **Executive summary**
   - workflow audited,
   - main risks found,
   - top recommendations.

2. **Agent action map**
   - proposed actions,
   - tool calls,
   - side effects,
   - human review points.

3. **Evidence chain**
   - decision record,
   - gate decision,
   - trace records,
   - causal audit findings.

4. **Failure classes**
   - missing parent,
   - missing authorization,
   - unmarked handoff,
   - irreversible action without commit,
   - unsupported claim/action,
   - replay gap.

5. **Hardening recommendations**
   - add pre-action gate,
   - add decision record,
   - add trace anchors,
   - add causal validation,
   - add consequence memory,
   - require human review for red/yellow gates.

6. **Next-step pilot plan**
   - what to automate next,
   - what to monitor,
   - what to measure.

## Example use case: coding agent CI autofix

A coding agent sees a failed CI run and proposes a fix.

Questions:

- Was the failure root cause actually identified?
- Did the agent modify only allowed files?
- Was the decision to edit CI config authorized?
- Was the change reversible?
- Did the agent skip human review?
- Can the path be replayed?
- Was the action causally valid or only functionally successful?

Audit output:

```text
Action: modify CI config
Gate: escalate
Decision record: present / missing
Trace replay: partial / complete
Causal lineage: valid / invalid
Risk: irreversible automation drift
Recommendation: require DRP record + PythiaLabs gate + CaPU commit-before-effect for CI config changes
```

## Pricing hypothesis

Early pricing should be simple:

| Offer | Scope | Price hypothesis |
| --- | --- | --- |
| Starter audit | one workflow, lightweight report | $1k-$3k |
| Deep audit | one workflow + trace review + recommendations | $5k-$10k |
| Design partner | 4-8 weeks, integration prototype | $15k-$50k |
| Enterprise | continuous evidence monitoring | custom |

For grants and research, the same artifact becomes:

```text
deterministic oversight benchmark + reproducible evidence report
```

For commercial teams, it becomes:

```text
AI-agent audit and governance readiness report
```

## Why this can sell

The commercial insight:

```text
Teams do not first buy a new protocol stack.
They buy confidence that their agent workflow will not create unreviewable risk.
```

Agent Action Audit Kit sells that confidence through evidence.

## Non-claims

This offer does not claim:

- complete AI alignment,
- production-grade enforcement on day one,
- replacement of human review,
- replacement of customer observability,
- replacement of security/compliance programs,
- prevention of all unsafe actions,
- universal correctness of agent decisions.

The narrower claim is stronger:

```text
We can help inspect one agent workflow and convert opaque behavior into a structured evidence chain with concrete findings and next controls.
```

## Short version

```text
From signal
to decision
to consequence
to gated action
to controlled execution
to replayable evidence
to causal audit.
```

## Best landing-page headline

```text
Audit the actions your AI agents take — not just the answers they give.
```

## Best CTA

```text
Send us one agent workflow or trace sample. We will turn it into an evidence chain and show where trust breaks.
```
