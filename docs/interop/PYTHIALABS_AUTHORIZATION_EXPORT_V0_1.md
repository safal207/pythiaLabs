# PythiaLabs Canonical Authorization Export Profile v0.1

**Status:** Draft interoperability profile  
**Issue:** [PythiaLabs #204](https://github.com/safal207/pythiaLabs/issues/204)  
**Canonical ecosystem profile:** [Liminal #108](https://github.com/safal207/Liminal/issues/108)

## Purpose

PythiaLabs evaluates proposed high-risk agent actions before tool execution.
This profile exports those deterministic gate decisions as provider-neutral
`authorization_record` artifacts that can later be joined to an
`observation_record` and a separately issued `response_integrity_record`.

The record answers:

> What exact action was evaluated, against which decision-time evidence,
> environment, target state, credentials, approval state, and temporal window,
> and what deterministic gate decision was returned?

It does not prove that a downstream tool executed, that an observation source
is uncompromised, or that a model later described the result honestly.

## Files

- Schema: [`schemas/interop/pythialabs-authorization-record-v0.1.schema.json`](../../schemas/interop/pythialabs-authorization-record-v0.1.schema.json)
- Fixtures: [`conformance/pythialabs-authorization-export-v0.1.json`](../../conformance/pythialabs-authorization-export-v0.1.json)
- Exporter/verifier: [`scripts/check_pythialabs_authorization_export.py`](../../scripts/check_pythialabs_authorization_export.py)

Run:

```bash
python3 scripts/check_pythialabs_authorization_export.py
```

Emit one derived record and its optional handoff:

```bash
python3 scripts/check_pythialabs_authorization_export.py \
  --emit-case accepted_with_matching_observation
```

## Portable record

A conforming record includes:

```text
schema
profile
transition_id
subject_id
source_showcase
gate_profile
gate_version
action_identity_profile
action_identity_digest
arguments_profile
arguments_digest
decision
reason_codes
decision_time
evaluation_clock
valid_from
expires_at
approval_state
credential_state
evidence_snapshot_digest
evidence_refs
environment_digest
target_state_digest
continuation_requirement
revalidation_requirements
artifact_digest
verification
claim_boundary
```

The record is wrapped with canonical bytes and a SHA-256 reference:

```text
record_ref = "sha256:" + SHA256(RFC8785-JCS(record))
```

The published vector contains no floating-point values, so standard-library
sorted minimal JSON is equivalent to RFC 8785 JCS for this fixture domain.

## Showcase adapters

The fixture pack demonstrates one portable shape across three existing
PythiaLabs domains:

| Source showcase | Gate profile |
| --- | --- |
| Infrastructure | `pythia.infrastructure.pre_execution.v1` |
| Banking risk | `pythia.banking_risk.pre_execution.v1` |
| Web3 treasury | `pythia.web3_treasury.pre_execution.v1` |

`source_showcase` and `gate_profile` preserve provenance, but Elixir module
names, atoms, structs, or function names are not normative interoperability
fields.

## Decision-time bindings

### Action identity

The action identity digest binds:

```text
caller_id
tool_id
resource_scope
```

### Arguments

The arguments digest binds:

```text
arguments_schema
arguments
```

### Evidence and environment

The record separately preserves:

```text
evidence_snapshot_digest
environment_digest
target_state_digest
artifact_digest
```

This separation makes evidence refresh, environment drift, and target-state
drift visible instead of hiding all context behind one generic hash.

## Decisions

The portable decision values are:

```text
ALLOW
BLOCK
ESCALATE
```

Only an `ALLOW` record whose derived authority state is `ACTIVE` permits the
fixture's one expected side effect. `BLOCK`, `ESCALATE`, expired, or
revalidation-required cases expect zero additional side effects.

## Temporal and drift semantics

A decision may become unusable after it was created because:

- its temporal authorization expired;
- the target-state digest changed;
- the evidence snapshot changed;
- credentials or approval changed;
- an explicit revalidation requirement became active.

The record retains the original decision-time evidence for audit, but stale
evidence does not remain live authority.

## Downstream handoff

A downstream runtime may issue an `observation_record` that repeats:

```text
transition_id
subject_id
authorization_ref
action_identity_digest
binding_digest
```

where `binding_digest` equals the PythiaLabs `arguments_digest`.

A separate verifier may issue a `response_integrity_record` that references the
authorization and observation records. Imported records keep their own issuer,
verifier, and claim boundary. PythiaLabs does not adopt their semantic verdicts
as its own.

## Fixture coverage

The conformance vector covers:

1. accepted reversible infrastructure action;
2. blocked destructive infrastructure action without approval;
3. expired banking-risk temporal authorization;
4. target-state drift after decision;
5. evidence updated before execution;
6. accepted Web3 action with matching observation;
7. accepted Web3 action with a contradicted external response claim.

## Claim boundary

This profile proves deterministic export, canonicalization, digest stability,
decision-time context binding, and record-join consistency for the fixture
domain.

It does not by itself prove:

- production security;
- policy correctness;
- signer or credential identity;
- observation-source integrity;
- financial settlement;
- regulatory compliance;
- complete agent safety;
- truthfulness of a later model response.

## Canonical invariant

> PythiaLabs decides before action and exports exactly what it decided against.
> Execution evidence and response honesty may be attached later, but their
> verdicts remain independent.
