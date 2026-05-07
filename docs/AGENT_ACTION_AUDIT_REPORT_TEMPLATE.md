# Agent Action Audit Report Template

Status: customer-facing pilot deliverable template.

Scope: use this template to produce a compact evidence report for one AI-agent workflow, action class, trace/log sample, or pilot engagement.

## Report title

```text
Agent Action Audit Report: <workflow / action class>
```

## Confidentiality note

```text
This report should not contain secrets, credentials, private customer data, regulated data, or sensitive production details unless explicitly approved by the customer and handled under the appropriate agreement.
```

## One-sentence purpose

```text
This report evaluates whether one AI-agent workflow is allowed, evidenced, replayable, reversible, and causally valid enough to scale safely.
```

## Executive summary

| Field | Value |
| --- | --- |
| Customer / team | `<name>` |
| Workflow audited | `<workflow>` |
| Action class | `<PR autofix / CI remediation / incident response / tool call / governance action / other>` |
| Date | `<YYYY-MM-DD>` |
| Auditor | `Aleksei Safonov / PythiaLabs` |
| Input artifacts | `<workflow description / logs / traces / synthetic scenario / screenshots / docs>` |
| Overall verdict | `<GREEN / YELLOW / RED>` |
| Primary risk | `<short risk>` |
| Recommended next control | `<short recommendation>` |

### Summary paragraph

```text
We reviewed <workflow> where an AI agent can <action>. The audit found that <main strength>, but <main gap>. The workflow is currently <verdict> because <reason>. Before scaling, the team should <top recommendation>.
```

## Verdict scale

| Verdict | Meaning | Recommended response |
| --- | --- | --- |
| GREEN | Action path is sufficiently evidenced and bounded for the reviewed scope. | Continue with monitoring and periodic review. |
| YELLOW | Workflow may continue only with additional controls, review, or limited blast radius. | Add controls before scale-up. |
| RED | Workflow should not proceed in current form. | Block, redesign, or require human approval. |

## Audit scope

### In scope

- `<workflow or action class>`
- `<agent role>`
- `<tool/action boundary>`
- `<provided logs/traces/docs>`
- `<specific decision or incident class>`

### Out of scope

- Full platform security review.
- Full compliance review.
- Penetration testing.
- Production deployment sign-off.
- Model capability evaluation beyond the provided workflow.
- Verification of artifacts not supplied by the customer.
- Sensitive production systems not explicitly included.

## Input artifacts reviewed

| Artifact | Description | Sensitivity | Notes |
| --- | --- | --- | --- |
| `<artifact 1>` | `<description>` | `<public / internal / anonymized / synthetic>` | `<notes>` |
| `<artifact 2>` | `<description>` | `<public / internal / anonymized / synthetic>` | `<notes>` |

## Workflow overview

```text
Trigger
→ agent observes state
→ agent proposes action
→ evidence is checked
→ decision/gate is applied
→ action may reach tool call
→ side effect may occur
→ result is logged / traced
→ reviewer inspects outcome
```

### Workflow narrative

```text
The agent receives <trigger>. It then proposes <action>. The action may affect <system/state/customer/infra/code>. Current controls include <controls>. Current gaps include <gaps>.
```

## Agent action map

| Step | Actor | Action | External state change? | Evidence available? | Human review? | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `<agent/system/human>` | `<action>` | `<yes/no>` | `<yes/no/partial>` | `<yes/no>` | `<notes>` |
| 2 | `<agent/system/human>` | `<action>` | `<yes/no>` | `<yes/no/partial>` | `<yes/no>` | `<notes>` |

## Action boundary classification

| Boundary | Status | Notes |
| --- | --- | --- |
| Read-only observation | `<present / absent / unclear>` | `<notes>` |
| Recommendation only | `<present / absent / unclear>` | `<notes>` |
| Tool call | `<present / absent / unclear>` | `<notes>` |
| External side effect | `<present / absent / unclear>` | `<notes>` |
| Irreversible / hard-to-reverse change | `<present / absent / unclear>` | `<notes>` |
| Human approval boundary | `<present / absent / unclear>` | `<notes>` |

## Evidence chain

Use this chain as the core audit model.

```text
Signal
→ Care-Case / policy gate
→ Decision record
→ Consequence memory
→ Pre-action gate
→ Side-effect lifecycle
→ Execution trace
→ Causal audit
→ Reviewer report
```

