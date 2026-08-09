# Grant Portfolio Status

Last updated: 2026-08-09

## Purpose

This file is the mission-control view for the current NLnet grant portfolio.

It tracks application codes, funds, repositories, reviewer-readiness status, and the next action for each proposal.

## Current portfolio

| Priority | Code | Fund | Project | Status |
|---:|---|---|---|---|
| 1 | 2026-08-00b | NGI TALER | ProofPath Agent Payment Guard | Submitted; reviewer-ready |
| 2 | 2026-08-00c | NGI Fediversity | LiminalDB | Submitted; budget corrected; reviewer-ready |
| 3 | 2026-06-133 | NGI Commons | PythiaLabs | Acknowledged; primary version; reviewer-ready |
| 4 | 2026-06-0c5 | NGI Commons | LiminalQAengineer | Acknowledged; grant-specific reviewer path prepared |
| 5 | 2026-06-087 | NGI Commons | Liminal Stack | Acknowledged; umbrella reviewer map prepared |
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

## Other acknowledged applications with lightweight reviewer paths

### LiminalQAengineer

```text
Application: 2026-06-0c5
Project: LiminalQAengineer: Open Causality and Temporal Memory for QA Pipelines
Repository: https://github.com/safal207/LiminalQAengineer
Status: Acknowledged; grant-specific reviewer path prepared and merged
```

Reviewer path:

- `docs/NLNET_COMMONS_REVIEWER_PATH_2026-06-0c5.md` in `safal207/LiminalQAengineer`
- linked from `docs/REVIEWER_FIRST_SCREEN.md`

Current next action:

```text
Wait for NLnet review response.
Do not expand scope unless NLnet asks; use the grant-specific path to answer implementation-vs-grant-delta questions.
```

### Liminal Stack

```text
Application: 2026-06-087
Project: Liminal Stack: Adaptive Routing, Reactive Storage and Secure Containers for Trustworthy AI Infrastructure
Requested amount: EUR 50,000
Submitted duration: 12 months
Status: Acknowledged; umbrella reviewer map prepared
```

Umbrella reviewer path:

- [`NLNET_LIMINAL_STACK_REVIEWER_PATH_2026-06-087.md`](NLNET_LIMINAL_STACK_REVIEWER_PATH_2026-06-087.md)

Canonical component repositories:

- DAO_lim — https://github.com/safal207/DAO_lim
- LiminalDB — https://github.com/safal207/LiminalDB
- GardenLiminal — https://github.com/safal207/GardenLiminal

Important boundary:

```text
Liminal Stack is an integration/hardening programme, not a fourth product.
Current component evidence is stronger than current full-stack evidence.
The canonical DAO → GardenLiminal → LiminalDB end-to-end demo remains a grant-funded deliverable.
```

Current next action:

```text
Wait for NLnet review response.
Do not create a new Liminal Stack repository.
If clarification is requested, answer from the umbrella reviewer map and the three canonical component repositories.
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
- The acknowledgement for Liminal Stack `2026-06-087` says first-round review is expected to take roughly 12–15 weeks, with natural variation possible.
- No selection/rejection status is inferred from the absence of a later message.

## Response playbook

If NLnet asks, answer with short, concrete, reviewer-friendly replies.

Recommended order:

1. Confirm the application code.
2. Link the correct repository or umbrella reviewer map.
3. State what is already implemented.
4. State what the grant will fund.
5. State non-claims clearly.
6. Point to runnable evidence and exact revisions.
7. Point to milestone issues when the application has explicit milestone tracking.

## Current strategic focus

```text
Do not submit new grants immediately.
Keep the primary reviewer-ready projects clean:

1. ProofPath
2. LiminalDB
3. PythiaLabs

Maintain lightweight reviewer traceability for:

4. LiminalQAengineer
5. Liminal Stack
```

The goal is not more noise.

The goal is reviewer confidence.
