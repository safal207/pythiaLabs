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

## Features

### ✅ Comprehensive Test Suite
- 80+ test cases covering all modules
- Property-based tests (symmetry, triangle inequality)
- Integration tests for full refinement pipeline
- CI runs tests automatically on every PR

### 🧠 Intelligent Critic (v0.1)
- Detects score plateaus (no improvement)
- Detects candidate loops (repetitive states)
- Detects slow progress (minimal improvement)
- Provides actionable advice for strategy switching

### 🎯 Multi-Strategy Engine
Three complementary refinement strategies:

- **GreedyLCP** - Fast, deterministic (default)
  - Uses longest common prefix
  - Optimal for strings with similar prefixes
  - Minimal steps for simple cases

- **RandomWalk** - Exploratory, escapes local minima
  - Random edit operations
  - Breaks plateaus effectively
  - Non-deterministic exploration

- **BeamSearch** - Balanced exploration/exploitation
  - Top-k candidate tracking
  - Diverse proposal generation
  - Good for complex problems

**Adaptive Strategy Selection**: Critic + StrategySelector automatically choose the best strategy based on context.

## Quickstart
```bash
mix deps.get
mix compile

# run tests
mix test

# basic refinement demo
mix run examples/lev_demo.exs

# multi-strategy demo (shows dynamic strategy switching)
mix run examples/multi_strategy_demo.exs

# strategy benchmark comparison
mix run benches/strategy_bench.exs

# port worker build + demo (maze)
cd workers/solver_port && cargo build --release && cd ../../
mix run examples/port_demo.exs

# benchmark (NIF vs fallback)
mix run benches/bench.exs
```

## API Usage

### Basic Refinement
```elixir
# Automatic strategy selection (recommended)
{:ok, result} = Pythia.refine("kitten", "sitting")

# Result:
# %{
#   best: %{candidate: "sitting", score: 0},
#   steps: 3,
#   trace: [%{step: 1, proposal: ..., score: ..., meta: %{strategy: :greedy_lcp}}, ...]
# }
```

### Manual Strategy Control
```elixir
# Force greedy-only strategy
{:ok, result} = Pythia.refine("hello", "world",
  enable_multi_strategy: false
)

# Configure strategy selector
{:ok, result} = Pythia.refine("test", "best",
  enable_multi_strategy: true,
  strategy_opts: [
    default_strategy: :random_walk,
    enable_adaptive: true
  ]
)

# Custom termination conditions
{:ok, result} = Pythia.refine("abc", "xyz",
  max_steps: 50,
  threshold: 1,  # Stop when score ≤ 1
  no_improve_limit: 10
)
```

## Planner loop (enhanced)
```
state ← init(problem)
selector ← StrategySelector.new()

repeat up to max_steps:
  # Get Critic advice
  advice ← critic.advise(state, trace)

  # Select strategy (greedy/random/beam)
  strategy ← selector.select(advice, context)

  # Generate proposal using selected strategy
  proposal ← strategy.propose(state, objective)

  candidate ← execute(proposal)
  score ← measure(candidate)

  if score ≤ threshold → stop
  if no_improve ≥ limit → stop

  state ← refine(state)
  trace ← record(step, proposal, score, strategy)

return best
```

## Architecture

```
User
  ↓
Pythia.refine() [Public API]
  ↓
Planner [Orchestration]
  ├→ Critic [Advice: plateau/loop/slow]
  ├→ StrategySelector [Choose: greedy/random/beam]
  ├→ Strategy [Generate proposal]
  ├→ Executor [Apply proposal]
  └→ Kernels [Score via Levenshtein]
       ├→ Rust NIF (fast)
       └→ Elixir fallback (portable)
```

## Test Coverage

```bash
$ mix test

  Pythia
    ✓ refine/3 (15 tests)

  Pythia.Planner
    ✓ termination conditions (5 tests)
    ✓ trace validation (8 tests)
    ✓ convergence (12 tests)

  Pythia.Strategies
    ✓ GreedyLCP (6 tests)
    ✓ RandomWalk (8 tests)
    ✓ BeamSearch (5 tests)

  Pythia.StrategySelector
    ✓ adaptive selection (10 tests)

  Pythia.Critic
    ✓ plateau detection (4 tests)
    ✓ loop detection (4 tests)

  Total: 80+ tests
  Finished in 2.5 seconds
```

## Roadmap

### ✅ Sprint 1: Foundation (COMPLETED)
- Comprehensive test suite (80+ tests)
- Critic v0.1 (heuristics-based)
- Error handling (port worker, validation)
- CI integration

### ✅ Sprint 2: Multi-Strategy (COMPLETED)
- Strategy abstraction (GreedyLCP, RandomWalk, BeamSearch)
- StrategySelector (meta-learner)
- Integration with Critic
- Benchmark suite

### 🔄 Sprint 3: Production Ready (NEXT)
- Phoenix REST API endpoint
- Trace persistence (PostgreSQL/Datomic)
- Performance optimization
- Landing page + playground

### 🔮 Future
- LLM integration for Critic (GPT-4o mini)
- Neo4j hypothesis graph
- Multi-domain executors (code, math, logic)
- Human-in-the-loop interface
