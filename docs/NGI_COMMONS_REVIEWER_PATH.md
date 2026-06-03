# NGI Commons Reviewer Path

## Project

**PythiaLabs: Open Evidence Gates for High-Risk AI-Agent Actions**

Repository: https://github.com/safal207/pythiaLabs

Primary NLnet application code: `2026-06-133`

## One-sentence summary

PythiaLabs is an open-source evidence-gate layer for high-risk AI-agent actions, producing deterministic ALLOW, BLOCK, or ESCALATE decisions with replayable traces and tamper-checkable evidence artifacts.

## Why this matters

AI agents are moving from text generation into tool execution. They can propose code changes, infrastructure commands, financial workflows, governance actions, and other high-risk operations.

Prompt instructions and model policies are not enough as an execution boundary.

PythiaLabs focuses on a simpler reviewer question:

> Is the available evidence sufficient to allow this action now?

The project turns that question into a reusable open-source schema, CLI, and demo library.

## Fit with NGI Commons

PythiaLabs fits the NGI Commons direction because it is designed as a reusable libre/open-source building block for agentic AI governance and safety.

The project produces:

- a JSON evidence schema;
- deterministic gate decisions;
- replayable traces;
- stable stop reasons;
- demo cases across multiple high-risk domains;
- GitHub Actions integration path;
- reviewer-facing documentation;
- explicit limitations and non-claims.

It is not a proprietary SaaS, not a wallet product, and not a production enforcement claim.

## Reviewer quick path

Start here:

1. Read this file.
2. Read `docs/REVIEWER_PATH.md`.
3. Read `docs/PYTHIALABS_ONE_PAGE_SUMMARY.md`.
4. Run `mix deps.get` and `mix test`.
5. Run the three main showcases:
   - `mix run examples/agent_infra_action_showcase.exs`
   - `mix run examples/banking_ai_risk_showcase.exs`
   - `mix run examples/web3_treasury_full_showcase.exs`
6. Compare expected output files in `docs/*_expected_output.md`.
7. Read `docs/BUDGET_AND_MILESTONES_COMMONS.md`.
8. Inspect `docs/GRANT_MILESTONE_TRACKER_COMMONS.md`.

## Current project status

The current repository demonstrates:

- deterministic local demos;
- evidence artifacts with SHA-256 digest paths;
- replayable traces;
- stable stop reasons;
- AI infrastructure action showcase;
- banking-risk action showcase;
- Web3 treasury governance showcase;
- MCP/IDE bridge path;
- CLI wrapper through `bin/pythia`;
- documentation, limitations, and architecture notes.

## Current non-claims

PythiaLabs does not currently claim:

- production cryptography;
- wallet integration;
- smart contract execution;
- RPC or indexer integration;
- cloud IAM enforcement;
- production cybersecurity protection;
- regulatory compliance;
- autonomous real-world action execution.

The current claim is narrower and stronger:

> PythiaLabs provides deterministic local evidence gates and reviewer-facing artifacts for high-risk AI-agent action proposals.

## Grant deliverable target

The NGI Commons grant plan turns the current MVP into a clearer open-source evidence-gate component with:

- Evidence schema v0.1;
- CLI command `pythia gate` or equivalent stable reviewer path;
- at least 9 reproducible demo cases;
- ALLOW / BLOCK / ESCALATE coverage;
- GitHub Actions prototype;
- threat model;
- implementation guide;
- public reviewer report.

## Success criteria

A reviewer or developer should be able to:

- clone the repository;
- run tests;
- run deterministic demos;
- inspect evidence artifacts;
- observe ALLOW, BLOCK, and ESCALATE behavior;
- verify that tampering changes evidence validation results;
- understand what is validated today and what remains a target.

## Suggested reviewer commands

```bash
git clone https://github.com/safal207/pythiaLabs.git
cd pythiaLabs

mix deps.get
mix test
mix run examples/agent_infra_action_showcase.exs
mix run examples/banking_ai_risk_showcase.exs
mix run examples/web3_treasury_full_showcase.exs
make demo
```

## Grant proposal reference

```text
Application: 2026-06-133
Fund: NGI Zero Commons / Commons Fund
Project: PythiaLabs: Open Evidence Gates for High-Risk AI-Agent Actions
Requested amount: EUR 30,000
Repository: https://github.com/safal207/pythiaLabs
```

## Duplicate proposal note

There is another acknowledged PythiaLabs application code, `2026-06-0fe`, with a similar title.

The intended current version is `2026-06-133`. NLnet has confirmed that the latest proposal is treated as the current version by default.
