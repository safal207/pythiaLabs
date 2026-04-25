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

## JSON trace export

The Web3 Treasury Action Showcase can export structured traces as deterministic maps suitable for JSON encoding.

This makes traces easier to:

- attach to audits
- include in grant demos
- share with DAO governance teams
- inspect in external tools
- compare across runs

If JSON encoding is available, the showcase can also print JSON output.

## Evidence digest

The exported trace can be wrapped into an evidence artifact with a SHA-256 digest.

This allows external reviewers to verify that a trace artifact has not changed.

The digest is computed over a deterministic canonical representation of the exported trace.

Example evidence shape:

```elixir
%{
  "artifact_type" => "pythia.web3_treasury_action.decision_trace.v1",
  "algorithm" => "sha256",
  "digest" => "...",
  "payload" => %{...}
}
```

This is not a digital signature yet. It is a deterministic fingerprint of the decision artifact.

## Evidence verification

Evidence artifacts can be verified by recomputing the SHA-256 digest over the canonical payload.

This allows external reviewers to detect whether the exported trace payload has changed.

Verification can detect:

- payload tampering
- digest mismatch
- unsupported artifact type
- unsupported algorithm
- malformed evidence shape

This is still not a digital signature.
It verifies artifact integrity, not authorship.

## Signature-ready evidence envelope

For unsigned envelopes, the signature placeholder must remain empty:

```elixir
%{
  "status" => "unsigned",
  "algorithm" => nil,
  "public_key" => nil,
  "signature" => nil
}
```

Any non-nil signature fields are rejected until real signature support is implemented.

## How to run

```bash
mix run examples/web3_treasury_action_showcase.exs
```

## Relation to Web3 Consensus Reason Layer

This showcase demonstrates the first in-memory Web3 application of the Web3 Consensus Reason Layer roadmap.

It does not add smart contracts, wallets, RPC calls, indexers, or chain adapters.

It shows how PythiaLabs could reason about DAO treasury safety before any on-chain execution.

## Non-goals in this stage

This PR does not add:

- digital signatures
- key management
- identity verification
- blockchain anchoring
- IPFS/Arweave upload
- smart contracts
- wallet integration
- persistence

## Relation to existing showcases

- Agent Safety Showcase: basic action permission gate
- Bitemporal Authorization Showcase: temporal authorization reasoning
- Web3 Treasury Action Showcase: governance + temporal authorization + replayable reason trace