| Layer | Audit question | Evidence found | Status | Gap |
| --- | --- | --- | --- | --- |
| Signal | What happened or what was proposed? | `<evidence>` | `<PASS / PARTIAL / FAIL / N/A>` | `<gap>` |
| Guardian Layer / Care-Case | Was the signal converted into a reviewable case? | `<evidence>` | `<PASS / PARTIAL / FAIL / N/A>` | `<gap>` |
| DRP / Decision record | What decision was made and why? | `<evidence>` | `<PASS / PARTIAL / FAIL / N/A>` | `<gap>` |
| DMP / Consequence memory | What happened after the decision? | `<evidence>` | `<PASS / PARTIAL / FAIL / N/A>` | `<gap>` |
| PythiaLabs / Pre-action gate | Was the action gated before execution? | `<evidence>` | `<PASS / PARTIAL / FAIL / N/A>` | `<gap>` |
| CaPU / Side-effect lifecycle | Was commit-before-effect enforced? | `<evidence>` | `<PASS / PARTIAL / FAIL / N/A>` | `<gap>` |
| T-Trace / LTP | Can the path be replayed or inspected? | `<evidence>` | `<PASS / PARTIAL / FAIL / N/A>` | `<gap>` |
| CML | Is causal/authorization lineage valid? | `<evidence>` | `<PASS / PARTIAL / FAIL / N/A>` | `<gap>` |
| Reviewer / Operator | Can a human understand the chain? | `<evidence>` | `<PASS / PARTIAL / FAIL / N/A>` | `<gap>` |

## Decision-time evidence

Key question:

```text
What evidence existed before the agent acted — not after the fact?
```

| Evidence item | Available before action? | Fresh? | Verifiable? | Used in decision? | Notes |
| --- | --- | --- | --- | --- | --- |
| `<item>` | `<yes/no/unclear>` | `<yes/no/unclear>` | `<yes/no/unclear>` | `<yes/no/unclear>` | `<notes>` |

## ALLOW / BLOCK / ESCALATE criteria

| Decision | Criteria | Evidence required |
| --- | --- | --- |
| ALLOW | Action is low-risk, authorized, reversible, evidenced, and within declared boundary. | `<list>` |
| BLOCK | Action is unauthorized, high-risk without evidence, irreversible without approval, or outside scope. | `<list>` |
| ESCALATE | Action is ambiguous, high-impact, partially evidenced, or requires human judgment. | `<list>` |

### Recommended decision for reviewed workflow

```text
Recommended gate: <ALLOW / BLOCK / ESCALATE>
Reason: <reason>
Required next evidence/control: <control>
```

## Causal validity review

Key question:

```text
Was the action not only functionally successful, but causally authorized?
```

| Check | Result | Notes |
| --- | --- | --- |
| Parent decision exists | `<PASS / PARTIAL / FAIL>` | `<notes>` |
| Authorization exists | `<PASS / PARTIAL / FAIL>` | `<notes>` |
| Evidence supports action | `<PASS / PARTIAL / FAIL>` | `<notes>` |
| Handoff is marked | `<PASS / PARTIAL / FAIL>` | `<notes>` |
| Side-effect boundary is explicit | `<PASS / PARTIAL / FAIL>` | `<notes>` |
| Replay path is complete | `<PASS / PARTIAL / FAIL>` | `<notes>` |
| Reversibility is known | `<PASS / PARTIAL / FAIL>` | `<notes>` |

## Failure classes

Use these labels consistently across reports.

| Code | Failure class | Description | Severity default |
| --- | --- | --- | --- |
| AAA-R1 | Missing authorization | Action lacks explicit authorization or approval boundary. | High |
| AAA-R2 | Missing parent | Action references no valid prior decision, trigger, or cause. | High |
| AAA-R3 | Replay gap | Trace/logs cannot reconstruct the action path. | Medium |
| AAA-R4 | Stale evidence | Decision used evidence that was outdated or unverifiable at action time. | Medium |
| AAA-R5 | Unmarked side effect | Workflow crosses from recommendation to external state change without explicit boundary. | High |
| AAA-R6 | Irreversible before commit | Irreversible or hard-to-reverse action occurs before commit/approval. | High |
| AAA-R7 | Unsupported claim/action | Agent asserts or acts without evidence anchor. | Medium |
| AAA-R8 | Human-review bypass | Workflow bypasses expected human review or escalation. | High |
| AAA-R9 | Ambiguous responsibility | It is unclear whether the agent, system, or human owns the decision. | Medium |
| AAA-R10 | Consequence memory missing | Outcome after the decision is not tracked. | Medium |

## Findings

### Finding 1 — `<title>`

| Field | Value |
| --- | --- |
| Code | `<AAA-R#>` |
| Severity | `<Low / Medium / High / Critical>` |
| Evidence | `<artifact / trace / log / statement>` |
| Affected step | `<workflow step>` |
| Status | `<open / mitigated / accepted risk>` |

**Description**

