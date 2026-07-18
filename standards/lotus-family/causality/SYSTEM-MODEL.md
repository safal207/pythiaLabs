# Lotus causal spacetime system model

The system model extends the original causal test graph with four additional
views while keeping one audit-only source of truth.

## Five dimensions

- **Causal** — why a condition changes risk or outcome.
- **Spatial** — where evidence exists: repository, file, workflow, job,
  dependency graph, step, inherited shell, working directory, test scope,
  evidence bundle, review, or merge gate.
- **Temporal** — which state must precede another and when independently bound
  exact-head evidence becomes stale.
- **Hierarchy** — how goals, invariants, controls, evidence, outcomes, gates, and
  authority boundaries relate.
- **Trajectory** — how the system moves toward bounded snapshot `PASS`,
  fail-closed `DRIFT`, stale evidence, or merge eligibility.

Machine-readable sources:

- `lotus-family-system-v0.1.json` — 49 nodes, 64 unique directed
  relationships, centers, and four canonical trajectories;
- `system-routes-v0.1.json` — 32 connected routes, including runtime
  regressions and governance-only merge trajectories.

## Centers without centralized authority

The model has separate semantic, snapshot-evidence, and governance centers:
the invariant set, same-byte hashes, independently verified exact head, and the
advisory authority boundary.

Same-byte hashing proves which supplied bytes were evaluated. It does not prove
remote provenance. `center.exact_head` participates only in governance
trajectories after `gate.provenance_verified`; runtime audit `PASS` routes retain
`limitation.identity_unverified`.

Centrality scores mean review priority and blast radius only. A highly connected
node deserves stronger tests and independent review; it does not gain ownership
or approval authority.

## Time and merge separation

`PASS` belongs to the bounded snapshot-audit trajectory. Merge eligibility is a
separate trajectory requiring independent provenance binding, fresh exact-head
evidence, green CI, green security, a fresh exact-head review, and no actionable
blockers. Even `state.merge_eligible` terminates at
`authority.advisory_only`.

A head change moves independently bound evidence to `time.evidence_stale`, which
leads to `state.merge_blocked` until checks and review are rerun on the new exact
head.

## Effective execution context

GitHub Actions `defaults.run` values are resolved through workflow, job, and step
scope. Step-level values override job defaults, and job defaults override
workflow defaults. Unknown shells and non-root or dynamic working directories
fail closed because raw command text alone cannot prove which tests execute.

## New blocker rule

Every newly discovered blocker must:

1. add or reuse a system node;
2. add a directed relationship if the causal, spatial, temporal, or hierarchical
   link is new;
3. include an executable route when runtime behavior is involved;
4. preserve the boundary `PASS != APPROVED != MERGED`.
