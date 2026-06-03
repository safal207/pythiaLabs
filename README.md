# PythiaLabs

Deterministic evidence gates for high-risk agentic actions.

PythiaLabs evaluates whether an AI/agent action should be allowed, blocked, or escalated under current evidence, authorization, environment, credential, and recovery context — producing replayable traces, stable stop reasons, and tamper-checkable evidence artifacts.

## Positioning

PythiaLabs does not replace transaction simulation, wallet security, or contract-monitoring tools.

It sits earlier in the workflow: evaluating AI-agent proposed actions before tools are called.

Web3 treasury is one high-risk demo scenario, not the product category.

## Project summary

For a concise reviewer-facing overview, see:

- **NGI Commons reviewer path:** [`docs/NGI_COMMONS_REVIEWER_PATH.md`](docs/NGI_COMMONS_REVIEWER_PATH.md)
- **NGI Commons budget and milestones:** [`docs/BUDGET_AND_MILESTONES_COMMONS.md`](docs/BUDGET_AND_MILESTONES_COMMONS.md)
- **NGI Commons milestone tracker:** [`docs/GRANT_MILESTONE_TRACKER_COMMONS.md`](docs/GRANT_MILESTONE_TRACKER_COMMONS.md)
- **Reviewer path:** [`docs/REVIEWER_PATH.md`](docs/REVIEWER_PATH.md)
- **One-page summary:** [`docs/PYTHIALABS_ONE_PAGE_SUMMARY.md`](docs/PYTHIALABS_ONE_PAGE_SUMMARY.md)
- **Documentation index:** [`docs/README.md`](docs/README.md)
- **Portfolio relationship:** [`docs/PORTFOLIO_RELATIONSHIP.md`](docs/PORTFOLIO_RELATIONSHIP.md)
- **Limitations:** [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md)
- **Architecture diagram:** [`docs/architecture_diagram.md`](docs/architecture_diagram.md)
- **Paid review demo reviewer checklist:** [`docs/paid_review_demo_reviewer_checklist.md`](docs/paid_review_demo_reviewer_checklist.md)
- **Evidence artifact schema:** [`docs/evidence_artifact_schema.md`](docs/evidence_artifact_schema.md)
- **OTF reviewer path:** [`docs/OTF_REVIEWER_PATH.md`](docs/OTF_REVIEWER_PATH.md)
- **Related LS grant path:** [`docs/RELATED_LS_GRANT_PATH.md`](docs/RELATED_LS_GRANT_PATH.md)
- **ProofPath continuation for reviewers:** [`docs/PROOFPATH_CONTINUATION_FOR_REVIEWERS.md`](docs/PROOFPATH_CONTINUATION_FOR_REVIEWERS.md)
- **Demo video:** https://youtu.be/IUk3iO0N4YU
- **Support-safety gate demo:** https://youtu.be/A6UAR3e2r3k
- **Landing page:** [`site/`](site/) (deployable via GitHub Pages)

## NGI Commons grant metadata

```text
Application: 2026-06-133
Fund: NGI Zero Commons / Commons Fund
Requested amount: EUR 30,000
Repository: https://github.com/safal207/pythiaLabs
```

## Landing Page

A landing page for PythiaLabs lives in [`site/`](site/). It is a
zero-runtime-JS static site optimized for fast loading: a small Node build
script renders three localized pages (English, Russian, Chinese) with all
CSS inlined, so each page is a single HTTP request.

Output structure:

- `dist/index.html`   — English (default)
- `dist/ru/index.html` — Русский
- `dist/zh/index.html` — 中文 (Simplified)

`<link rel="alternate" hreflang>` tags and a header language switcher
connect the three locales.

### Local preview

```bash
cd site
npm install
npm run build     # writes dist/
npm run preview   # serves dist/ at http://localhost:5173
npm run dev       # build + serve in one step
```

### Deploy to GitHub Pages

A workflow at `.github/workflows/pages.yml` deploys the contents of `site/`
to GitHub Pages on pushes to `main`. To enable it:

1. In the repository settings, go to **Pages** and set **Source** to
   **GitHub Actions**.
2. Push to `main` (or trigger the workflow manually from the Actions tab).

PythiaLabs is currently an open-source MVP with deterministic local demos. It is not presented as a production enforcement system, regulatory compliance product, or certified safety framework.

## Why this matters

AI agents are moving from text generation into real actions: infrastructure changes, financial decisions, governance actions, and treasury operations. Prompt instructions alone are not a reliable safety boundary. PythiaLabs explores deterministic action gates that make high-risk decisions reviewable, replayable, and auditable.

