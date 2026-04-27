# PythiaLabs — EF Ecosystem Support Program Grant Application (USD 50k)

## Project title

PythiaLabs: Deterministic Temporal-Causal Reason Layer for Web3 Treasury Governance

## One-sentence summary

PythiaLabs is a deterministic temporal-causal reasoning layer for agentic governance actions that evaluates Web3 treasury actions before execution and produces stable allow/deny decisions, stop reasons, replayable traces, and tamper-checkable evidence artifacts.

---

## Problem

Web3 treasuries and DAOs increasingly rely on automated agents, scripts, and structured playbooks to move significant amounts of value on Ethereum and related ecosystems.  
Today, there is no widely adopted deterministic reasoning layer that sits between these agentic workflows and execution, evaluates proposed actions before they hit on-chain systems, and produces reproducible, reviewer-facing explanations.  
Existing governance and treasury tooling focuses on proposal submission, voting flows, and execution, but not on a transparent, auditable “reason layer” for pre-execution decisions and agent safety.  
As a result, DAO treasuries are exposed to avoidable errors (misconfigured treasury transfers, incorrect payouts, mismatched authorizations in time, and ambiguous approvals) that are hard to audit after the fact and difficult to simulate before execution.

---

## Why now

The Ethereum ecosystem is in a phase where governance and treasury scale faster than security and verification practices.  
Agentic workflows and multi-step automations are becoming more common around treasuries and protocol operations, but the verification tooling available to DAOs is still largely ad hoc and specific to particular products.  
The Ecosystem Support Program has shifted toward proactive, needs-driven grantmaking via wishlists and targeted RFPs, including calls related to programmable institutional design and verifiable governance.  
This creates a timely opportunity to fund an independent, deterministic reasoning and evidence layer that can be evaluated, replayed, and integrated into a variety of governance and treasury tools without requiring immediate on-chain or wallet integration.

---

## Solution

PythiaLabs provides a deterministic temporal-causal reasoning layer for agentic governance actions.  
It is designed to sit before execution and:

- accept a structured description of a proposed Web3 treasury or governance action (for example, a DAO treasury transfer with its proposal context and temporal constraints);  
- evaluate the action against explicit policies and temporal rules (quorum, voting window, timelock, authorization validity at different times);  
- emit a stable allow/deny decision with human-readable stop reasons for rejected actions;  
- produce structured chronological traces that show which checks passed or failed and in what order;  
- support generation and verification of evidence artifacts for local tamper detection and audit, including digest and envelope flows, as described in the Web3 Treasury demos.  

The core principles are:

- determinism: the same inputs produce the same decisions and traces;  
- replayability: reasoning runs can be reproduced later using saved inputs and expected outputs;  
- transparency: reviewers can inspect which governance checks drove the final decision;  
- agent safety: agent actions are constrained by observable, explainable reasoning rather than opaque heuristics.  

---

## Current MVP / v0.1.0-pregrant

The `v0.1.0-pregrant` release marks a reviewer-focused MVP for deterministic, pre-execution reasoning around Web3 treasury and agent actions.

The repository currently includes:

- a deterministic agent safety showcase demonstrating how safe and unsafe actions are accepted or rejected with observable traces and stable stop reasons;  
- a bitemporal authorization showcase demonstrating decisions that depend on action time, decision time, and authorization validity;  
- a Web3 Treasury Action Showcase for in-memory DAO treasury transfer reasoning, covering proposal matching, quorum, voting window, timelock, temporal authorization, and transfer expiration;  
- a Web3 Treasury Trace Export and Evidence flow that demonstrates how traces can be exported, wrapped into SHA-256 based evidence artifacts, verified, and wrapped into signature-ready envelopes for future authorship verification (with a `signed_demo` local flow that is explicitly not production cryptography);  
- a Full Web3 Treasury Showcase that runs the entire flow in one deterministic command with an expected output guide for reviewers.  

The release is anchored at:

