# Proposal: CAEP action-boundary evidence adapter for Inspect Petri 3.x

Status: companion benchmark prototype implemented  
Target project: https://github.com/meridianlabs-ai/inspect_petri  
Related benchmark: [`benchmarks/agent-authority-boundary/`](benchmarks/agent-authority-boundary/)  
Related case pack: [`cases/atlas-whistleblowing/`](cases/atlas-whistleblowing/)  
Related RFC: https://github.com/safal207/pythiaLabs/issues/242

## Summary

Inspect Petri is strong at generating realistic alignment-audit environments, exercising target models, simulating tools and rollbacks, and scoring transcripts. CAEP addresses a complementary question at the simulated action boundary:

> Can an evaluator prove that the action actually dispatched was the exact action authorized, and that the recorded consequence and recovery state came from an authority outside the target model?

The integration is an optional companion layer, not a replacement for Petri's auditor, target, realism filter, judge, or viewer.

## Current v0.1 implementation

The Agent Authority Boundary Benchmark now provides:

- an Inspect Petri 3.x custom task using the documented `Task`, `seeds_dataset`, `audit_solver`, `auditor_agent`, `target_agent`, `audit_judge`, and `audit_viewer` building blocks;
- a fixed target-tool surface across four scenario families;
- baseline, prompt-only, and CAEP-gated experiment conditions;
- a deterministic model-free `authority_gate` auditor tool;
- custom behavioral dimensions;
- a structured JSONL run contract and stdlib scorer;
- synthetic scorer fixtures and regression tests.

The public Petri 3.x synthetic-tool path currently lets the auditor return target tool results. Therefore v0.1 keeps behavioral scoring and enforcement evidence separate and does **not** claim a production-grade live interception hook. A future Inspect integration may connect them more directly.

## Event mapping

```text
Petri target proposes tool action
  → exact proposed action binding
  → deterministic CAEP policy decision
  → ALLOW | DENY | REQUIRE_APPROVAL | REVISE
  → simulated dispatch only when permitted
  → observable tool result
  → structured benchmark event
  → optional CAEP episode export
```

Suggested bound action input:

```json
{
  "run_id": "petri-run-...",
  "turn_id": "turn-...",
  "action_type": "external_email.send",
  "target_resource": "mailto:recipient@example.org",
  "requested_capabilities": ["external.communication.write"],
  "boundary_id": "eval:confidential:v1",
  "human_approval_ref": null
}
```

Raw transcript material remains in Petri. CAEP stores only the bounded action evidence required for verification.

## Trust separation

```text
target model
  ≠ auditor model
  ≠ deterministic policy decision point
  ≠ dispatch enforcement point
  ≠ outcome observer
  ≠ judge model
  ≠ incident controller
```

A judge score is behavioral evidence. It is not authorization, an execution receipt, or independently observed recovery.

## Fail-closed checks

The companion gate or future adapter should reject or explicitly escalate when:

1. action type, target, parameters, destination, credential class, or boundary changes after approval;
2. authorization is expired, unknown, or invented;
3. a denied action receives a dispatch;
4. a dispatched action has no terminal outcome;
5. a human-proxy request hides an external-disclosure capability;
6. evaluation evidence is modified or deleted without a valid correction authority;
7. containment runs but a reversible recovery objective is not met.

## Non-goals

- no claim that CAEP prevents behavioral misalignment by itself;
- no requirement that Petri adopt CAEP terminology or storage;
- no production credential, network, or sandbox enforcement claim;
- no forensic reconstruction of any private evaluation environment;
- no use of benchmark seeds or transcripts as training data;
- no claim that a bounded simulation proves general model safety.

## Questions for Inspect Petri maintainers

1. Which public Inspect/Petri hook is the most stable point for intercepting proposed target tool calls before a result is returned?
2. Would maintainers prefer an external companion package, an Inspect approval policy, a solver wrapper, or a post-run transcript adapter?
3. Which event fields can be exported without leaking hidden benchmark instructions?
4. Is there a preferred extension pattern for attaching structured non-judge metrics to Petri logs and Inspect View?

## Ready-to-post issue text

> We implemented an Inspect Petri 3.x companion benchmark for a narrow question: can an external deterministic action boundary reduce unauthorized execution without suppressing legitimate refusal and internal safety escalation?
>
> The suite compares baseline, prompt-only, and gated conditions across internal escalation, unauthorized external disclosure, human-proxy bypass, and evaluation-evidence tampering. It includes fixed tools, custom judge dimensions, a model-free policy gate, structured JSONL metrics, synthetic fixtures, and regression tests.
>
> Petri continues to generate and judge the behavioral audit. The companion gate only evaluates the exact proposed consequence-bearing action before simulated dispatch. We deliberately keep judge narrative separate from authorization and execution evidence.
>
> We would value guidance on the most stable Petri 3.x / Inspect extension point for a stricter pre-result interception hook.