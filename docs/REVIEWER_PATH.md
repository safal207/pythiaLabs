# PythiaLabs Reviewer Path

Status: reviewer-facing navigation path.

This document gives a short reading path for OpenAI, grant, and external reviewers.

## One-sentence summary

PythiaLabs is an open-source MVP for deterministic pre-execution evidence gates over high-risk AI-agent actions.

## Core thesis

```text
AI agent proposes action -> evidence gate -> ALLOW / BLOCK / ESCALATE
```

PythiaLabs sits before the tool call, transaction, code change, infrastructure action, or governance action happens.

## If you only have 5 minutes

Read:

1. `README.md`
2. `docs/PORTFOLIO_RELATIONSHIP.md`
3. `docs/PYTHIALABS_ONE_PAGE_SUMMARY.md`
4. `docs/architecture_diagram.md`
5. `docs/positioning_vs_transaction_simulation.md`
6. `docs/NON_CLAIMS.md`

Then answer:

```text
Does PythiaLabs clearly function as a pre-execution evidence gate, rather than a Web3 transaction simulator or generic memory product?
```

## Recommended reviewer sequence

1. Start with `README.md` for project positioning and quickstart.
2. Read `docs/PORTFOLIO_RELATIONSHIP.md` to understand the role of PythiaLabs relative to LTP, CML, DMP, and LRI.
3. Read `docs/PYTHIALABS_ONE_PAGE_SUMMARY.md` for the short project summary.
4. Read `docs/architecture_diagram.md` for the action-gate flow.
5. Read `docs/paid_review_demo_reviewer_checklist.md` for deterministic demo review steps.
6. Read `docs/evidence_artifact_schema.md` to understand evidence artifact shape.
7. Read `docs/positioning_vs_transaction_simulation.md` to avoid misclassifying the project as a Web3 transaction simulator.
8. Read `docs/NON_CLAIMS.md` for scope boundaries.

## What PythiaLabs evaluates

PythiaLabs evaluates proposed high-risk agentic actions before execution.

It asks:

```text
Is there enough evidence?
Is the action authorized?
Is the environment/context valid?
Is recovery possible?
Should this be allowed, blocked, or escalated?
```

## What PythiaLabs is distinct from

| System type | Usually answers | PythiaLabs adds |
|---|---|---|
| Transaction simulator | What happens if this transaction is sent? | Should the AI agent reach this tool call at all? |
| Wallet/security tool | Is the wallet or transaction protected? | Is the proposed agent action evidence-backed before execution? |
| CI/CD tool | Can a code/deploy action run? | Should an autonomous agent be allowed to trigger it? |
| Observability | What happened after execution? | Whether action evidence was sufficient before execution. |
| Generic memory product | What did the agent remember? | Whether the proposed action has enough evidence to proceed. |

## Fast validation

Primary Elixir validation path:

```bash
mix deps.get
mix test
```

Reviewer demo path:

```bash
make demo
```

Additional deterministic showcases:

```bash
mix run examples/agent_infra_action_showcase.exs
mix run examples/banking_ai_risk_showcase.exs
mix run examples/web3_treasury_full_showcase.exs
```

## Current evidence anchors

- One-page summary: `docs/PYTHIALABS_ONE_PAGE_SUMMARY.md`
- Portfolio relationship: `docs/PORTFOLIO_RELATIONSHIP.md`
- Architecture diagram: `docs/architecture_diagram.md`
- Paid review demo checklist: `docs/paid_review_demo_reviewer_checklist.md`
- Evidence artifact schema: `docs/evidence_artifact_schema.md`
- Positioning vs transaction simulation: `docs/positioning_vs_transaction_simulation.md`
- OTF reviewer path: `docs/OTF_REVIEWER_PATH.md`
- ProofPath continuation: `docs/PROOFPATH_CONTINUATION_FOR_REVIEWERS.md`
- Grant evidence: `docs/GRANT_EVIDENCE.md`

## Current artifact surface

PythiaLabs currently includes:

- deterministic local action-gate demos;
- stable `ALLOW / BLOCK / ESCALATE` decision framing;
- replayable traces and stop reasons;
- evidence artifact schema documentation;
- Web3 treasury, banking risk, agent infrastructure, and support-safety showcases;
- Elixir/BEAM orchestration with Rust integration paths;
- reviewer-facing docs for grants, pilots, and artifact inspection.

## Reviewer questions

A useful review should answer:

1. Is the product category clear?
2. Is it clear that Web3 treasury is one demo scenario, not the product boundary?
3. Are non-claims explicit enough?
4. Are demos deterministic and locally reviewable?
5. Is the evidence artifact concept understandable?
6. How does PythiaLabs connect to LTP/CML/DMP/LRI?
7. What additional evidence would make this more fundable?

## Portfolio relationship

PythiaLabs is one layer in a broader trustworthy-agent evidence architecture:

```text
PythiaLabs — pre-execution evidence gates
LTP — path-level trace/replay/admissibility
CML — causal permission and responsibility lineage
DMP — decision memory and irreversibility governance
LRI — living identity and relational invariants
```

PythiaLabs' specific role:

```text
Decide whether a proposed AI-agent action should be allowed, blocked, or escalated before execution.
```

## Funding interpretation

PythiaLabs is most fundable as an applied action-gate layer:

```text
an open-source MVP for deterministic pre-execution evidence gates over high-risk AI-agent actions
```

It should not be presented as a production security product, compliance product, or complete agent safety framework.