- Tag: `v0.1.0-pregrant`  
- URL: `https://github.com/safal207/pythiaLabs/releases/tag/v0.1.0-pregrant`  

Roadmap documents such as `docs/persistent_reasoning_memory.md`, `docs/temporal_causal_memory_stack.md`, and `docs/web3_consensus_reason_layer.md` describe potential future extensions, but they are not implemented in the current MVP.

---

## Demo instructions

The main reviewer-facing demo described in the README is the **Full Web3 Treasury Showcase**.

Environment (from `README.md`):

- Elixir/BEAM, as configured via `mix.exs`;  
- dependencies installed using `mix deps.get`.  

Steps:

```bash
git clone https://github.com/safal207/pythiaLabs.git
cd pythiaLabs
# Optionally check out the v0.1.0-pregrant tag
# git checkout v0.1.0-pregrant

mix deps.get
mix compile

# Full Web3 Treasury Showcase
mix run examples/web3_treasury_full_showcase.exs
```

This deterministic demo shows, in process output:

- accepted and rejected treasury actions;  
- chronological decision traces;  
- evidence export, digest calculation, verification, tamper rejection, unsigned envelope checks, and a `signed_demo` envelope flow (non-production cryptography).  

The expected reviewer-facing output is documented in:

- `docs/web3_treasury_full_showcase_expected_output.md`  

Other targeted demos:

- Agent Safety Showcase: `mix run examples/agent_safety_showcase.exs`  
- Bitemporal Authorization Showcase: `mix run examples/bitemporal_authorization_showcase.exs`  
- Web3 Treasury Action Showcase: `mix run examples/web3_treasury_action_showcase.exs`  
- Trace export and evidence flows:  
  - `mix run examples/web3_treasury_trace_export.exs`  
  - `mix run examples/web3_treasury_trace_evidence.exs`  
  - `mix run examples/web3_treasury_trace_verify.exs`  
  - `mix run examples/web3_treasury_evidence_envelope.exs`  
  - `mix run examples/web3_treasury_signed_envelope_demo.exs`  

---

## Public goods value

PythiaLabs targets a cross-cutting public-goods problem: making agentic governance and treasury actions more transparent, deterministic, and reviewable before they touch user funds.  
The repository is public and reviewable today, including code, showcases, threat model, and security automation materials.  

We use the following careful framing, aligned with the current licensing and roadmap:

> PythiaLabs is public and reviewable today. As part of the grant work, we plan to clarify the public-goods licensing boundary for specs, test vectors, and reusable verification materials.

This means the grant specifically supports:

- clearer public-goods licensing guidance (documented in `docs/license_strategy.md` and updated according to the work funded by this grant);  
- open, reviewable reasoning specs and test vectors for governance and treasury scenarios;  
- reusable verification patterns that other teams can adopt, even if their core products use different licensing models.

---

## Security and integrity posture

Security and integrity materials are already part of the repository:

- `SECURITY.md` describes security reporting expectations and outlines future hardening work;  
- `docs/threat_model_web3_treasury_reason_layer.md` describes an initial threat model for the Web3 treasury reasoning layer;  
- `docs/security_automation.md` documents CI security automation, including secret scanning;  
- `CHANGELOG.md` and release notes provide a transparent record of changes across versions.  

The design emphasizes:

- deterministic reasoning loops with observable traces and stable stop reasons;  
- explicit, documented non-goals for production cryptography, wallets, and on-chain enforcement at the MVP stage;  
- evidence flows that demonstrate how traces and envelopes can be verified locally, including tamper detection, while still being clearly labeled as non-production cryptography.  

These materials are intended to make it easier for external reviewers, auditors, and governance participants to understand what PythiaLabs does and does not do at this stage.

---

## Limitations (explicit non-goals)

As documented in the README under “What PythiaLabs is not yet”, the current project **does not claim**:

- production cryptography  
- wallet integration  
- smart contract execution  
- RPC/indexer integration  
- on-chain enforcement  
- production identity verification  
- persistent external storage  

We will restate and preserve this limitations block in all grant materials and will not describe the project as production-ready infrastructure.