## Current showcases

- **Agent Infrastructure Action Safety** — destructive infrastructure actions such as production volume deletion.
  
  Expected output: [`docs/agent_infra_action_showcase_expected_output.md`](docs/agent_infra_action_showcase_expected_output.md)
- **Banking AI Risk** — high-risk financial/agentic actions with operator approval, freshness, and decision-time knowledge checks.
  
  Expected output: [`docs/banking_ai_risk_showcase_expected_output.md`](docs/banking_ai_risk_showcase_expected_output.md)
- **Web3 Treasury Governance** — DAO treasury action review with quorum, timelock, temporal authorization, evidence export, and tamper rejection.
  
  Expected output: [`docs/web3_treasury_full_showcase_expected_output.md`](docs/web3_treasury_full_showcase_expected_output.md)
- **AI Coding Agents / CI Autofix** — pre-execution review for autonomous coding-agent actions such as CI fixes, PR updates, dependency changes, and deploy-adjacent workflows.

## Reviewer quickstart

```bash
mix deps.get
mix test
mix run examples/agent_infra_action_showcase.exs
mix run examples/banking_ai_risk_showcase.exs
mix run examples/web3_treasury_full_showcase.exs
```

## Paid review demo (recordable in ~30 seconds)

Run:

```bash
make demo
```

A single-command, deterministic demo that drives the real
`Pythia.Showcase.Web3TreasuryAction` engine through four Web3 treasury
scenarios — one accepted transfer plus three orthogonal rejection reasons
(quorum, timelock, transfer-window expiration) — and a counterfactual that
flips one evidence field to show the decision flip.

For each scenario the demo:

- runs the engine and prints the per-check evidence trace,
- builds an evidence record with a real SHA-256 digest, and
- calls `Pythia.Showcase.Web3TreasuryAction.verify_evidence/1` to confirm the
  digest round-trips (plain evidence verification, not the signed
  `verify_evidence_envelope/1` path).

Inputs live in `examples/paid_review_demo_input.json`; the run writes a bundle
of evidence records to `examples/output/paid_review_demo_artifact.json`
(gitignored — regenerated each run). For expected reviewer-facing output, see
`examples/paid_review_demo_expected_output.md`.

## Cursor / IDE bridge (MCP)

A minimal **stdio MCP server** in [`integrations/mcp/`](integrations/mcp/) calls `mix pythia.eval_json` locally so Cursor (or any MCP host) can run deterministic gates (`agent_infra_action`, `banking_risk_action`, `web3_treasury_action`) from JSON.

```bash
# Any supported gate — see integrations/mcp/README.md
echo '{"gate":"agent_infra_action","action":{...},"safety_context":{...}}' | mix pythia.eval_json
```

For users who do not want to remember the `mix` invocation, a thin wrapper at
[`bin/pythia`](bin/pythia) exposes the same gate as `pythia eval` — and ships
machine-readable input schemas under [`schemas/mcp/`](schemas/mcp/):

```bash
# Stdin (auto-locates the repo from the script path)
echo '{"gate":"agent_infra_action", ...}' | ./bin/pythia eval

# Or from a file
./bin/pythia eval --file proposal.json

# List supported gates and inspect their JSON Schema
./bin/pythia gates
./bin/pythia describe banking_risk_action

# Help
./bin/pythia --help
```

The JSON Schemas (draft-07) describe required fields and types per gate so
editors can give you autocomplete and inline errors before you ever invoke the
evaluator. Set `PYTHIA_REPO_ROOT` if you symlink the script into your `$PATH`
from outside the repository.

Setup steps and `mcp.json` snippet: [`integrations/mcp/README.md`](integrations/mcp/README.md).

## What PythiaLabs is not yet

PythiaLabs currently does not claim:

- production cryptography
- wallet integration
- smart contract execution
- RPC/indexer integration
- on-chain enforcement
- production identity verification
- persistent external storage
- cloud-provider integration
- IAM enforcement
- backup management
- regulatory compliance
- production-grade cybersecurity protection

See [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) for the reviewer-facing scope note.

## Agent Infrastructure Action Safety Showcase

PythiaLabs includes a deterministic local showcase for high-risk agent infrastructure actions.
It demonstrates decision-time replay reasoning for destructive operations such as production database volume deletion.

Run:

```bash
mix run examples/agent_infra_action_showcase.exs
```

