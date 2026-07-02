# Guarded GitHub Merge Execution

**Status:** Experimental reference enforcement slice  
**Action:** `merge_pull_request`  
**Protocol:** [Action Envelope V1](ACTION-ENVELOPE-V1.md)  
**Evaluator:** [GitHub Pull Request Merge Gate v0.1](GITHUB-PR-MERGE-GATE.md)

## Purpose

The snapshot adapter proves that a proposed merge is eligible for `ALLOW`,
but an evaluator alone does not prevent a caller from invoking a merge too early
or more than once.

`adapters/guarded_github_merge.py` adds the executable boundary:

```text
load current GitHub head
  -> reject missing required evidence
  -> evaluate Action Envelope V1
  -> reserve semantic idempotency key
  -> load current GitHub head again
  -> call injected merge executor only after ALLOW
  -> record SUCCEEDED or FAILED
```

The merge executor is unreachable when the decision is `BLOCK` or `ESCALATE`.

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

## Missing evidence

The lower-level snapshot adapter represents absent checks or reviews as
unresolved preconditions. The guarded execution service is stricter: a required
check or required review that is absent is a known unsafe execution state and
returns:

```text
BLOCK / REQUIRED_EVIDENCE_MISSING
```

External-state failures remain:

```text
ESCALATE / CURRENT_STATE_UNAVAILABLE
```

## Replay protection

The reference in-memory store exposes four states:

```text
NEW -> IN_PROGRESS -> SUCCEEDED | FAILED
```

A semantic idempotency key can be reserved once. A second attempt is blocked
with `ACTION_ALREADY_IN_PROGRESS` or `ACTION_ALREADY_EXECUTED`, and tests assert
that the executor call count remains one.

This store is deliberately process-local. Durable atomic replay storage and
distributed coordination belong to the LiminalDB follow-up.

## Interfaces

The orchestration depends on two injected boundaries:

- `CurrentPullRequestStateProvider.get_head_sha(...)`;
- `MergeExecutor.merge_pull_request(..., expected_head_sha)`.

Tests use fakes to prove call ordering and executor reachability. A production
GitHub client, credentials, webhook handling, and branch-protection integration
remain outside this PR.

## Covered scenarios

- valid exact-head action executes once;
- initial head mismatch blocks;
- missing required check blocks;
- missing required review blocks;
- old-head CI evidence blocks;
- head drift between evaluation and execution blocks;
- replay after success blocks;
- concurrent in-progress action blocks;
- GitHub state unavailability escalates;
- executor failure is recorded as failed and never reported as success.

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
