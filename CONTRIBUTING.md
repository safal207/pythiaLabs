# Contributing to PythiaLabs

Thank you for your interest in contributing to PythiaLabs.

PythiaLabs is currently an MVP focused on deterministic temporal-causal reasoning, agent action safety, replayable traces, and evidence-oriented auditability.

## Current contribution scope

Good first contribution areas include:

- documentation improvements
- deterministic test scenarios
- threat model expansion
- example outputs
- grant/reviewer materials
- negative-path tests
- evidence artifact validation examples

Please avoid large architectural rewrites unless discussed first.

## Development setup

Build outputs such as `_build/`, `deps/`, Rust `target/` directories, and compiled NIF artifacts under `priv/` are listed in `.gitignore` so they are not committed by mistake.

```bash
mix deps.get
mix compile
mix test
```

If Rust worker changes are needed:

```bash
cd workers/solver_port
cargo build --release
cd ../../
mix test
```

## Before opening a PR

Please run:

```bash
mix format --check-formatted
mix test
```

The repository includes `.formatter.exs` so formatter inputs are consistent across contributors and CI. CI also runs `mix format --check-formatted`; run it locally before opening a PR.

For documentation-only PRs, still run tests when possible.

## PR guidelines

A good PR should include:

- clear summary
- reason for the change
- affected files
- test status
- known limitations

## Project posture

PythiaLabs is early-stage infrastructure research.

Please keep claims honest:

- do not claim production cryptography unless implemented
- do not claim wallet or smart contract integration unless implemented
- do not claim on-chain enforcement unless implemented
- keep Web3 integration described as roadmap or demo unless production integration exists

## Design principles

Core principles:

- deterministic reasoning over opaque decisions
- stable stop reasons
- replayable traces
- temporal authorization awareness
- audit-friendly evidence artifacts
- clear non-goals and limitations

For more context, see:

- `docs/design_principles.md`
- `docs/web3_treasury_action_showcase.md`
- `docs/threat_model_web3_treasury_reason_layer.md`
