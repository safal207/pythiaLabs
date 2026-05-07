# Agent Action Audit Kit — Outreach Pack

Status: sales-facing outreach asset.

Scope: this document provides short outbound messages, qualification questions, discovery-call structure, and first-pilot positioning for Agent Action Audit Kit.

## Core offer

```text
Audit the actions your AI agents take — not just the answers they give.
```

## Core question

```text
Your AI agent may produce the right output.
But can you prove it was allowed to do what it did?
```

## Best use case

Use this outreach when talking to teams that already have or are actively building agents that can:

- edit code,
- open or modify pull requests,
- change CI/CD configuration,
- call internal tools,
- touch infrastructure,
- triage incidents,
- recommend or perform remediation,
- interact with finance, customer, or governance workflows.

## Positioning

Do not sell the whole Liminal Stack first.

Sell a narrow audit:

```text
One workflow.
One action class.
One trace/log sample.
One evidence report.
```

The customer is not buying protocols.

They are buying confidence that an agent workflow will not create unreviewable risk.

## One-line pitch

```text
We help teams turn opaque AI-agent behavior into reviewer-ready evidence chains: decision, gate, consequence, trace replay, and causal audit.
```

## Short DM

```text
Hi <Name> — quick question.

Are you using AI agents that can touch code, CI/CD, infra, internal tools, or customer workflows?

I’m building Agent Action Audit Kit: a narrow audit for one agent workflow.

The output is a reviewer-ready evidence chain showing what the agent did, why it was allowed, what evidence supported it, what happened after, and whether the action was causally valid.

Core question:
Your agent may produce the right output — but can you prove it was allowed to do what it did?

Open to a quick look at one workflow?
```

## Founder-style X / LinkedIn post

```text
AI agents are moving from answering questions to taking actions.

That changes the safety question.

Not only:
“Did the agent produce the right answer?”

But:
“Can we prove the agent was allowed to do what it did?”

I’m packaging a narrow pilot:
Agent Action Audit Kit.

One workflow.
One action class.
One trace/log sample.
One evidence report.

The goal: turn opaque agent behavior into a reviewer-ready evidence chain:
decision → gate → consequence → execution → replay → causal audit.

Functional correctness is not enough.
Agentic systems need causal accountability.
```

## Cold email — short version

Subject options:

```text
Agent action audit for one workflow?
Can you prove your AI agent was allowed to act?
Audit the actions your AI agents take
```

Email:

```text
Hi <Name>,

I’m reaching out because your team appears to be working with AI agents / automation that may touch code, CI/CD, infrastructure, internal tools, or operational workflows.

I’m building Agent Action Audit Kit — a narrow pilot for auditing one AI-agent workflow.

The core question is simple:

Your AI agent may produce the right output.
But can you prove it was allowed to do what it did?

The pilot takes one workflow or trace/log sample and turns it into a reviewer-ready evidence chain:

- what action was proposed,
- what decision/gate applied,
- what evidence supported it,
- whether the action was reversible,
- whether the path can be replayed,
- whether authorization / causal lineage is valid,
- what controls should be added next.

This is not a platform migration. It is a bounded audit of one workflow.

Would it be useful to look at one agent workflow your team is concerned about?

Best,
Aleksei Safonov
PythiaLabs
https://safal207.github.io/pythiaLabs/
```

## Cold email — enterprise version

```text
Hi <Name>,

AI agents are starting to perform consequential work: editing code, modifying CI/CD, calling internal tools, triaging incidents, and recommending remediations.

Most teams can inspect final outputs. Fewer teams can prove the full action chain:

- what the agent decided,
- why the action was allowed,
- what evidence supported the decision,
- what changed after execution,
- whether the trace is replayable,
- whether the action was causally authorized.

I’m building Agent Action Audit Kit, a narrow pilot that audits one AI-agent workflow and produces a reviewer-ready evidence report.

The goal is not to replace your observability, security, or compliance tooling. The goal is to map one high-risk workflow into an evidence chain and show where trust breaks.

Typical first workflow:

- coding-agent PR/autofix,
- CI remediation,
- incident-response agent,
- high-risk tool call,
- internal automation touching production-like systems.

Would you be open to sharing one non-sensitive workflow pattern for a short fit conversation?

Best,
Aleksei Safonov
PythiaLabs
https://safal207.github.io/pythiaLabs/
```

## Reply to “what exactly do you deliver?”

```text
The first deliverable is a compact evidence report for one workflow.

It usually includes:

1. Agent action map
   - proposed action,
   - tool calls,
   - side effects,
   - human review points.

2. Evidence chain
   - decision record,
   - gate criteria,
   - trace/replay assumptions,
   - causal-audit findings.

3. Failure classes
   - missing authorization,
   - missing parent / broken lineage,
   - irreversible action before commit,
   - replay gap,
   - unsupported claim or action.

4. Hardening recommendations
   - add pre-action gate,
   - add decision record,
   - add trace anchors,
   - add causal validation,
   - require human review for red/yellow gates.

The goal is to make one opaque agent workflow reviewable before scaling the system.
```

