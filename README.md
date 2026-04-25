# liminal-pythia — MVP

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

# benchmark (NIF vs fallback)
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

See `docs/persistent_reasoning_memory.md`.

For the broader five-layer roadmap, see `docs/temporal_causal_memory_stack.md`.

Additional roadmap items:

- temporal-causal memory stack for facts, relations, bitemporal validity, events, and metrics
- critic triggers based on confidence, repeated failure classes, and trace patterns
- multi-domain executors for QA, graph problems, puzzles, and agent actions

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