```text
<What was found.>
```

**Why it matters**

```text
<Why this creates risk for agentic accountability, replayability, authorization, or side effects.>
```

**Recommended control**

```text
<Concrete next control.>
```

### Finding 2 — `<title>`

| Field | Value |
| --- | --- |
| Code | `<AAA-R#>` |
| Severity | `<Low / Medium / High / Critical>` |
| Evidence | `<artifact / trace / log / statement>` |
| Affected step | `<workflow step>` |
| Status | `<open / mitigated / accepted risk>` |

**Description**

```text
<What was found.>
```

**Why it matters**

```text
<Why this creates risk.>
```

**Recommended control**

```text
<Concrete next control.>
```

## Severity model

| Severity | Meaning | Recommended response |
| --- | --- | --- |
| Critical | Current workflow can create high-impact side effects without authorization, replay, or review. | Block until redesigned. |
| High | Workflow has serious gaps around authorization, side effects, or causal lineage. | Require controls before scale-up. |
| Medium | Workflow has incomplete evidence, replay, or consequence tracking. | Fix before broad deployment. |
| Low | Minor documentation or observability gap. | Track and improve. |

## Control recommendations

| Priority | Control | Owner | Effort | Risk reduced |
| --- | --- | --- | --- | --- |
| P0 | `<control>` | `<team/person>` | `<S/M/L>` | `<risk>` |
| P1 | `<control>` | `<team/person>` | `<S/M/L>` | `<risk>` |
| P2 | `<control>` | `<team/person>` | `<S/M/L>` | `<risk>` |

Recommended control library:

- Add pre-action gate for high-risk tool calls.
- Add explicit decision record before action.
- Add evidence freshness check.
- Add trace anchors for key claims/actions.
- Add human review for yellow/red gates.
- Add commit-before-effect lifecycle.
- Add consequence memory after execution.
- Add causal lineage audit for side-effect actions.
- Add replayable trace export.
- Add responsibility owner for each action class.

## Minimum viable hardening plan

```text
Week 1:
- identify high-risk action class
- define ALLOW / BLOCK / ESCALATE rules
- require decision record for that action class

Week 2:
- add trace anchors / replay path
- add side-effect boundary
- add human review for yellow/red cases

Week 3+:
- add causal audit checks
- add consequence memory
- prepare continuous monitoring or integration pilot
```

## Reviewer checklist

A reviewer should be able to answer:

```text
1. What action did the agent propose?
2. What evidence existed before action?
3. Was the action allowed?
4. Who or what authorized it?
5. Was the action reversible?
6. Did the workflow cross a side-effect boundary?
7. Can the path be replayed?
8. Is the causal lineage valid?
9. What happened after execution?
10. What control should be added next?
```

## Customer-safe sharing guidance

Ask customers to share only non-sensitive materials:

- anonymized workflow description,
- synthetic trace/log sample,
- redacted policy or approval rule,
- generic action class,
- non-production scenario,
- summary of current controls.

Do not request or store:

- credentials,
- secrets,
- customer data,
- regulated data,
- raw production incidents without approval,
- private prompts or proprietary traces unless explicitly authorized.

## Final report conclusion

Use a concise close:

```text
The reviewed workflow is currently <GREEN/YELLOW/RED>.

The strongest existing control is <control>.
The largest trust gap is <gap>.

Before scaling this workflow, the team should <top recommendation>.
```

## Appendix A — Evidence chain diagram

```text
Signal
  ↓
Care-Case / Policy Gate
  ↓
Decision Record
  ↓
Consequence Memory
  ↓
Pre-Action Gate
  ↓
Commit-Before-Effect
  ↓
Execution Trace
  ↓
Causal Audit
  ↓
Reviewer Report
```

## Appendix B — One-page version

```text
Workflow: <workflow>
Action class: <action class>
Verdict: <GREEN/YELLOW/RED>
Primary risk: <risk>
Top recommendation: <recommendation>

Evidence chain status:
- Signal: <PASS/PARTIAL/FAIL>
- Decision record: <PASS/PARTIAL/FAIL>
- Pre-action gate: <PASS/PARTIAL/FAIL>
- Side-effect boundary: <PASS/PARTIAL/FAIL>
- Trace replay: <PASS/PARTIAL/FAIL>
- Causal lineage: <PASS/PARTIAL/FAIL>
- Consequence memory: <PASS/PARTIAL/FAIL>

Top findings:
1. <finding>
2. <finding>
3. <finding>

Next controls:
1. <control>
2. <control>
3. <control>
```

## Final short version

```text
We do not audit whether the answer looked good.
We audit whether the action was allowed, evidenced, replayable, reversible, and causally valid.
```