---

## USD 50k milestone plan

This is a 12‑month, four‑milestone plan with explicit deliverables and acceptance criteria.  
Each milestone produces concrete artifacts in the repository (code, docs, demos) on top of `v0.1.0-pregrant`.

### Milestone 1 (Months 0–3) — Governance Policy Modeling Toolkit

**Goal:** Define a minimal, deterministic representation for governance and treasury policies.

**Deliverables:**

- A documented minimal policy description layer (DSL or structured schema) for Web3 treasury and governance actions, including quorum, voting windows, timelocks, authorization validity, and transfer constraints;  
- At least 3 fully documented policy examples for different DAO treasury scenarios (for example: grants, recurring payments/payroll, emergency payouts) in `docs/` and examples under `examples/`;  
- Updated Web3 Treasury Action and Full Showcase demos using this policy representation.  

**Acceptance criteria:**

- For each example policy, at least one deterministic demo that:  
  - compiles,  
  - runs via a single `mix run ...` command,  
  - produces output matching an expected-output document committed in `docs/`;  
- Threat model document updated to reference the new policy layer and any new classes of misconfiguration risk.

### Milestone 2 (Months 3–6) — Scenario Pack & Replay Engine

**Goal:** Provide a reusable scenario pack and a more explicit replay pathway for reasoning runs.

**Deliverables:**

- A curated scenario pack of at least 10 distinct governance and treasury scenarios (success, failure, edge cases), each with a clear textual description and expected outcome;  
- A documented procedure (and supporting code) for replaying a reasoning run using recorded inputs and expected outputs;  
- One or more CLI entrypoints or tasks that make it easy for reviewers to re-run specific scenarios from the pack.  

**Acceptance criteria:**

- All scenarios in the pack can be run deterministically on a fresh clone with documented commands and expected outputs in `docs/`;  
- At least one scenario that demonstrates how a previously “safe” configuration can become unsafe after a policy change, with a clear narrative of the replayed reasoning.

### Milestone 3 (Months 6–9) — Evidence Verification Patterns

**Goal:** Strengthen the evidence flows demonstrated in the Web3 Treasury showcases and make them easier to adopt.

**Deliverables:**

- A refined evidence format specification (for traces, digests, and envelopes) documented in `docs/`, linked from `docs/threat_model_web3_treasury_reason_layer.md`;  
- Small, language-agnostic verification examples (e.g., JSON-based description) that show how an external tool could verify PythiaLabs evidence;  
- At least one minimal reference verification example outside the core Elixir library (for example, a short script or pseudo-code indicating how to recompute digests and check envelopes).  

**Acceptance criteria:**

- The Full Web3 Treasury Showcase expected-output document updated to explain the evidence artifacts and how they can be verified;  
- A reviewer can follow the documentation to manually or semi-manually verify at least one evidence artifact using the documented procedure.

### Milestone 4 (Months 9–12) — Reviewer-Facing Guides & Governance Drill Kit

**Goal:** Make it straightforward for DAO governance reviewers and grant committees to use PythiaLabs in structured reviews and drills.

**Deliverables:**

- A reviewer guide in `docs/` that explains how to interpret traces, stop reasons, evidence artifacts, and limitations;  
- A “governance drill kit” with at least 3 scripted drills for DAO treasuries (e.g., “misconfigured payout”, “late authorization update”, “expired approval”), each with instructions, commands, and interpretation guidance;  
- A short “integration notes” document for projects that may want to connect existing governance interfaces or dashboards to PythiaLabs demos and reasoning flows.  

**Acceptance criteria:**

- Each drill can be run via a documented `mix run ...` command and has an expected-output document describing what reviewers should look for;  
- Reviewer guide explicitly points back to the limitations block and clarifies non-production status;  
- At least one example section describing how a grant committee could use PythiaLabs outputs as part of a review process.

---

## Budget breakdown (USD 50k)

This is a high-level budget aligned with the milestones above.

