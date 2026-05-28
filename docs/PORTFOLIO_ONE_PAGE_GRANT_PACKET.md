# Liminal Evidence Stack — One-Page Grant Packet

Status: portfolio-level grant/reviewer packet.

## Summary

The Liminal Evidence Stack is a tagged, reproducible open-source portfolio for deterministic oversight of agentic AI systems and human-boundary governance.

It combines five narrow artifacts:

```text
PythiaLabs — pre-execution evidence gates
LTP — deterministic trace replay / admissibility
CML — causal permission and responsibility lineage
DMP — decision memory and irreversibility governance
LRI — human revisability and identity-boundary invariants
```

The stack is designed for reviewable evidence, not narrative-only claims.

## Problem

AI agents increasingly take consequential actions: editing code, changing infrastructure, executing workflows, invoking tools, shaping decisions, and maintaining long-term memory about people.

Current review is often too late or too shallow:

- final outputs hide unsafe paths;
- logs show what happened but not why it was allowed;
- decisions lose rationale and reversibility assumptions;
- long-term memory can drift into profiling, identity freezing, or silent authorship;
- reviewers lack reproducible artifacts across the action lifecycle.

## Proposed contribution

The portfolio separates the lifecycle into narrow, testable layers:

| Layer | Question | Current evidence |
|---|---|---|
| PythiaLabs | Should this proposed action proceed before execution? | deterministic demos, reviewer checklist, artifact inspection, sample report |
| LTP | Was the execution path grounded, replayable, and admissible? | 115 deterministic cases, conformance tests, clean-checkout validation |
| CML | Why was this action allowed, and is causal lineage intact? | API smoke tests, safety eval `6/6 matched`, clean-checkout validation |
| DMP | What was decided, why, and did later reality make it irreversible? | schema, examples, validation snapshot, reviewer-ready tag |
| LRI | Is the human still revisable and not compressed into a fixed profile? | 54 tests, 3 identity-boundary fixtures, automated anti-profiling checks |

## Current tagged snapshots

| Artifact | Snapshot |
|---|---|
| PythiaLabs | `v0.1-reviewer-ready` |
| LTP | `v0.2-100k-evidence-upgrade` |
| CML | `v0.1-reviewer-ready` |
| DMP | `v0.1-reviewer-ready` |
| LRI | `v0.3-evidence-expansion` |

Each artifact includes reviewer-facing documentation, validation paths, scope boundaries, and non-claims.

## Why this is fundable

The portfolio provides an unusually concrete starting point for AI safety infrastructure research:

- implemented open-source artifacts rather than only proposals;
- deterministic validation and clean-checkout evidence;
- narrow non-claims to prevent overstatement;
- multiple independent layers that can be evaluated separately;
- a path toward end-to-end benchmarks for high-risk agent actions.

The fundable research question is:

```text
Can high-risk AI-agent behavior be made more reviewable, reproducible, and auditable by separating action gates, trace replay, causal lineage, decision memory, and human-boundary checks into deterministic evidence artifacts?
```

## Proposed next work

A grant would support:

1. **Full-path demo** — one scenario flowing through PythiaLabs -> LTP -> CML -> DMP -> LRI.
2. **Shared evidence packet** — one reviewer report containing gate decision, replay result, causal audit, decision memory, and human-boundary status.
3. **Benchmark expansion** — coding agents, infra actions, financial workflows, governance workflows, and long-term memory scenarios.
4. **External validation** — 2-3 independent reviewer comments/issues and reproducibility checks.
5. **Adapters** — integrations with CI, agent frameworks, MCP-style tools, and workflow engines.
6. **Technical report** — arXiv-style paper documenting architecture, artifacts, limitations, and validation results.

## Reviewer-safe claims

The stack currently claims:

```text
Tagged, reproducible open-source artifacts exist for making selected classes of agentic decisions, traces, causal lineages, decision memories, and human-boundary risks more structured, inspectable, replayable, and testable.
```

The stack does not claim:

- complete AI alignment;
- production-grade safety enforcement;
- certified compliance;
- replacement of human review;
- universal prevention of unsafe actions;
- production-readiness across all layers;
- identity classification, profiling, therapy, diagnosis, social scoring, or automated decisioning about humans.

## Reviewer path

Start here:

```text
docs/LIMINAL_EVIDENCE_STACK.md
```

Then inspect the tagged snapshots and reviewer paths in each repository:

```text
safal207/pythiaLabs
safal207/L-THREAD-Liminal-Thread-Secure-Protocol-LTP-
safal207/Causal-Memory-Layer
safal207/DMP-decision-memory-protocol
safal207/Living-Relational-Identity-LRI
```

## Bottom line

This is not a single monolithic safety claim.

It is a portfolio of narrow, reproducible evidence layers for making AI-agent behavior easier to review before execution, inspect during execution, audit after execution, preserve as decision memory, and bound when humans are affected.
