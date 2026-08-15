# RLC-001: Responsibility Lane Continuity Extension for VCE

- **Status:** Draft
- **Version:** 0.1
- **Extends:** RFC-001 — Verifiable Continuation Envelope
- **Scope:** Context compaction, restart, cross-session handoff, and recovery from durable sources of truth

## 1. Abstract

RFC-001 proves that an agent recovered the active operational state and did not silently restore untrusted memory as authority.

RLC-001 adds a second requirement: the resumed agent must also recover the **responsibility topology** of the task before any material action. Knowing *what* happened is not enough when separate ownership lanes, mutation scopes, done conditions, or recent user rulings can be conflated after compaction.

The extension is intentionally additive. It does not change the RFC-001 `0.1` schemas. A runtime may emit a sidecar `Responsibility Lane Continuity` document bound to a VCE `envelope_id`, plus separate lane-restore results.

## 2. Failure class

A continuation can be state-complete but authority-topology-invalid.

Example:

```text
pre-compaction:
  lane A = architecture change
  lane B = verification
  user ruling = keep the architecture change deliberately simple

post-compaction:
  durable checkpoint reread successfully
  files reread successfully
  BUT:
    lane A and B are conflated
    rejected/fallback behavior returns
    partial checks are treated as near-completion
```

This is not ordinary memory loss. The state may have been recovered while the **boundaries that determine who/what may act, where, and under which done condition** were not.

## 3. Governing principle

> A continuation is not valid merely because state was recovered. Ownership and mutation boundaries must also be recovered and revalidated before mutation.

In compact form:

```text
state recovery
→ responsibility-lane recovery
→ source revalidation
→ scoped continuation
```

## 4. Responsibility lane

A responsibility lane is a bounded execution role with:

- `lane_id` — stable identity;
- `owner_ref` — the role/actor responsible for the lane;
- `objective` — what this lane is trying to achieve;
- `mutation_scope.allowed_refs` — effect references this lane may produce;
- `mutation_scope.denied_refs` — effect references this lane must not produce;
- `done_condition` — lane-specific completion criteria;
- `status` — `active | blocked | complete | superseded`;
- `latest_ruling_ref` — the latest user/policy ruling that materially constrains this lane;
- `source_refs` — durable sources that must be reread/revalidated;
- `depends_on` — explicit lane dependencies;
- `lane_digest` — canonical digest of the lane definition.

Scope references are intentionally opaque, vendor-neutral identifiers. Examples include:

```text
artifact:rfc
artifact:schema
capability:verify
workspace:frontend
service:payments
```

A runtime may map these identifiers to files, tools, worktrees, services, or orchestration capabilities.

## 5. Event bindings

Material VCE events must be attributable to a responsibility lane.

RLC-001 requires bindings for VCE events whose type is one of:

- `tool_call`;
- `tool_result`;
- `artifact_modified`;
- `verification_started`;
- `verification_result`.

Each binding includes:

- `event_id`;
- `lane_id`;
- `effect_refs`.

The `effect_refs` must be inside the lane allowlist and outside the lane denylist.

This makes lane conflation machine-detectable instead of a narrative judgment.

## 6. Next-action scoping

The extension carries a lane-scoped next action:

```json
{
  "lane_id": "verification",
  "effect_refs": ["capability:verify"]
}
```

The next action MUST NOT:

- reference an unknown lane;
- target a `complete` or `superseded` lane;
- use effects outside that lane's allowlist;
- use effects explicitly denied by that lane.

## 7. Source revalidation

Every non-superseded lane MUST have a `source_revalidation` restore requirement.

A restore result for a lane records:

- the check ID;
- lane ID;
- `status: passed | pending | failed | conflict`;
- independently observed lane digest;
- source references actually checked;
- conflicting source references, if any.

A `passed` result is valid only when:

1. the observed lane digest matches the expected `lane_digest`;
2. every declared `source_ref` was checked;
3. `conflict_refs` is empty.

