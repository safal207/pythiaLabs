# Guarded GitHub Merge Execution

**Status:** Experimental reference enforcement slice  
**Action:** `merge_pull_request`  
**Protocol:** [Action Envelope V1](ACTION-ENVELOPE-V1.md)  
**Evaluator:** [GitHub Pull Request Merge Gate v0.1](GITHUB-PR-MERGE-GATE.md)

## Purpose

The snapshot adapter proves that a proposed merge is eligible for `ALLOW`, but
an evaluator alone does not prevent a caller from invoking a merge too early,
with backdated freshness inputs, or more than once.

`adapters/guarded_github_merge.py` adds the executable boundary:

```text
validate snapshot
  -> reject missing or cross-target evidence
  -> obtain trusted decision time
  -> load current GitHub head
  -> evaluate Action Envelope V1
  -> atomically reserve semantic idempotency key
  -> load current GitHub head again
  -> call injected merge executor only after ALLOW
  -> record SUCCEEDED or FAILED
```

Every rejection before the executor call returns:

```text
executor_called = false
execution_status = NOT_ATTEMPTED
```

`BLOCK / EXECUTION_FAILED` is different: the gate allowed the action, the
executor boundary was reached, and the executor failed. That outcome returns
`executor_called = true` and `execution_status = FAILED`.

## Trusted decision time

The effective `decision_time` is supplied by an injected trusted clock. The
caller-provided value in the snapshot is overwritten before authorization and
evidence-freshness evaluation.

This prevents a caller from backdating the decision to make expired evidence
appear fresh. If trusted time cannot be obtained, the service returns:

```text
ESCALATE / TRUSTED_TIME_UNAVAILABLE
```

The executor is not called.

## Exact-head invariant

The current head is checked twice:

1. before gate evaluation;
2. immediately before the executor call.

If the first head differs from the proposed head, execution returns:

```text
BLOCK / HEAD_SHA_MISMATCH
```

If the head changes after evaluation but before execution, it returns:

```text
BLOCK / TARGET_CHANGED_BEFORE_EXECUTION
```

In both cases the merge executor is not called.

The executor interface also receives `expected_head_sha`. A production GitHub
implementation must pass that value to GitHub's conditional merge operation so
GitHub itself rejects a moved head.

## Evidence binding

A required check or review that is absent is a known unsafe execution state:

```text
BLOCK / REQUIRED_EVIDENCE_MISSING
```

Workflow locators must belong to the proposed repository. Review locators must
belong to the proposed repository and pull request. Cross-target locators return:

```text
BLOCK / EVIDENCE_TARGET_MISMATCH
```

The existing Action Envelope evaluator separately checks exact-head binding,
action binding, freshness, successful result, and authorization.

## Replay protection

The reference in-memory store exposes four states:

```text
NEW -> IN_PROGRESS -> SUCCEEDED | FAILED
```

A semantic idempotency key can be reserved once. Reservation is protected by a
lock so `NEW -> IN_PROGRESS` is atomic within the reference process. A repeated
attempt is blocked with `ACTION_ALREADY_IN_PROGRESS` or
`ACTION_ALREADY_EXECUTED`.

This store is deliberately process-local. Durable atomic replay storage and
distributed coordination belong to the LiminalDB follow-up.

## Interfaces

The orchestration depends on three injected boundaries:

- `DecisionClock.now()`;
- `CurrentPullRequestStateProvider.get_head_sha(...)`;
- `MergeExecutor.merge_pull_request(..., expected_head_sha)`.

Tests use fakes to prove call ordering, freshness behavior, and executor
reachability. A production GitHub client, credentials, webhook handling, and
branch-protection integration remain outside this PR.

## Covered scenarios

- valid exact-head action executes once;
- initial head mismatch blocks;
- missing required check or review blocks;
- foreign reviewer does not replace a required reviewer;
- cross-repository workflow evidence blocks;
- review evidence for another pull request blocks;
- a backdated snapshot cannot revive stale evidence;
- trusted-clock failure escalates before external state lookup;
- old-head CI evidence blocks;
- head drift between evaluation and execution blocks;
- replay after success blocks;
- concurrent in-progress action blocks;
- GitHub state unavailability escalates;
- executor failure is recorded as an attempted but failed execution.

## Non-claims

This reference slice does not provide:

- a live GitHub API client;
- production credentials or webhook authentication;
- distributed locking;
- durable replay storage;
- post-merge verification;
- compensation or automatic revert execution.

It demonstrates the safety property required before those integrations:

> A merge implementation is reachable only after fresh exact-head evidence is
> allowed, the semantic action is reserved, and the target is revalidated.
