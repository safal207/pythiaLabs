# liminal-pythia — MVP

PythiaLabs is a deterministic temporal-causal reasoning layer for agentic actions. It evaluates whether an action should proceed before execution, produces stable stop reasons, and exports replayable evidence traces for audit and review.

## Current focus

- deterministic reasoning loops
- agent action safety gates
- bitemporal authorization reasoning
- Web3 DAO treasury action review
- evidence export, verification, and tamper detection
- local deterministic demos for grant and reviewer evaluation

## Main demo for reviewers

Run:

```bash
mix run examples/web3_treasury_full_showcase.exs
```

This demo shows:

- accepted treasury action
- rejected treasury action when quorum is not met
- rejected treasury action when authorization was valid but unknown at decision time
- evidence export
- SHA-256 digest generation
- evidence verification
- tamper rejection
- unsigned envelope verification
- signed_demo envelope generation and verification

Expected output guide: `docs/web3_treasury_full_showcase_expected_output.md`

## What PythiaLabs is not yet

PythiaLabs currently does not claim:

- production cryptography
- wallet integration
- smart contract execution
- RPC/indexer integration
- on-chain enforcement
- production identity verification
- persistent external storage

**Mission**: Minimal HRM-style reasoning loop for LIMINAL: `propose → run → measure → refine` with transparent step traces, fast kernels, and safe isolation.

## Stack

- Elixir/BEAM for orchestration
- Rust NIF (via rustler) for fast kernels
- Rust Port worker for sandboxed solvers (BFS maze)
- JSON via `jason`
- CI: GitHub Actions
- License: Pythia Labs Custom License v1.0

## Values
### Business Value
- **Lower compute cost** by winning via refinement, not giant params
- **Explainability** for clients/regulators (auditable traces)
- **Easy integration** on top of GPT-5/LLMs with step control
- **Edge/On‑prem friendly** footprint
- **Reliability** thanks to BEAM supervision

### Human Value
- **Transparent reasoning** (no black box)
- **Co‑thinking**: human can inspect/interrupt/refine
- **Ethics & control**: limits, stop rules, visible logic
- **Learning effect**: users adopt the refinement habit
- **Accessibility**: good performance without huge hardware

## Quickstart
```bash
mix deps.get
mix compile

# refinement demo (strings)
mix run examples/lev_demo.exs

# port worker build + demo (maze)
cd workers/solver_port && cargo build --release && cd ../../
mix run examples/port_demo.exs

# benchmarks (NIF vs fallback)
mix run benches/bench.exs
```

## Planner loop (concept)
```
state ← init(problem)
repeat up to max_steps:
  proposal ← propose(state)
  candidate ← execute(proposal)
  score ← measure(candidate)
  if score ≤ threshold → stop
  if no_improve ≥ limit → (hook) critic → stop (MVP)
  state ← refine(state)
return best
```

## Current MVP status

PythiaLabs is currently an MVP focused on:

- deterministic refinement loops
- observable traces
- stable stop reasons
- Elixir/BEAM orchestration
- Rust NIF / Rust Port worker integration
- deterministic Agent Safety Showcase

The Datomic/Neo4j/XTDB/EventStoreDB/TimescaleDB-style memory layers are not implemented yet.
They are part of the architectural roadmap.

## Roadmap: persistent reasoning memory

Future versions may add persistent reasoning memory with two complementary layers:

1. **Datomic-style append-only step log**  
   Stores every reasoning step as an immutable event for replay, audit, debugging, and version comparison.

2. **Neo4j-style hypothesis graph**  
   Connects actions, constraints, proposals, failures, stop reasons, and successful paths.

This would allow PythiaLabs to support replay, audit, recurring failure analysis, and cross-run reasoning patterns.

This layer is not implemented in the current MVP.

For details, see `docs/persistent_reasoning_memory.md`.

For the broader five-layer roadmap, see `docs/temporal_causal_memory_stack.md`.

For the Web3 application roadmap, see `docs/web3_consensus_reason_layer.md`.

For the design principles behind these decisions, see `docs/design_principles.md`.

For grant preparation materials, see:

- `docs/grant_readiness.md`
- `docs/threat_model_web3_treasury_reason_layer.md`
- `docs/grant_one_pager_web3_treasury_reason_layer.md`

Additional roadmap items:

- temporal-causal memory stack for facts, relations, bitemporal validity, events, and metrics
- critic triggers based on confidence, repeated failure classes, and trace patterns
- multi-domain executors for QA, graph problems, puzzles, and agent actions
- Web3 consensus reason layer for DAO governance, treasury safety, and agentic on-chain actions

## Agent Safety Showcase

PythiaLabs includes a deterministic showcase for controlled agent actions.

The demo shows two core outcomes:
- a safe action proceeds when the required permission is present
- an unsafe action is rejected when authorization is missing

It also includes an invalid action example to show strict shape validation.
The goal is to demonstrate a core PythiaLabs principle: agent actions should produce observable traces and stable stop reasons, not just outputs.

Run:

```bash
mix run examples/agent_safety_showcase.exs
```

## Bitemporal Authorization Showcase

PythiaLabs includes a deterministic showcase for temporal authorization reasoning.

Run:

```bash
mix run examples/bitemporal_authorization_showcase.exs
```

The demo shows how an agent action can be accepted or rejected based on:

- whether the permission was valid at action_time
- whether the system knew about the permission at decision_time
- whether the permission was expired or scheduled for the future

This demonstrates the Temporal-Causal Memory Stack idea without requiring XTDB or any external database.

## Web3 Treasury Action Showcase

PythiaLabs includes a deterministic in-memory showcase for DAO treasury transfer reasoning.

Run:

```bash
mix run examples/web3_treasury_action_showcase.exs
```

The demo shows how a proposed treasury transfer can be accepted or rejected based on:

- proposal matching
- quorum
- voting window
- timelock
- temporal authorization
- transfer expiration

This demonstrates the Web3 Consensus Reason Layer roadmap without requiring smart contracts, wallets, RPC nodes, or chain adapters.

The result includes a structured chronological trace explaining which governance check passed or failed.
The structured trace can also be exported as a deterministic JSON-ready audit artifact.

```bash
mix run examples/web3_treasury_trace_export.exs
```

The exported trace can also be wrapped into a SHA-256 evidence artifact:

```bash
mix run examples/web3_treasury_trace_evidence.exs
```

Evidence artifacts can also be verified locally:

```bash
mix run examples/web3_treasury_trace_verify.exs
```

Evidence can also be wrapped into a signature-ready envelope:

```bash
mix run examples/web3_treasury_evidence_envelope.exs
```

The project also includes a local deterministic demo signer to show how evidence envelopes may later support authorship verification.
This `signed_demo` flow is a deterministic local demo only and is not production cryptography.

```bash
mix run examples/web3_treasury_signed_envelope_demo.exs
```


## Full Web3 Treasury Showcase

Run:

```bash
mix run examples/web3_treasury_full_showcase.exs
```

For expected reviewer-facing output, see: `docs/web3_treasury_full_showcase_expected_output.md`

This single deterministic demo shows:

- accepted and rejected treasury actions
- chronological decision traces
- evidence export
- SHA-256 digest generation
- evidence verification
- tamper rejection
- unsigned evidence envelope verification
- signed_demo envelope generation
- signed_demo verification

The `signed_demo` flow is deterministic local demo logic only and is not production cryptography.
