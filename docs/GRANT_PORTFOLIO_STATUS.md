# Grant Portfolio Status

Last updated: 2026-06-03

## Purpose

This file is the mission-control view for the current NLnet grant portfolio.

It tracks application codes, funds, repositories, reviewer-readiness status, and the next action for each proposal.

## Current portfolio

| Priority | Code | Fund | Project | Status |
|---:|---|---|---|---|
| 1 | 2026-08-00b | NGI TALER | ProofPath Agent Payment Guard | Submitted |
| 2 | 2026-08-00c | NGI Fediversity | LiminalDB | Submitted; budget corrected |
| 3 | 2026-06-133 | NGI Commons | PythiaLabs | Acknowledged; primary version |
| 4 | 2026-06-0c5 | NGI Commons | LiminalQAengineer | Acknowledged |
| 5 | 2026-06-087 | NGI Commons | Liminal Stack | Acknowledged |
| 6 | 2026-06-0fe | NGI Commons | PythiaLabs | Acknowledged; duplicate/older variant |

## Reviewer-ready repositories

### ProofPath

```text
Application: 2026-08-00b
Fund: NGI TALER
Repository: https://github.com/safal207/ProofPath
Requested amount: EUR 50,000
```

Reviewer path:

- `docs/NGI_TALER_REVIEWER_PATH.md`
- `docs/TALER_ALIGNMENT.md`
- `docs/AGENT_PAYMENT_GUARD_DEMO.md`
- `docs/BUDGET_AND_MILESTONES.md`
- `docs/GRANT_MILESTONE_TRACKER.md`

Public milestone issues:

- `#159` — Signed intent envelope and threat model
- `#160` — Core payment guard engine
- `#161` — Evidence bundle and offline verifier
- `#162` — CLI API and integration notes
- `#163` — Documentation and community review

Current next action:

```text
Wait for NLnet review response.
If asked for clarification, answer from the TALER reviewer path and milestone tracker.
```

### LiminalDB

```text
Application: 2026-08-00c
Fund: NGI Fediversity
Repository: https://github.com/safal207/LiminalDB
Requested amount: EUR 50,000
```

Reviewer path:

- `docs/FEDIVERSITY_REVIEWER_PATH.md`
- `docs/FEDERATED_EVENT_SOURCING_ALIGNMENT.md`
- `docs/ACTIVITYPUB_MATRIX_INTEGRATION_PLAN.md`
- `docs/BUDGET_AND_MILESTONES_FEDIVERSITY.md`
- `docs/GRANT_MILESTONE_TRACKER_FEDIVERSITY.md`

Public milestone issues:

- `#75` — Event envelope and local replay model
- `#76` — Local-first persistence and audit path
- `#77` — Federated replication design
- `#78` — Protocol adapter notes
- `#79` — Developer and reviewer experience

Current next action:

```text
Wait for NLnet review response.
Keep README clean, keep open PR count at zero, and only add changes that improve reviewer clarity.
```

### PythiaLabs

```text
Application: 2026-06-133
Fund: NGI Zero Commons / Commons Fund
Repository: https://github.com/safal207/pythiaLabs
Requested amount: EUR 30,000
```

Reviewer path:

- `docs/NGI_COMMONS_REVIEWER_PATH.md`
- `docs/REVIEWER_PATH.md`
- `docs/PYTHIALABS_ONE_PAGE_SUMMARY.md`
- `docs/BUDGET_AND_MILESTONES_COMMONS.md`
- `docs/GRANT_MILESTONE_TRACKER_COMMONS.md`

Public milestone issues:

- `#190` — Evidence schema v0.1
- `#191` — CLI and library path
- `#192` — Demo case library
- `#193` — GitHub Actions prototype
- `#194` — Documentation and public reviewer report

Current next action:

```text
Wait for NLnet review response.
If PythiaLabs receives reviewer interest, point to application 2026-06-133 as the current intended version.
```

## Other acknowledged applications

### LiminalQAengineer

```text
Application: 2026-06-0c5
Project: LiminalQAengineer: Open Causality and Temporal Memory for QA Pipelines
Status: Acknowledged
```

Current next action:

```text
Do not expand unless NLnet asks for clarification.
If needed, prepare a lightweight reviewer path later.
```

### Liminal Stack

```text
Application: 2026-06-087
Project: Liminal Stack: Adaptive Routing, Reactive Storage and Secure Containers for Trustworthy AI Infrastructure
Status: Acknowledged
```

Current next action:

```text
Do not expand unless NLnet asks for clarification.
If needed, prepare a lightweight reviewer path later.
```

### PythiaLabs duplicate / older variant

```text
Application: 2026-06-0fe
Project: PythiaLabs: Open Evidence Gates for High-Risk Agentic Actions
Status: Acknowledged; likely older or duplicate variant
```

Current next action:

```text
Do not use this as the primary PythiaLabs code.
Use 2026-06-133 as the main PythiaLabs application reference.
```

## NLnet communication notes

- NLnet confirmed that the LiminalDB budget correction to EUR 50,000 was adjusted.
- NLnet confirmed earlier that the latest PythiaLabs proposal is treated as the intended current version by default.
- Acknowledgement emails say the first round of review may take around 12 to 15 weeks, but this can vary by project and complexity.

## Response playbook

If NLnet asks, answer with short, concrete, reviewer-friendly replies.

Recommended order:

1. Confirm the application code.
2. Link the correct repository.
3. Link the reviewer path.
4. State what is already implemented.
5. State what the grant will fund.
6. State non-claims clearly.
7. Point to milestone issues.

## Current strategic focus

```text
Do not submit new grants immediately.
Focus on keeping the three reviewer-ready projects clean:

1. ProofPath
2. LiminalDB
3. PythiaLabs
```

The goal is not more noise.

The goal is reviewer confidence.