A contradiction between recovered sources MUST fail closed. The runtime must not pick a lane interpretation silently.

## 8. Normative invariants

### RLC-001 — Material actions remain lane-attributable

Every material VCE event MUST bind to exactly one known responsibility lane.

### RLC-002 — Lane mutation scope survives recovery

An event or next action MUST NOT produce an effect outside its lane allowlist or inside its denylist.

### RLC-003 — Ownership cannot be inferred from summary text alone

`owner_ref`, objective, mutation scope, done condition, and latest ruling MUST be recovered from the declared lane sources and checked through restore results.

### RLC-004 — Latest ruling remains attached to the lane

A lane MUST retain `latest_ruling_ref` across continuation. A generated summary cannot silently replace the latest user/policy ruling.

### RLC-005 — Lane conflation fails closed

If a material event or next action is attributed to a lane whose scope does not permit its effects, continuation MUST be blocked.

### RLC-006 — Contradictory lane sources fail closed

If reread sources disagree about ownership, objective, scope, done condition, or latest ruling, the lane restore result MUST be `conflict` and consequential execution MUST remain blocked.

### RLC-007 — All live lanes are revalidated

Every lane whose status is not `superseded` MUST have a required source-revalidation check.

### RLC-008 — Lane and extension digests are tamper-evident

`lane_digest` and `extension_digest` use the same `sha256` + `json-sort-keys-utf8-v1` canonicalization profile defined by RFC-001, excluding their own digest field.

## 9. Composition with RFC-001

RLC-001 is an additional gate, not a replacement.

```text
RFC-001 restore gate
AND
RLC-001 responsibility-lane gate
AND
task-specific verification
→ continuation may proceed
```

A runtime MUST NOT claim overall resumability merely because RLC-001 passes. Other VCE and task verification gates remain authoritative for their own scopes.

## 10. Machine-readable contracts

```text
extensions/schema/responsibility-lane-envelope.schema.json
extensions/schema/responsibility-lane-restore-results.schema.json
```

Reference implementation and tests:

```text
extensions/conformance/rlc_reference.py
extensions/conformance/test_rlc_conformance.py
```

Accepted/rejected fixtures:

```text
extensions/fixtures/rlc-accepted.json
extensions/fixtures/rlc-rejected-lane-conflation.json
```

The rejected fixture reproduces the core failure class: an authoring mutation is restored into the verification lane, whose mutation scope explicitly forbids those artifact effects.

## 11. Minimum conformance suite

A conforming implementation must demonstrate:

1. schema validation;
2. unique lane identity;
3. valid lane and extension digests;
4. active-lane existence;
5. lane-scoped next action;
6. material-event lane attribution;
7. rejection of cross-lane effects;
8. source revalidation for every non-superseded lane;
9. rejection of missing source reads;
10. rejection of observed lane-digest mismatch;
11. `pending` → review required;
12. `failed` or `conflict` → blocked;
13. rejection of unknown lane dependencies;
14. rejection of allow/deny overlap;
15. fail-closed behavior for tampering.

## 12. Relation to the Codex compaction failure mode

This extension targets a failure where a post-compaction agent can reread a durable checkpoint and filesystem successfully yet still continue under the wrong responsibility topology.

The expected recovery boundary is therefore stronger than:

```text
summary read
checkpoint read
files read
```

It becomes:

```text
objective revalidated
ownership lanes revalidated
latest rulings revalidated
mutation scopes revalidated
done conditions revalidated
material events rebound to lanes
next action proven in-scope
```

Only then is mutation eligible to continue.

## 13. Open questions

- signed lane definitions and third-party attestations;
- hierarchical/nested responsibility lanes;
- lane transfer and delegation;
- cross-agent lane ownership proofs;
- standardized effect-reference namespaces;
- mapping lane scopes to worktrees, tools, MCP routes, and service capabilities.

## 14. Closing principle

> Recovering the work is not enough. Recover the boundaries that make the work safe to continue.
