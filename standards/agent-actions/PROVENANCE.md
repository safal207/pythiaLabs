# Action Envelope V1 provenance and related prior work

**Status:** Reviewer-verifiable provenance record  
**Scope:** Public concepts, implementation lineage, and attribution actions for PythiaLabs Action Envelope V1  
**Tracking issue:** [#215](https://github.com/safal207/pythiaLabs/issues/215)

## Purpose

This document records related public work without claiming ownership of generic
ideas such as pre-execution authorization, fail-closed validation, deterministic
hashing, replay protection, or conformance testing.

It also avoids treating conceptual similarity as proof of copying. A direct
adaptation requires a concrete mapping of distinctive fields, executable logic,
test structure, or wording.

No item below implies CrewAI adoption, certification, endorsement, standards
ownership, or production-security approval.

## Public chronology

### PythiaLabs lineage before July 2026

- **2026-05-05 — PythiaLabs issue #83:** specified a deterministic
  pre-execution gate returning `ALLOW`, `BLOCK`, or `ESCALATE`, a stable stop
  reason, and an evidence artifact suitable for reviewer comparison.
  Source: https://github.com/safal207/pythiaLabs/issues/83
- **2026-05-07 — PythiaLabs issue #128:** documented the coding-agent flow
  `agent proposes action -> evidence snapshot -> ALLOW/BLOCK/ESCALATE -> tool
  call/PR/human review/no-op`.
  Source: https://github.com/safal207/pythiaLabs/issues/128
- **2026-05-24 — PythiaLabs issue #189:** positioned PythiaLabs as the
  pre-execution evidence-gate/action-admissibility layer and separately named
  trace/replay, causal permission, decision memory, and irreversibility layers.
  Source: https://github.com/safal207/pythiaLabs/issues/189
- **2026-06-03 — PythiaLabs issue #190:** requested a versioned public evidence
  schema containing action proposal, authorization chain, evidence freshness,
  recovery/risk, and decision-output fields.
  Source: https://github.com/safal207/pythiaLabs/issues/190
- **2026-06-03 — PythiaLabs issue #192:** requested replayable
  `ALLOW/BLOCK/ESCALATE` cases with expected outputs, generated evidence, and a
  rule that tampering or missing evidence changes the decision.
  Source: https://github.com/safal207/pythiaLabs/issues/192

These artifacts establish that the core PythiaLabs product boundary — a
pre-execution evidence gate with deterministic decisions — predates the July 1
CrewAI discussion cited in the attribution request.

### Related implementation in the maintainer portfolio

- **2026-06-30 20:02 UTC — ibex-agent-verification PR #63 opened; 22:06 UTC
  merged:** implemented a JCS-based verifiable action chain:
  `action_envelope -> action_id -> decision_id -> execution_outcome_id ->
  audit_record_id`, with exact upstream identifier binding and fail-closed
  continuation checks.
  Source: https://github.com/safal207/ibex-agent-verification/pull/63
- **2026-07-01 04:51 UTC — ibex-agent-verification PR #64 opened; 05:39 UTC
  merged:** published a strict self-describing `ActionEnvelopeV1`, immutable
  schema identity, canonical action identifier, conformance vector, unknown-field
  rejection, and continuation mismatch tests.
  Source: https://github.com/safal207/ibex-agent-verification/pull/64

The ibex implementation is a separate repository and contract surface, but it is
relevant prior implementation by the same maintainer and must be included when
reviewing lineage.

### CrewAI discussion and acknowledgements

- **2026-06-30 16:03 UTC — Correctover comment in CrewAI #4877:** addressed
  `@safal207`, described frozen action-envelope binding as the implementation
  path being proposed, and referred to 17 existing schema/fail-closed/crosswalk
  conformance tests.
  Source: https://github.com/crewAIInc/crewAI/issues/4877#issuecomment-4845534502
- **2026-07-01 06:39 UTC — Correctover comment in CrewAI #4877:** called the
  merged `ActionEnvelopeV1` a milestone, described its immutable conformance
  vector, and proposed the adapter path
  `BeforeToolCallHook -> ActionEnvelopeV1 -> action_id -> Correctover validation
  -> GuardrailDecision`.
  Source: https://github.com/crewAIInc/crewAI/issues/4877#issuecomment-4851029064
- **2026-07-01 17:17 UTC — Correctover comment in CrewAI #4877:** introduced the
  phrase **“honesty theater”** for disclosure without decision-path dependency
  and described binding `reversibility` and `source_class` into a verdict digest.
  Source: https://github.com/crewAIInc/crewAI/issues/4877#issuecomment-4858225716
- **2026-07-01 19:55 UTC — PythiaLabs issue #211:** converted the existing
  PythiaLabs gate/evidence/replay work into a bounded roadmap for a formal,
  versioned machine-verifiable action protocol.
  Source: https://github.com/safal207/pythiaLabs/issues/211
- **2026-07-01 20:06 UTC — PythiaLabs PR #213:** published the PythiaLabs
  `Action Envelope V1` schema, evaluator, examples, decision-code registry, and
  executable conformance suite.
  Source: https://github.com/safal207/pythiaLabs/pull/213
- **2026-07-02 — attribution request on PR #213:** requested credit for the
  phrase, the CrewAI discussion, and a five-case conformance framework.
  Source: https://github.com/safal207/pythiaLabs/pull/213#issuecomment-4862357577

## Provenance table

| Source concept or artifact | PythiaLabs artifact | Actual overlap | Independent additions in PythiaLabs | Attribution action |
|---|---|---|---|---|
| Generic pre-tool-call authorization / guardrail provider pattern | Action Envelope lifecycle and evaluator | Both gate an action before a side effect | Strict envelope schema, authorization tuple, evidence freshness, replay input, recovery readiness, stable reason codes | Cite CrewAI #4877 as related public discussion; do not imply CrewAI adoption |
| PythiaLabs pre-execution gate (`ALLOW/BLOCK/ESCALATE`) from May 2026 | Decision semantics and tests | Direct internal lineage | Stable stop-reason registry and strict schema classification | Cite PythiaLabs #83, #128, #189, #190, and #192 |
| ibex verifiable action chain and `ActionEnvelopeV1` | Canonical envelope integrity and exact action binding | Related implementation by the same maintainer; not the same schema | PythiaLabs adds evidence rows, temporal semantics, preconditions, recovery, and domain-neutral decision codes | Cite ibex PRs #63 and #64 as prior portfolio implementation |
| “Frozen action-envelope binding” discussed in CrewAI #4877 | Digest mismatch and action-bound authorization/evidence tests | Shared structural principle | PythiaLabs uses its own schema, canonicalization identifier, decision codes, and evaluator ordering | Credit the CrewAI discussion and named participants where the discussion materially shaped presentation |
| “Honesty theater” phrase | Governing principle that prose/disclosure must not replace machine-verifiable enforcement | Related conceptual framing; the exact phrase is not normative PythiaLabs terminology | Existing PythiaLabs gate predates the phrase; Pythia evaluator directly reads fields and changes decisions | Credit Correctover whenever the phrase itself is used or discussed |
| Correctover guardrail-conformance benchmark | PythiaLabs executable conformance suite | Both test whether declared controls affect behavior | The case sets and decision models differ materially; see comparison below | Cite benchmark as related work; credit its README’s named contributors rather than attributing all five cases to one party |

## Five-case benchmark comparison

The public benchmark describes these cases:
https://github.com/Correctover/guardrail-conformance-benchmark#the-5-conformance-cases

Its own README attributes the five-case fixture shape to `@Tuttotorna`, the
reference decision implementation and fixture execution to `@babyblueviper1`,
and the “honesty theater” phrase plus a provider implementation to Correctover.

| Benchmark case | PythiaLabs comparison | Classification |
|---|---|---|
| 1. Supported Dimension Effect | PythiaLabs changes the decision when authorization identity, evidence binding/freshness, precondition status, idempotency state, or recovery readiness changes. It does not implement the benchmark’s confidence/reversibility function. | Shared generic conformance goal; different dimensions and fixture shape |
| 2. Low Confidence + Irreversible -> `HARD_BLOCK` | PythiaLabs has no `confidence_deficit`, `reversibility` input, or `HARD_BLOCK` verdict. Missing mandatory rollback produces `ESCALATE / RECOVERY_NOT_READY`. | No direct test mapping |
| 3. Unsupported Source Class | PythiaLabs has source provenance in evidence but no `source_class` support declaration or equivalent benchmark case. | No direct test mapping |
| 4. Disclosed Unread Field | The Pythia evaluator reads authorization, evidence, precondition, idempotency, and recovery fields. The suite does not contain the benchmark’s generic write-only-field detector. | Partial conceptual overlap; no copied fixture structure demonstrated |
| 5. Unbound Read Field | PythiaLabs binds the serialized envelope into a digest and separately checks authorization/evidence against the action. It does not implement the benchmark’s `decision_ref` field-binding fixture. | Partial structural overlap; different identifiers, logic, and test shape |

The PythiaLabs suite additionally covers cases not present in the five-case
benchmark, including:

- malformed versus unsupported schema-version classification;
- unknown top-level and nested-field rejection;
- decision-before-creation temporal ordering;
- authorization not-yet-valid and expiry checks;
- evidence action mismatch, future observation, expiry, duplicate IDs, and
  unknown references;
- failed versus unresolved precondition classification;
- duplicate idempotency-key detection;
- rollback-readiness escalation;
- stable decision/reason-code formats.

## Attribution decisions

1. **Credit Correctover for the phrase “honesty theater”** whenever that phrase
   is used in PythiaLabs documentation or discussion.
2. **Credit the broader CrewAI #4877/#5888 discussion** as related public work on
   provider contracts, decision records, frozen transitions, and conformance.
3. **Credit contributors by the roles stated in the benchmark’s own README:**
   `@Tuttotorna`, `@babyblueviper1`, and Correctover.
4. **Document PythiaLabs and ibex prior artifacts** so reviewers can distinguish
   pre-existing project lineage from later framing and hardening.
5. **Do not state that PythiaLabs copied the five-case fixture** unless a future
   comparison demonstrates distinctive field, logic, test, or text reuse.
6. **Correct this record** if an exact public mapping demonstrates a direct
   adaptation not presently identified.

## Current conclusion

The evidence supports a mixed lineage:

- PythiaLabs’ pre-execution gate, deterministic decisions, evidence artifacts,
  and reproducible cases existed publicly before July 2026;
- the same maintainer had already merged a strict `ActionEnvelopeV1` and
  verifiable action chain in ibex before the cited “honesty theater” comment;
- the CrewAI discussion contributed useful public framing and related
  conformance ideas that should be credited;
- the public five-case benchmark is related prior work, but its published cases
  are not the same executable case set as the PythiaLabs suite;
- no current evidence establishes line-by-line copying or a direct downstream
  relationship for the whole PythiaLabs implementation.

This conclusion is intentionally revisable when new exact evidence is provided.