## Reply to “is this a product or consulting?”

```text
The first step is a bounded audit, not a platform sale.

I do not ask teams to migrate their stack.

We start with one workflow, one action class, and one trace/log sample. Then I produce a reviewer-ready evidence chain and recommendations for what controls should be added next.

If the workflow is high-value, that can later become integration work or continuous evidence monitoring.
```

## Reply to “how is this different from observability/logging?”

```text
Observability usually tells you what happened.

Agent Action Audit Kit asks additional questions:

- Was the action allowed?
- What decision authorized it?
- What evidence existed at decision time?
- Was the action reversible?
- Did the workflow cross a side-effect boundary?
- Can the path be replayed?
- Is the causal lineage valid?

Logs are useful.
But logs alone do not prove causal accountability.
```

## Reply to “why now?”

```text
Because agents are moving from text generation into tool use and side effects.

Once an agent can edit code, call internal APIs, modify infrastructure, or trigger workflow actions, final-output evaluation is not enough.

Teams need evidence around decisions, permissions, trace replay, reversibility, and causal authorization.
```

## Qualification questions

Use these in first conversations:

```text
1. What actions can the agent actually execute today?
2. Which of those actions could create operational, financial, security, compliance, or customer risk?
3. Is there a human approval step before execution?
4. What logs/traces exist today?
5. Can the same workflow be replayed or reconstructed?
6. How do you know an action was authorized?
7. What evidence exists at decision time, not after the fact?
8. Which actions should be ALLOW / BLOCK / ESCALATE?
9. What would make this workflow safe enough to scale?
10. What would a reviewer need to see to trust it?
```

## Discovery-call structure

A 30-minute call can use this structure:

```text
0-5 min: context
- what the agent does
- where it runs
- what tools it can call

5-12 min: action boundary
- which actions matter
- what can change external state
- where human review exists

12-20 min: evidence boundary
- what logs/traces exist
- what evidence exists before execution
- what cannot be reconstructed today

20-27 min: audit fit
- choose one workflow
- choose one action class
- choose one evidence report target

27-30 min: next step
- confirm input artifacts
- confirm non-sensitive scope
- confirm report format
```

## What to ask them to send

```text
Please send only non-sensitive materials.

Useful input:

- one workflow description,
- one anonymized trace/log sample,
- one example of an agent-proposed action,
- current approval/escalation rules,
- current logs or audit records,
- what the team wants to prove.

Do not send:

- credentials,
- secrets,
- customer data,
- production incident details that cannot be shared,
- regulated data,
- private model prompts if not approved for sharing.
```

## First-pilot scope

```text
Input:
one workflow or anonymized trace/log sample

Output:
one evidence report + hardening recommendations

Timeline:
1-2 weeks depending on material quality

Result:
a clear map of what can be trusted, what cannot be proven, and what control should be added next
```

## Simple pricing language

```text
For early pilots, I usually suggest starting with a bounded audit instead of a platform integration.

Starter audit: one workflow, lightweight report.
Deep audit: one workflow + trace review + recommendations.
Design partner: multiple weeks with integration notes and implementation guidance.

The exact scope depends on what artifacts you can safely share.
```

## Objection handling

### “We already have logs.”

```text
That is useful.

The audit starts from your existing logs. The question is whether they prove enough:

- authorization,
- decision-time evidence,
- replayability,
- reversibility,
- causal lineage.

Most logging systems were not designed for agentic accountability.
```

### “We are too early.”

```text
That may actually be the right time.

If the agent has not reached production yet, the audit can help define the action boundary before unsafe patterns harden into architecture.
```

### “We cannot share traces.”

```text
That is fine.

We can start with an anonymized workflow description or synthetic trace. The goal is not to extract sensitive data; it is to map the evidence requirements and trust gaps.
```

### “Is this security testing?”

```text
Adjacent, but not the same.

Security testing asks whether the system can be attacked.

Agent action audit asks whether a consequential agent action was authorized, evidenced, replayable, reversible, and causally valid.
```

## Best first targets

Prioritize teams with:

- coding agents in CI/CD,
- internal tools agents,
- infra/DevOps automation,
- incident response assistants,
- AI governance teams,
- regulated enterprise AI pilots,
- platform teams adding tool use to LLM workflows,
- safety teams evaluating agent behavior.

Avoid first:

- teams only using chatbots for Q&A,
- teams with no tool use,
- teams wanting generic prompt advice,
- teams seeking full production platform replacement immediately,
- teams asking to share sensitive data before scope is clear.

## Final short version

```text
We do not audit whether the answer looked good.
We audit whether the action was allowed, evidenced, replayable, reversible, and causally valid.
```
