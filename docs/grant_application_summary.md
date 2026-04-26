# Grant Application Summary — PythiaLabs

## Project

PythiaLabs: Deterministic Reason Layer for Web3 Treasury Actions

## Summary

PythiaLabs is a temporal-causal reasoning layer for agentic Web3 actions. It evaluates whether a DAO treasury action should proceed before execution, producing deterministic allow/deny decisions, stable stop reasons, replayable traces, and verifiable evidence artifacts.

The current MVP focuses on local deterministic demos for Web3 treasury safety, auditability, and reviewer-friendly grant evaluation.

## Problem

DAO treasury and governance workflows are becoming increasingly automated. As AI agents and operational bots enter these workflows, ecosystems need a clear way to answer:

- why was this action allowed?
- why was this action rejected?
- was authorization valid at action time?
- did the system know the authorization at decision time?
- was quorum met?
- was the voting window closed?
- was the timelock satisfied?
- can this decision be audited later?

Blockchains can prove that a transaction happened, but they do not always explain the full reasoning boundary before execution.

PythiaLabs addresses this missing pre-execution reasoning layer.

## Solution

PythiaLabs evaluates governance and temporal constraints before an action proceeds.

For a proposed DAO treasury transfer, the system can produce:

- accepted or rejected status
- stable stop reason
- chronological decision trace
- deterministic export artifact
- SHA-256 evidence digest
- local verification result
- tamper rejection behavior
- signature-ready evidence envelope
- local signed_demo flow for future authorship-verification design

## Current demo

The repository includes a full deterministic local showcase:

```bash
mix run examples/web3_treasury_full_showcase.exs
```

This demo shows:

- accepted treasury action
- rejected action when quorum is not met
- rejected action when authorization was valid but unknown at decision time
- evidence export
- SHA-256 digest generation
- evidence verification
- tamper rejection
- unsigned evidence envelope verification
- signed_demo envelope generation and verification

Expected output guide:

`docs/web3_treasury_full_showcase_expected_output.md`

## Requested grant amount

Suggested request: $50,000

This amount is appropriate for moving the project from deterministic MVP showcase to a stronger grant-ready public-goods toolkit with expanded threat modeling, scenario coverage, evidence validation, and reviewer/operator documentation.

## Milestones

### Milestone 1 — Policy and threat model expansion

Deliverables:

- expanded Web3 treasury policy matrix
- replay, stale-action, revocation, expiry, and adversarial evidence scenarios
- improved threat model documentation
- stronger negative-path test coverage

Budget: $15,000

### Milestone 2 — Evidence and verification hardening

Deliverables:

- stricter evidence schema validation
- deterministic canonicalization documentation
- conformance test vectors
- independent verifier guidance
- clearer evidence envelope versioning

Budget: $20,000

### Milestone 3 — Reviewer and operator adoption materials

Deliverables:

- grant reviewer guide
- DAO operator guide
- demo walkthrough
- integration notes
- example audit report template

Budget: $15,000

## Expected impact

This grant would help produce an open, reusable safety pattern for agentic governance actions.

Expected outcomes:

- clearer pre-execution decision logic for DAO treasury actions
- better auditability for grant-funded operations
- reusable temporal authorization examples
- tamper-detectable evidence artifacts
- reviewer-friendly deterministic demos
- safer design patterns for future human + agent governance systems

## Why now

AI-assisted governance and treasury operations are emerging faster than safety and audit conventions are maturing.

PythiaLabs provides a local-first, deterministic way to test these controls before teams integrate wallets, smart contracts, RPC nodes, or production cryptography.

This makes the project useful during the early safety-design phase, before irreversible on-chain execution is introduced.

## Current limitations

The current MVP does not claim:

- production cryptography
- wallet integration
- smart contract execution
- RPC/indexer integration
- on-chain enforcement
- production identity verification
- persistent external storage
- production key management

The signed_demo flow is deterministic local demo logic only and is not production cryptography.

## Why this team

The project already includes working deterministic demos, tests, trace exports, evidence verification, tamper rejection, threat modeling, and grant-readiness documentation.

The work is grounded in a broader temporal-causal safety stack focused on:

- agent action safety
- temporal authorization
- replayable reasoning traces
- evidence-oriented auditability
- governance decision boundaries

## Closing

PythiaLabs does not replace blockchain consensus.

It adds a missing reason layer around agentic actions before execution.

The goal of this grant is to strengthen PythiaLabs into a public-goods toolkit for deterministic Web3 treasury reasoning, auditability, and safer agent-assisted governance.