- **Core engineering (reasoning engine, policy modeling, scenario pack, evidence flows)** — USD 30k  
  - Implementation and refinement of the policy layer and reasoning paths for treasury and governance scenarios;  
  - Maintenance of deterministic demos and expected-output documents.  

- **Security and threat modeling work** — USD 10k  
  - Iterative threat modeling for the reasoning layer and evidence flows;  
  - Updates to `SECURITY.md`, threat model docs, and security automation.  

- **Documentation, reviewer guides, and governance drills** — USD 7k  
  - Reviewer-facing guides, drill scripts, and integration notes.  

- **Community and ecosystem support** — USD 3k  
  - Time to work with early adopters (e.g., DAOs, auditors) to run drills and refine scenarios;  
  - Preparation of example materials that can be reused in future governance tooling.  

---

## Expected outcomes

By the end of the grant, PythiaLabs aims to deliver:

- a deterministic reasoning layer and policy modeling toolkit that can be used to evaluate Web3 treasury and governance actions before execution;  
- a reusable scenario pack and replay approach that DAOs and reviewers can run locally for drills, self-assessment, and incident reconstruction;  
- documented evidence formats and verification patterns that make it easier for other tools to consume PythiaLabs traces and artifacts;  
- reviewer-facing guides and drills that help governance participants understand how to interpret outputs and where the system’s boundaries are;  
- clearer licensing and public-goods boundaries for specifications, test vectors, and verification materials, as part of the project’s license strategy.  

---

## Repository and release links

- Repository: `https://github.com/safal207/pythiaLabs`  
- Main README and overview: `README.md`  
- Current MVP release: `v0.1.0-pregrant`  
  - Release page: `https://github.com/safal207/pythiaLabs/releases/tag/v0.1.0-pregrant`  

Key documents:

- `CHANGELOG.md` — release notes and maturity history  
- `SECURITY.md` — security policy and hardening roadmap  
- `CONTRIBUTING.md` — contribution expectations  
- `CODE_OF_CONDUCT.md` — community guidelines  
- `docs/grant_readiness.md`  
- `docs/grant_one_pager_web3_treasury_reason_layer.md`  
- `docs/threat_model_web3_treasury_reason_layer.md`  
- `docs/web3_treasury_action_showcase.md`  
- `docs/web3_treasury_full_showcase_expected_output.md`  
- `docs/security_automation.md`  
- `docs/license_strategy.md`  

---

## Final submission checklist

This checklist is for internal use before submitting to the EF Ecosystem Support Program.

- [ ] The application text clearly describes PythiaLabs as a deterministic temporal-causal reasoning layer for agentic governance actions and Web3 treasury safety.  
- [ ] The one-sentence summary matches the repository description and README.  
- [ ] The limitations block is present, unchanged, and visible (no production cryptography, no wallet integration, no smart contract execution, no RPC/indexer integration, no on-chain enforcement, no production identity verification, no persistent external storage).  
- [ ] No claims of production readiness are made anywhere in the application or linked documents.  
- [ ] No claims are made that exceed the current license; public-goods language follows: “PythiaLabs is public and reviewable today. As part of the grant work, we plan to clarify the public-goods licensing boundary for specs, test vectors, and reusable verification materials.”  
- [ ] The main demo command `mix run examples/web3_treasury_full_showcase.exs` is included, and expected output is referenced from `docs/web3_treasury_full_showcase_expected_output.md`.  
- [ ] All referenced docs (`README.md`, `SECURITY.md`, threat model, license strategy, grant readiness, showcases) exist on the `v0.1.0-pregrant` base and render correctly in GitHub.  
- [ ] Milestones are framed as research and infrastructure work, not as deployment of production wallets, smart contracts, or enforcement components.  
- [ ] Budget matches the described scope and timeline (USD 50k across four milestones).  
- [ ] Links to the repository and the `v0.1.0-pregrant` release are correct.  
- [ ] This document (`docs/grant_application_ef_esp_50k.md`) has been reviewed and approved by the maintainer before any submission to EF ESP.
