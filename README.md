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

## Next steps (beyond MVP)
- Datomic (step log) + Neo4j (hypothesis graph)
- Critic triggers (confidence‑based, rate‑limited) + cache
- Multi‑domain executors (QA, graphs, puzzles)