For expected reviewer-facing output, see: `docs/agent_infra_action_showcase_expected_output.md`

This is a deterministic local showcase only. It does not implement production infrastructure controls and does not claim cloud-provider integration, IAM enforcement, backup management, or cybersecurity protection.

## Banking AI Risk Showcase

PythiaLabs includes a deterministic banking-risk action showcase for AI-enabled financial workflows.
It demonstrates how a proposed high-risk action can be accepted or rejected during deterministic decision-time replay based on operator approval, evidence freshness, temporal authorization, and decision-time knowledge.
The showcase emits stable stop reasons and replayable evidence artifacts for audit and review.

Run:

```bash
mix run examples/banking_ai_risk_showcase.exs
```

For expected reviewer-facing output, see: `docs/banking_ai_risk_showcase_expected_output.md`

This is a deterministic local showcase for governance/audit reasoning. It does not claim production banking integration, regulatory compliance, or cybersecurity protection.

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

## Stack

- Elixir/BEAM for orchestration
- Rust NIF (via rustler) for fast kernels
- Rust Port worker for sandboxed solvers (BFS maze)
- JSON via `jason`
- CI: GitHub Actions
- License: Apache License 2.0

Runtime note: canonical float encoding in evidence paths uses Erlang/OTP 25+ behavior (`:erlang.float_to_binary/2` with `[:short]`).

## Storage Architecture

PythiaLabs separates three kinds of truth:

- Postgres — product truth: teams, paid reviews, pilots, workflow submissions.
- TimescaleDB — temporal measurement truth: decision events, latency, outcome trends, failure classes.
- LiminalDB — adaptive causal-memory truth: agentic state, causal transitions, evidence evolution, and replayable decision context.

The gate decides before execution.
The storage architecture preserves why that decision was valid, measurable, and auditable.

[Read the database architecture](docs/database_architecture.md)

## Current MVP status

PythiaLabs is currently an MVP focused on:

- deterministic refinement loops
- observable traces
- stable stop reasons
- Elixir/BEAM orchestration
- Rust NIF / Rust Port worker integration
- deterministic evidence gates for high-risk agentic actions
- Agent Infrastructure Action Safety Showcase
- Banking AI Risk Showcase
- Web3 Treasury Governance Showcase

The Datomic/Neo4j/XTDB/EventStoreDB/TimescaleDB-style memory layers are not implemented yet.
They are part of the architectural roadmap.

## Core MVP / legacy demos

**Mission**: Minimal HRM-style reasoning loop for LIMINAL: `propose → run → measure → refine` with transparent step traces, fast kernels, and safe isolation.

### Values
#### Business Value
- **Lower compute cost** by winning via refinement, not giant params
- **Explainability** for clients/regulators (auditable traces)
- **Easy integration** on top of GPT-5/LLMs with step control
- **Edge/On‑prem friendly** footprint
- **Reliability** thanks to BEAM supervision

#### Human Value
- **Transparent reasoning** (no black box)
- **Co‑thinking**: human can inspect/interrupt/refine
- **Ethics & control**: limits, stop rules, visible logic
- **Learning effect**: users adopt the refinement habit
- **Accessibility**: good performance without huge hardware

### Legacy quickstart
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

### Planner loop (concept)
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
- `docs/grant_application_summary.md`

Additional roadmap items:

- temporal-causal memory stack for facts, relations, bitemporal validity, events, and metrics
- critic triggers based on confidence, repeated failure classes, and trace patterns
- multi-domain executors for QA, graph problems, puzzles, and agent actions
- Web3 consensus reason layer for DAO governance, treasury safety, and agentic on-chain actions

## Further Reading

- [Database Architecture](docs/database_architecture.md) — Postgres, TimescaleDB, and LiminalDB as three kinds of truth.
- [Agent Memory vs. Action Gates](docs/agent_memory_vs_action_gate.md) — why PythiaLabs is not an organizational memory product.
- [Sponsorship and Paid Pilots](docs/SPONSORSHIP.md) — support paths, paid review scope, and sponsorship options.

## Research / Positioning / Docs

- Open agentic models need evidence gates: `docs/open_agentic_models_need_evidence_gates.md`

## Project trust and governance

Project governance and trust materials:

- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `CHANGELOG.md`
- `docs/license_strategy.md`
- `docs/security_automation.md`

These documents describe contribution expectations, security reporting, project maturity, release notes, and licensing strategy.

The repository also includes a minimal GitHub Actions security workflow for secret scanning.
