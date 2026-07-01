# GitHub Pull Request Merge Gate v0.1

**Status:** Experimental reference adapter  
**Action:** `merge_pull_request`  
**Protocol:** [Action Envelope V1](ACTION-ENVELOPE-V1.md)

## Purpose

This adapter turns a bounded GitHub pull-request snapshot into an
`ActionEnvelopeV1` before merge execution.

It answers one narrow question:

```text
May this exact pull-request head be merged under the supplied authorization,
checks, reviews, freshness windows, replay state, and recovery evidence?
```

The adapter does not call GitHub and does not merge anything. It only constructs
and evaluates the pre-execution contract.

## Exact-head invariant

The expected pull-request head SHA is included in all of:

- the deterministic action identity;
- the requested target;
- the authorization target;
- the idempotency key;
- the expected state transition;
- every required check and review comparison.

A successful CI run or review attached to another head is not accepted as proof
for the proposed merge.

## Decision flow

```text
strict GitHub snapshot validation
  -> canonical action_id(repository, PR, operation, expected head)
  -> observed head == expected head
  -> PR mergeability known and true
  -> every required check present, successful, fresh, exact-head bound
  -> every required review present, approved, fresh, exact-head bound
  -> Action Envelope authorization binding
  -> Action Envelope replay and recovery checks
  -> ALLOW / BLOCK / ESCALATE
```

## Input and implementation

- [`schema/github-pr-merge-gate-input.schema.json`](schema/github-pr-merge-gate-input.schema.json)
  defines the strict input snapshot;
- [`examples/github-pr-merge-gate-input.example.json`](examples/github-pr-merge-gate-input.example.json)
  provides a complete example;
- [`adapters/github_pr_merge_gate.py`](adapters/github_pr_merge_gate.py)
  constructs and evaluates the Action Envelope;
- [`conformance/test_github_pr_merge_gate.py`](conformance/test_github_pr_merge_gate.py)
  covers exact-head drift, missing evidence, stale evidence, replay, recovery, and
  authorization mismatch.

## Outcome interpretation

- `ALLOW / ALLOW_OK` means every declared check in this bounded adapter and the
  Action Envelope evaluator passed.
- `BLOCK / GITHUB_INPUT_INVALID` means the supplied GitHub snapshot is malformed
  or semantically ambiguous, such as duplicate check names.
- `BLOCK / PRECONDITION_FAILED` means a deterministic merge condition failed,
  including head drift, failed checks, stale-head checks, requested changes, or
  stale-head reviews.
- `ESCALATE / PRECONDITION_UNRESOLVED` means required evidence is absent or a
  state such as mergeability remains unknown.

## Relationship to other PythiaLabs surfaces

- **Action Envelope V1** is the action authorization contract used by this
  adapter.
- **Evidence Gate Receipt Protocol v0.2** can project the resulting decision and
  later verification as append-only reviewer receipts. This adapter does not
  replace that protocol.
- **Verifiable Continuation Envelope** preserves operational continuity across
  restart or handoff. It does not authorize the merge.

## Non-claims

This adapter is not:

- a GitHub App or GitHub API client;
- a branch-protection replacement;
- a production merge queue;
- a guarantee that reviewed code is correct or secure;
- durable replay storage;
- cryptographic reviewer identity verification;
- post-merge verification;
- a compliance or security certification.

The caller remains responsible for independently retrieving GitHub state,
verifying reviewer identity, storing replay keys atomically, enforcing the
returned decision, and confirming the post-merge result.
