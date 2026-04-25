# Web3 Treasury Action Showcase

## Problem

DAO treasury transfers are high-stakes actions.
A blockchain can prove that a transaction happened, but agentic governance systems also need to explain why a transfer was allowed or rejected before execution.

## What the showcase demonstrates

This deterministic in-memory showcase evaluates a proposed DAO treasury transfer using:

- proposal existence
- permission match
- quorum
- voting window
- timelock
- authorization valid_time
- authorization transaction_time / known-at-decision-time
- transfer expiration

## Why this matters

A treasury action should not proceed merely because it is executable.

It should proceed only when it is:

- structurally valid
- causally permitted
- temporally valid
- known to the system at decision time
- replayable through trace


## Structured decision trace

The showcase returns a chronological trace where each entry includes:

- `event`
- `result`
- optional `reason`
- relevant `expected` / `actual` values when useful
- a final decision entry with `stop_reason`

Example:

```elixir
%{
  event: :quorum_check,
  result: :fail,
  reason: :quorum_not_met
}
```

This makes the showcase useful not only as a demo, but as an audit-oriented explanation of why a treasury transfer was accepted or rejected.

## How to run

```bash
mix run examples/web3_treasury_action_showcase.exs
```

## Relation to Web3 Consensus Reason Layer

This showcase demonstrates the first in-memory Web3 application of the Web3 Consensus Reason Layer roadmap.

It does not add smart contracts, wallets, RPC calls, indexers, or chain adapters.

It shows how PythiaLabs could reason about DAO treasury safety before any on-chain execution.

## Relation to existing showcases

- Agent Safety Showcase: basic action permission gate
- Bitemporal Authorization Showcase: temporal authorization reasoning
- Web3 Treasury Action Showcase: governance + temporal authorization + replayable reason trace
