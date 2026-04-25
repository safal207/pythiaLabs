# Web3 Consensus Reason Layer Roadmap

## Current status

PythiaLabs currently has no blockchain integration.
This document is a roadmap, not an implementation claim.
The current MVP does not require a wallet, smart contract, chain adapter, RPC node, indexer, or token.

## Problem

Web3 systems can prove that a transaction happened.

But agentic Web3 systems also need to explain why an action was allowed, rejected, delayed, escalated, or blocked.

Key questions:
- Who proposed the action?
- What state transition was attempted?
- What rule or permission allowed it?
- Was the permission valid at action_time?
- Did the system know the permission at decision_time?
- Was the governance window open or closed?
- Was quorum satisfied?
- Was the action expired, premature, or stale?
- Can the decision be replayed and audited?

## Core idea

PythiaLabs can become a reason layer for consensus-driven systems.

It does not replace blockchain consensus.
It explains the reasoning boundary around agentic actions that may interact with consensus systems.

Working formulation:

A Web3 agent action should proceed only when it is:
- structurally valid
- causally permitted
- temporally valid
- known at decision time
- replayable through trace

## Use case 1: DAO treasury transfer

For a deterministic in-memory demo of this use case, see: `docs/web3_treasury_action_showcase.md`.

Scenario:
An AI agent proposes a treasury transfer.

Checks:
- treasury proposal exists
- signer or agent role is valid
- quorum threshold was met
- voting window has closed
- timelock has passed
- transfer has not expired
- required authorization was known at decision_time

Possible stop reasons:
- quorum_not_met
- voting_window_still_open
- timelock_not_satisfied
- authorization_expired
- authorization_valid_but_unknown_at_decision_time
- transfer_accepted

## Use case 2: Governance parameter change

Scenario:
An agent proposes a protocol parameter change.

Checks:
- proposal type is allowed
- governance rule matches parameter type
- signer authority is valid
- execution window is active
- policy version is known
- trace can explain the decision

Possible stop reasons:
- unsupported_parameter_change
- missing_governance_rule
- execution_window_not_yet_open
- execution_window_expired
- parameter_change_accepted

## Use case 3: Security or validator action

Scenario:
An agent proposes emergency pause, slashing alert, or security escalation.

Checks:
- evidence exists
- evidence is recent enough
- escalation authority is valid
- action is not stale
- emergency rule is active
- decision is traceable

Possible stop reasons:
- missing_evidence
- stale_evidence
- escalation_authority_missing
- emergency_rule_inactive
- security_action_accepted

## Mapping to existing PythiaLabs components

- Planner loop: controlled propose -> execute -> measure -> stop cycle
- Agent Safety Showcase: basic action constraint gate
- Bitemporal Authorization Showcase: valid_time and transaction_time reasoning
- Temporal-Causal Memory Stack: future multi-layer memory for facts, relations, time, events, and metrics
- Design Principles: timely and mature action as a decision boundary

## Mapping to broader Liminal Stack

- CML: causal permission / why a transition was allowed
- LTP: replayable trace / transition transport
- PythiaLabs: reasoning and decision supervision layer
- Temporal-Causal Memory Stack: cross-run audit and pattern memory

## Grant positioning

Potential grant narratives:
- public goods tooling for AI-assisted governance
- transparent agent decision traces for DAOs
- temporal-causal auditability for treasury operations
- safety layer for autonomous Web3 agents
- replayable reason traces for consensus-adjacent decisions

## Non-goals for current MVP

The current MVP does not include:
- smart contracts
- wallet integration
- chain adapters
- RPC/indexer integration
- DAO governance module
- tokenomics
- production Web3 deployment

This document should not be read as a claim that Web3 integration is implemented.
