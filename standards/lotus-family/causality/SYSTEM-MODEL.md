# Lotus causal spacetime system model

The system model extends the original causal test graph with four additional views while keeping one audit-only source of truth.

## Five dimensions

- **Causal** — why a condition changes risk or outcome.
- **Spatial** — where evidence exists: repository, file, workflow, job, dependency graph, step, shell, test scope, evidence bundle, review, or merge gate.
- **Temporal** — which state must precede another and when evidence becomes stale after the exact head changes.
- **Hierarchy** — how goals, invariants, controls, evidence, outcomes, gates, and authority boundaries relate.
- **Trajectory** — how the system moves toward `PASS`, fail-closed `DRIFT`, evidence staleness, or merge eligibility.

Machine-readable sources:

- `lotus-family-system-v0.1.json` — 46 nodes, 62 unique directed relationships, centers, and four canonical trajectories;
- `system-routes-v0.1.json` — 25 connected routes, including runtime regressions and governance-only merge trajectories.

## Centers without centralized authority

The model has semantic and evidence centers: current exact head, invariant set, same-byte hashes, and the advisory authority boundary. They centralize identity, meaning, and evidence consistency. They do **not** centralize execution or decision power.

Centrality scores mean review priority and blast radius only. A highly connected node deserves stronger tests and independent review; it does not gain ownership or approval authority.

## Time and merge separation

`PASS` belongs to the audit trajectory. Merge eligibility is a separate trajectory requiring green CI, green security, a fresh exact-head review, and no actionable blockers. Even `state.merge_eligible` terminates at `authority.advisory_only`.

A head change moves prior evidence to `time.evidence_stale`, which leads to `state.merge_blocked` until checks and review are rerun on the new exact head.

## New blocker rule

Every newly discovered blocker must:

1. add or reuse a system node;
2. add a directed relationship if the causal, spatial, temporal, or hierarchical link is new;
3. include an executable route when runtime behavior is involved;
4. preserve the boundary `PASS != APPROVED != MERGED`.
