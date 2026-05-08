# Agent Action Audit Snapshot

Status: commercial OTO / paid entry offer.

Scope: use this as a small paid first step before a full Agent Action Audit Kit pilot.

## Positioning

```text
Before you scale an AI agent, find the first place where trust breaks.
```

Agent Action Audit Snapshot is a lightweight first audit for one AI-agent workflow.

It is designed for teams that are interested in agent safety, but are not ready to commit to a full pilot yet.

## Core offer

```text
Send one AI-agent workflow.
Get a concise evidence-risk snapshot.
```

## Founding offer

```text
Agent Action Audit Snapshot — $197
```

Founding-price language:

```text
Founding Snapshot price: $197 for the first limited engagements.
After the workflow is validated, this may move to $497+.
```

## Who it is for

Best fit:

- teams using coding agents,
- CI/CD autofix agents,
- incident-response agents,
- internal tool-calling agents,
- AI governance reviewers,
- platform teams testing agentic workflows,
- security teams evaluating agent actions before tools run.

Not a fit if:

- the team has no concrete agent workflow,
- the agent only chats and cannot call tools,
- the customer wants a full platform deployment immediately,
- the customer wants legal, compliance, or production sign-off.

## What the customer sends

Ask for one bounded workflow only:

- one workflow description,
- one action class,
- one redacted trace/log/sample description,
- current approval or permission rule,
- what the agent is allowed to do today,
- what the customer worries could go wrong.

Safety note:

```text
Please do not include credentials, secrets, customer data, regulated data, private production logs, or proprietary traces unless explicitly authorized under agreement.
```

## What the customer receives

The Snapshot returns a concise report with:

- workflow summary,
- action-risk map,
- ALLOW / BLOCK / ESCALATE recommendation,
- missing evidence list,
- causal-validity gaps,
- top 3 controls to add before scaling,
- recommended next step: no action, hardening, or full pilot.

## Output shape

Recommended length:

```text
2–3 pages
```

Recommended sections:

1. Executive verdict
2. Workflow map
3. Action boundary
4. Evidence available before action
5. Missing evidence
6. ALLOW / BLOCK / ESCALATE recommendation
7. Causal-validity gaps
8. Top 3 controls
9. Next step

## Snapshot verdicts

| Verdict | Meaning | Recommended next step |
| --- | --- | --- |
| GREEN | Workflow is low-risk in the reviewed scope. | Continue with lightweight monitoring. |
| YELLOW | Workflow can continue only with added controls. | Add controls before scaling. |
| RED | Workflow should not run in current form. | Block, redesign, or require human approval. |

## Example Snapshot conclusion

```text
Snapshot verdict: YELLOW.

The workflow has a useful human review point before merge, but the agent can still create a pull request that modifies CI configuration without a structured decision record or pre-action evidence gate.

Top trust break:
The action may be functionally correct, but it is not yet causally accountable.

Recommended next control:
Classify CI configuration changes as ESCALATE and require a decision record plus pre-action gate before PR creation.
```

## Sales copy

Short version:

```text
For $197, we audit one AI-agent workflow and show the first place where trust breaks.
```

Landing version:

```text
Not ready for a full pilot?
Start with a $197 Agent Action Audit Snapshot.

Send one workflow, one action class, and one redacted evidence sample.
Get a concise report showing whether the action should be allowed, blocked, or escalated — and what evidence is missing before you scale.
```

Button text:

```text
Get a $197 Agent Action Audit Snapshot
```

Microcopy:

```text
A lightweight first audit for one AI-agent workflow — before committing to a full pilot.
```

## Email CTA

Subject:

```text
Agent Action Audit Snapshot inquiry
```

Body template:

```text
Hi Aleksei,

I am interested in the Agent Action Audit Snapshot.

Workflow / agent system:
Action class:
What can the agent execute today?
What logs/traces can we share safely?
What are we worried could go wrong?
Current stage: prototype / pilot / production / exploring

We will not include secrets, credentials, customer data, or sensitive production details.
```

## Relationship to Agent Action Audit Kit

The Snapshot is the entry offer.

The full Agent Action Audit Kit is the deeper pilot.

```text
One-pager interest
→ Snapshot OTO
→ Full audit pilot
→ Design partner / integration
```

## Upgrade path

After Snapshot, offer one of three next steps:

1. No pilot needed — low risk in reviewed scope.
2. Hardening recommendations only — add controls internally.
3. Full Agent Action Audit Kit pilot — produce a reviewer-ready evidence report.

## Boundaries

This Snapshot does not provide:

- legal advice,
- compliance certification,
- production sign-off,
- security penetration testing,
- full model evaluation,
- continuous monitoring,
- autonomous remediation.

It provides:

```text
A focused evidence-risk snapshot for one AI-agent workflow.
```

## Final short version

```text
Before a full pilot, buy one small truth:
where does trust break in this workflow?
```
