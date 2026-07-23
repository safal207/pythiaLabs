# Candidate AISVS requirements for causal agent-action incident evidence

Status: community proposal draft  
Target: OWASP AISVS AI Incident Response appendix and related C09 controls  
Reference implementation: CAEP v0.1 in this repository  
Related RFC: [#242](https://github.com/safal207/pythiaLabs/issues/242)

## Submission summary

Current agent-security controls increasingly cover pre-execution authorization, isolated policy decision points, human approval, and audit logging. A remaining incident-response gap is the binding of an authorization decision to:

1. the exact operation dispatched;
2. the observable consequence produced;
3. the causal path to later actions;
4. containment and recovery results;
5. independently verifiable evidence that survives a compromised agent runtime.

The proposed invariant is:

```text
authorization
  → exact dispatch
  → observable consequence
  → containment
  → verified recovery
```

The candidate requirements below are vendor-neutral. CAEP is offered only as a compact reference schema, verifier, and test corpus.

## Scope boundary

These requirements are specific to agentic AI because they address systems in which a model or agent runtime can:

- select tools and compose multi-step actions;
- transform an approved intent into a different dispatched operation;
- cross network, credential, or execution boundaries;
- produce a narrative outcome that differs from the external state change;
- influence or rewrite evidence generated inside its own execution surface;
- continue acting through causally enabled child actions after the initiating step.

They do not replace general SIEM logging, IAM, backup, disaster recovery, or enterprise incident-response controls.

## Candidate requirements

The identifiers below are working labels, not proposed final AISVS numbering.

### IR-ACT-1 — Action episode identity

**Level:** 2  
**Role:** Architecture, verification

> **Verify that** every consequence-bearing agent action is assigned an immutable episode identifier derived from or cryptographically bound to the initiating intent, including the actor or principal, agent runtime, action type, target, parameter digest, execution boundary, requested capability, and decision-time context.

**Rationale:** An investigator must be able to distinguish one approved action episode from a later or modified request without trusting an agent-generated correlation ID.

**Minimum evidence:**

- content-derived or signed episode identifier;
- exact intent record;
- documented binding fields;
- rejection test for mutation of any binding field.

### IR-ACT-2 — Exact dispatch enforcement

**Level:** 2  
**Role:** Architecture, implementation, verification

> **Verify that** an enforcement point outside the agent-controlled execution surface compares the actual tool identity, target resource, network destination, parameters, credential class, and execution boundary against the authorization immediately before dispatch, and blocks or escalates every mismatch.

**Rationale:** Authorization of an intent is insufficient when the actual connector call can drift after approval.

**Minimum tests:**

- mutate parameters after approval;
- redirect an internal target to an external destination;
- replace the approved credential class;
- change the tool or execution boundary;
- verify fail-closed behavior for an unknown decision value.

### IR-ACT-3 — Causal outcome evidence

**Level:** 2  
**Role:** Implementation, verification, incident response

> **Verify that** each dispatched agent action produces a terminal outcome record that identifies its dispatch parent and records the externally observable status, response digest, contacted or changed resources, policy-conformance result, execution duration, and post-action state evidence.

**Rationale:** An agent's statement that an action succeeded, failed, or caused no side effects is not sufficient incident evidence.

**Minimum evidence:**

- dispatch-to-outcome parent link;
- observer or enforcement-source identity;
- post-action state digest or equivalent bounded evidence;
- explicit conformance state: conformant, drift detected, or unknown.

### IR-ACT-4 — Missing outcome as an incident signal

**Level:** 1  
**Role:** Operations, monitoring, incident response

> **Verify that** a dispatched action without a terminal outcome within its defined completion window is classified as an incident signal and cannot be treated as a successful or harmless action solely because no error was reported.

**Rationale:** Loss of the result channel may indicate runtime compromise, enforcement bypass, observer failure, or an incomplete external operation.

**Minimum test:** Dispatch an action and suppress the terminal receipt; verify alerting, containment routing, and an explicit lost-outcome state.

### IR-ACT-5 — Multi-step causal continuity

**Level:** 2  
**Role:** Architecture, logging, incident response

> **Verify that** multi-step agent trajectories preserve append-only parent and child references across authorization, dispatch, outcome, recovery, and subsequent enabled actions, so an investigator can reconstruct which earlier action made each later action possible.

**Rationale:** Chronological logs alone do not prove causal enablement in a long autonomous trajectory.

**Minimum tests:**

- reject an unknown causal parent;
- reject a parent that occurs after its child;
- reject an orphan child action;
- distinguish event time from the time evidence became known to the system.

### IR-ACT-6 — Verified recovery evidence

**Level:** 2  
**Role:** Resilience, incident response, verification

> **Verify that** containment, token revocation, quarantine, rollback, or restoration produces a recovery record containing the recovery objective, resulting state evidence, objective-achievement result, residual external effects, and unresolved dependencies.

**Rationale:** The existence or invocation of a kill switch, rollback command, or runbook is not evidence that the system actually recovered.

**Minimum tests:**

- rollback command executes but the recovery objective is not met;
- credentials remain usable after claimed revocation;
- external effects remain after internal state restoration;
- recovered status is claimed while residual effects remain undeclared.

### IR-ACT-7 — Append-only correction and supersession

**Level:** 2  
**Role:** Logging, governance, incident response

> **Verify that** corrections to agent-action evidence append a supersession record identifying the prior record, reason, new evidence, authority, and transaction time rather than rewriting or deleting the historical decision or outcome.

**Rationale:** Incident reconstruction must preserve what was authorized or believed at the time and what was learned later.

**Minimum test:** Correct a prior outcome and verify that both the original and superseding records remain independently retrievable and ordered.

### IR-ACT-8 — Independently verifiable high-assurance receipts

**Level:** 3  
**Role:** Cryptography, architecture, verification

> **Verify that** high-assurance authorization, dispatch, outcome, and recovery records carry independently verifiable integrity proofs bound to the complete record payload and to a separately managed issuer and authority role, and that downstream verifiers fail closed for unknown keys, unsupported schemes, malformed signatures, issuer mismatch, or authority-role mismatch.

**Rationale:** A runtime-controlled log or an unverified `integrity_proof` field is self-attestation, not proof.

**Minimum evidence:**

- published or otherwise independently available public keyset;
- deterministic signed-record canonicalization;
- separate authority roles for policy decision, enforcement, observation, and incident control;
- proof-verification tests for payload mutation and key substitution;
- portable evidence format usable without access to the producing runtime.

## Suggested verification procedure

A conforming test can use a bounded synthetic episode:

1. Create an intent with exact target, parameter digest, boundary, and capability.
2. Authorize the intent with a finite validity window and credential class.
3. Dispatch the exact operation through an independent enforcement point.
4. Capture the externally observed consequence.
5. Trigger containment and capture recovery state.
6. Export the episode for offline verification.
7. Repeat with one mutation at a time:
   - target;
   - destination;
   - parameters;
   - credentials;
   - boundary;
   - decision value;
   - causal parent;
   - time ordering;
   - outcome omission;
   - false recovery;
   - payload or signature tampering.
8. Confirm that every mutation is rejected, escalated, or represented as an explicit incident state.

## Reference implementation

The CAEP implementation is intentionally small and offline-verifiable:

- JSON Schema 2020-12;
- standard-library semantic and strict validators;
- deterministic signed-record profile;
- Ed25519 verifier using an external authority-bound keyset;
- complete-record JSON Lines transport;
- synthetic and adversarial fixtures;
- 33 automated tests;
- dedicated CI and security checks.

Merged implementation layers:

- base protocol and strict validation: PR #243;
- verified F3 evidence and portable transport: PR #244.

CAEP is not presented as a production security boundary, a certified framework, or a replacement for existing AISVS controls. It is a concrete testable artifact that may help refine requirement language and validation procedures.

## Suggested AISVS placement

Potential integration points:

- **C05:** authorization and policy-decision separation;
- **C09:** orchestration, action authorization, high-impact actions, execution-chain evidence;
- **C12 / planned AI Incident Response appendix:** causal reconstruction, containment, recovery, and portable incident evidence;
- cross-reference to human oversight and out-of-band kill-switch requirements where consequence or reversibility class requires escalation.

The requirements may be split across existing chapters rather than introduced as a new standalone section. The important property is that authorization, exact dispatch, outcome, and recovery remain one independently auditable causal episode.

## Ready-to-post working-group message

> Hello AISVS / Agentic Security contributors — we have published a small vendor-neutral reference implementation for a gap between agent authorization and incident reconstruction.
>
> Existing controls increasingly cover isolated policy decision points, approvals, and logs. The remaining question is whether an investigator can prove that the agent dispatched exactly what was authorized, produced the recorded external consequence, preserved the causal chain to later actions, and actually recovered after containment.
>
> We propose a testable invariant:
>
> `authorization → exact dispatch → observable consequence → containment → verified recovery`
>
> The open CAEP prototype includes a JSON Schema, strict offline validator, Ed25519 verification with authority-role separation, full-record JSONL evidence, adversarial fixtures, and 33 tests. It is not proposed as an AISVS-specific product or required implementation; it is offered as a concrete schema and test corpus for candidate AI Incident Response requirements.
>
> Candidate requirement language and verification procedures are documented in `protocols/caep/OWASP_AISVS_IR_PROPOSAL.md`. Feedback is especially welcome on chapter placement, assurance levels, minimal evidence fields, and whether missing outcomes and failed recovery should be explicit incident states.

## Requested community decision

1. Is this gap already fully covered by current AISVS normative requirements?
2. If partially covered, should these clauses refine C09, the planned IR appendix, or both?
3. Which fields are the minimum interoperable evidence set?
4. Should independently verifiable receipts be Level 3 only, while causal outcome and recovery records remain Level 2?
5. Would maintainers accept a small follow-up PR containing only AISVS-style language and tests, without requiring adoption of the CAEP schema?
