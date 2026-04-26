# Grant One-Pager — Web3 Treasury Reason Layer

## Project title

PythiaLabs: Deterministic Reason Layer for Web3 Treasury Actions

## One-sentence pitch

PythiaLabs is a temporal-causal reasoning layer that evaluates agentic Web3 treasury actions before execution, producing deterministic allow/deny decisions, stable stop reasons, replayable traces, and verifiable evidence artifacts.

## Problem

DAO treasury and governance workflows are becoming more automated, but many systems still struggle to explain why a high-stakes action was allowed or rejected.

A blockchain can prove that a transaction happened, but it usually does not explain the full reasoning boundary before execution:

- Was the proposal valid?
- Was quorum met?
- Was the voting window closed?
- Was the timelock satisfied?
- Was authorization valid at action time?
- Did the system know that authorization at decision time?
- Was the action expired, stale, or replayed?
- Can the decision be audited later?

As AI agents enter governance and treasury operations, this gap becomes more dangerous.

## Solution

PythiaLabs adds a deterministic pre-execution reasoning layer for agentic actions.

For a proposed Web3 treasury transfer, it evaluates policy and temporal constraints before any on-chain execution path is taken.

The system returns:

- accepted or rejected status
- stable stop reason
- chronological decision trace
- deterministic export artifact
- SHA-256 evidence digest
- local verification result
- tamper rejection behavior
- signature-ready envelope structure
- local signed_demo flow for future authorship verification design

## Current implemented demo

The repository includes a full local deterministic showcase:

```bash
mix run examples/web3_treasury_full_showcase.exs
```

This demo shows:

- accepted treasury action
- rejected action when quorum is not met
- rejected action when authorization was valid but unknown at decision time
- trace export
- evidence digest generation
- evidence verification
- tamper rejection
- unsigned evidence envelope verification
- signed_demo envelope generation and verification

Expected output guide:

`docs/web3_treasury_full_showcase_expected_output.md`

## Why this matters

PythiaLabs helps governance systems answer not only:

“Did this action happen?”

but also:

“Was this action allowed at the right time, for the right reason, with evidence that can be reviewed later?”

This is useful for:

- DAO treasury review
- grant committee accountability
- AI agent safety controls
- governance postmortems
- audit and compliance workflows
- public-goods infrastructure
- future human + agent decision systems

## Public goods value

PythiaLabs can provide reusable open patterns for:

- deterministic governance checks
- temporal authorization reasoning
- evidence-oriented decision traces
- tamper-detectable audit artifacts
- reviewer-friendly grant reporting
- safer agentic treasury workflows

## Current limitations

The current stage is an MVP and local deterministic demo stack.

It does not yet include:

- production cryptography
- wallet integration
- smart contract execution
- RPC/indexer integration
- on-chain enforcement
- production identity verification
- persistent external storage
- production key management

The signed_demo flow is explicitly local demo logic only and is not production cryptography.

## Proposed grant scope

### Milestone 1 — Policy and threat model expansion

Expand Web3 treasury reasoning coverage with:

- richer governance policy scenarios
- replay and stale-action cases
- revocation and expiry scenarios
- adversarial evidence cases
- improved threat model documentation

Expected output:

- expanded scenario pack
- stronger negative-path tests
- updated threat model
- reviewer-facing examples

### Milestone 2 — Evidence and verification hardening

Improve the evidence artifact flow with:

- stricter schema validation
- deterministic canonicalization documentation
- independent verifier guidance
- conformance test vectors
- clearer envelope versioning

Expected output:

- versioned evidence profile
- verification guide
- tamper-resistance examples
- external review checklist

### Milestone 3 — Adoption and reviewer tooling

Create materials that make the system easier for grant programs, DAO operators, and technical reviewers to evaluate.

Expected output:

- operator guide
- grant reviewer guide
- integration notes
- demo walkthrough
- example audit report template

## Budget options

### Small grant — $25k

Focus:

- threat model expansion
- policy scenario pack
- expected output documentation
- reviewer-facing grant package

Outcome:

A stronger grant-ready and reviewer-ready deterministic demo package.

### Medium grant — $50k

Focus:

- all small grant items
- evidence schema hardening
- verification profile
- conformance test vectors
- operator documentation

Outcome:

A more robust pre-integration safety toolkit for DAO treasury review.

### Large grant — $100k

Focus:

- all medium grant items
- extended policy matrix
- replay/staleness modeling
- independent verifier specification
- governance drill materials
- ecosystem onboarding package

Outcome:

A full public-goods safety framework for deterministic Web3 treasury reasoning and auditability.

## Success criteria

A successful grant phase should produce:

- deterministic demos that run locally
- stable accept/reject outcomes
- expanded negative-path coverage
- documented threat model
- evidence artifacts that can be verified
- clear non-goals and limitations
- reviewer-friendly output guides
- reusable governance safety patterns

## Closing summary

PythiaLabs is not trying to replace blockchain consensus.

It adds a missing reasoning layer around agentic actions:

- before execution
- with temporal context
- with stable stop reasons
- with replayable traces
- with verifiable evidence artifacts

This makes it easier for Web3 ecosystems to evaluate whether an action should be allowed, rejected, delayed, or escalated before irreversible execution occurs.
