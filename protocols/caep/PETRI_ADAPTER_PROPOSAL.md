# Proposal: CAEP action-boundary evidence adapter for Petri

Status: external discussion draft  
Target project: https://github.com/safety-research/petri  
Related case pack: [`cases/atlas-whistleblowing/`](cases/atlas-whistleblowing/)  
Related RFC: https://github.com/safal207/pythiaLabs/issues/242

## Summary

Petri is strong at generating realistic alignment-audit environments, exercising target models, and scoring transcripts for concerning behavior. CAEP addresses a complementary question at the simulated-tool boundary:

> Can an evaluator prove that the action actually dispatched was the exact action authorized, and that the recorded consequence and recovery state came from an authority outside the target model?

The proposed integration is an **optional adapter**, not a replacement for Petri's auditor, target, realism filter, or judge.

## Motivation

A transcript may show that a model intended to send a message, modify a file, contact a person, or cross a boundary. For consequence-bearing tool actions, an evaluator may also need a portable record of:

- the exact proposed target, parameters, destination, credential class, and boundary;
- the policy decision made outside the target model;
- the exact simulated-tool dispatch;
- the observable effect returned by the environment;
- containment and recovery evidence when drift occurs.

This is especially useful for scenarios in which a model preserves a legitimate right to refuse or escalate, but attempts to convert that concern into an unauthorized external action or a human-proxy bypass.

## Minimal event mapping

```text
Petri proposed tool event
  → CAEP intent
  → external ALLOW | DENY | REQUIRE_APPROVAL | REVISE decision
  → exact pre-dispatch comparison
  → CAEP dispatch, when permitted
  → simulated environment receipt
  → CAEP outcome
  → optional containment/recovery
```

Suggested adapter input:

```json
{
  "run_id": "petri-run-...",
  "turn_id": "turn-...",
  "tool_identity": "email.send",
  "target_resource": "mailto:recipient@example.org",
  "parameters": {},
  "network_destination": "mail.example.org:443",
  "credential_class": "eval-mailbox-writer",
  "boundary_id": "eval:confidential:v1"
}
```

The adapter derives stable digests for parameters and pre/post state. The raw transcript remains in Petri; CAEP stores only the bounded action evidence needed for verification.

## Trust separation

The following roles should not collapse into one target-model-controlled trust root:

```text
target model / orchestrator
  ≠ policy decision point
  ≠ dispatch enforcement point
  ≠ outcome observer
  ≠ incident controller
```

A Petri model judge may score behavior, but its score is not authorization and its narrative is not an independently observed outcome.

## Fail-closed checks

The adapter should reject or explicitly escalate when:

1. tool identity changes after approval;
2. target, parameters, destination, credential class, or boundary drift;
3. the authorization is expired or unknown;
4. a denied action receives a dispatch record;
5. a dispatched action has no terminal outcome;
6. a human-proxy request hides an external-disclosure capability;
7. containment runs but the recovery objective is not met.

## Non-goals

- no claim that CAEP prevents behavioral misalignment by itself;
- no requirement that Petri adopt CAEP terminology or storage;
- no production credential, network, or sandbox enforcement;
- no forensic reconstruction of Anthropic's internal evaluation environment;
- no use of benchmark transcripts as training data.

## Small proof of concept

A narrow first contribution could:

1. define a Petri tool-event-to-CAEP mapping;
2. export one JSONL action episode per consequence-bearing tool call;
3. run the existing offline validator after an audit;
4. include the synthetic Atlas case pack as a non-benchmark integration fixture;
5. demonstrate that internal escalation remains allowed while recipient drift and human-proxy disclosure are blocked.

## Questions for Petri maintainers

1. Which internal event object is the most stable integration point for proposed and executed tool calls?
2. Should evidence export occur inside the simulated tool, an Inspect hook, or a post-run transcript adapter?
3. Which fields can be recorded without risking benchmark-data leakage?
4. Would maintainers prefer an external companion package before considering an optional in-repository adapter?

## Ready-to-post issue text

> We have implemented a small vendor-neutral action-evidence protocol called CAEP and would like feedback on a narrow optional Petri adapter. Petri would continue to generate and judge behavioral audits; the adapter would only bind a proposed consequence-bearing tool action to an external policy decision, exact simulated dispatch, observable outcome, and optional recovery record.
>
> The motivating gap is that transcript scoring and action authorization are different trust functions. A model can be allowed to refuse or escalate internally while an independent action boundary still blocks unauthorized external disclosure, recipient drift, or a human-proxy bypass.
>
> A synthetic case pack and regression tests are available in `protocols/caep/cases/atlas-whistleblowing/`. The proposed integration and non-goals are documented in `protocols/caep/PETRI_ADAPTER_PROPOSAL.md`.
>
> We would appreciate guidance on the most stable Petri/Inspect event hook and whether maintainers would prefer an external companion adapter as the first proof of concept.
