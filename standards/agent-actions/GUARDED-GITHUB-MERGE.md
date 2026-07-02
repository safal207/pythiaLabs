# Guarded GitHub Merge Execution

**Status:** Experimental reference enforcement slice  
**Action:** `merge_pull_request`  
**Protocol:** [Action Envelope V1](ACTION-ENVELOPE-V1.md)  
**Evaluator:** [GitHub Pull Request Merge Gate v0.1](GITHUB-PR-MERGE-GATE.md)

## Purpose

`adapters/guarded_github_merge.py` adds an executable boundary around the merge
gate:

```text
validate snapshot
  -> reject missing or cross-target evidence
  -> obtain trusted decision time
  -> load current GitHub head and base
  -> evaluate Action Envelope V1
  -> atomically reserve semantic idempotency key
  -> load current GitHub head and base again
  -> call injected merge executor only after ALLOW
  -> record SUCCEEDED or FAILED
```

Every rejection before the executor call returns `executor_called=false` and
`execution_status=NOT_ATTEMPTED`. Executor failure is distinct: the boundary was
reached, so it returns `executor_called=true` and `execution_status=FAILED`.

## Trusted decision time

The effective `decision_time` comes from an injected trusted clock. The
caller-provided value is overwritten before authorization and evidence
freshness evaluation. Clock failure returns
`ESCALATE / TRUSTED_TIME_UNAVAILABLE` without reaching GitHub state or executor.

## Exact-target invariant

The current head SHA and base ref are checked twice:

1. before gate evaluation;
2. immediately before the executor call.

Initial mismatches return `HEAD_SHA_MISMATCH` or `BASE_REF_MISMATCH`.
Changes after `ALLOW` return `TARGET_CHANGED_BEFORE_EXECUTION` or
`BASE_CHANGED_BEFORE_EXECUTION`. The executor receives both expected values.

A production implementation must use GitHub's conditional head-SHA merge guard
and independently revalidate the base ref before issuing the side effect.

## Evidence binding

Missing required checks or reviewers return `REQUIRED_EVIDENCE_MISSING`.
Workflow and review locators must belong to the exact repository and pull
request. Cross-target locators return `EVIDENCE_TARGET_MISMATCH` before external
state lookup.

## Replay and retry semantics

The reference store exposes:

```text
NEW -> IN_PROGRESS -> SUCCEEDED | FAILED
          |
          +-> NEW  (release before executor reachability)
```

Reservation is atomic within the process. A transient failure during the second
GitHub state read occurs before executor reachability, so the reservation is
released back to `NEW`; a later retry may proceed. Target drift and executor
failure are terminal for that semantic action.

An allowed lower-layer result that lacks the required idempotency key is an
internal contract violation and returns `GITHUB_ENVELOPE_INVALID`, not
`GITHUB_INPUT_INVALID`.

## Interfaces

The orchestration depends on:

- `DecisionClock.now()`;
- `CurrentPullRequestStateProvider.get_state(...)` returning head and base;
- `MergeExecutor.merge_pull_request(..., expected_head_sha, expected_base_ref)`;
- `ExecutionStateStore` with reserve, release, success, and failure transitions.

## Covered scenarios

- valid exact-target action executes once;
- initial head or base mismatch blocks;
- missing or cross-target evidence blocks;
- stale evidence and backdating block;
- head or base drift after `ALLOW` blocks;
- transient second-read outage releases the reservation and permits retry;
- replay and concurrent execution block;
- malformed internal allowed-envelope state blocks with a dedicated code;
- executor failure is terminal and reported as attempted.

## Non-claims

This reference slice does not provide a live GitHub client, production
credentials, distributed locking, durable replay storage, post-merge
verification, compensation, or automatic revert execution.

> A merge implementation is reachable only after fresh exact-target evidence is
> allowed, the semantic action is reserved, and both base and head are
> revalidated.
