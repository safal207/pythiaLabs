# Agent Action Audit Snapshot — Example v0.1

> One-page sample output for a bounded, redacted AI-agent workflow. This is an example artifact for reviewers, not a certification, compliance report, or replacement for sandboxing, evals, code review, or runtime security controls.

## 1. Workflow under review

**Workflow name:** CI workflow change suggested by an AI coding agent

**Scenario:**

An AI coding agent proposes a pull request change to `.github/workflows/build.yml` after observing a failing JavaScript formatting check. The proposed change modifies CI behavior so the formatting step is skipped on documentation-only pull requests.

**High-impact action category:**

- Repository workflow / CI configuration change
- Could affect future automated checks
- Could reduce reviewer visibility if applied too broadly

**Provided input:**

```text
Redacted PR summary
Redacted diff excerpt
CI failure summary
Repository policy notes
Requested action description
```

**Not provided / intentionally excluded:**

```text
Private customer data
Secrets or tokens
Production logs
Private repository content beyond the redacted workflow shape
```

## 2. Snapshot decision

**Decision:** `ESCALATE`

**Why not ALLOW?**

The agent identified a real CI friction point, but the proposed workflow change could alter future validation behavior. The evidence is not enough to safely allow the change without a human reviewer confirming scope and policy alignment.

**Why not BLOCK?**

The action is not clearly malicious or invalid. It may be acceptable if narrowed to a safe condition and reviewed by the repository owner.

## 3. Evidence checked

| Evidence item | Status | Notes |
|---|---:|---|
| Triggering task is present | Checked | The agent was asked to diagnose a formatting failure. |
| Proposed action is described | Checked | The action modifies a CI workflow file. |
| Action owner / reviewer is identified | Missing | No explicit repository owner approval was attached. |
| Scope of change is bounded | Partial | The change says “documentation-only PRs,” but matching rules need review. |
| Failure context is linked | Checked | CI failure summary was provided. |
| Existing policy is referenced | Partial | Repository policy notes were provided, but not enough to confirm safe skip rules. |
| Rollback path is described | Missing | No rollback or monitoring note was included. |

## 4. Stop reasons

```text
ESCALATE_REQUIRES_OWNER_REVIEW
ESCALATE_POLICY_SCOPE_NOT_PROVEN
ESCALATE_CI_BEHAVIOR_CHANGE
ESCALATE_ROLLBACK_NOT_SPECIFIED
```

## 5. Reviewer-facing explanation

The proposed change touches a workflow that can affect future PR validation. Even if the immediate task is legitimate, the decision should not be based only on the agent’s final diff.

A reviewer should confirm:

1. whether documentation-only PR detection is reliable,
2. whether formatting checks may safely be skipped in that path,
3. whether the change affects only the intended job or also broader CI behavior,
4. who owns approval for CI workflow changes,
5. how the change can be reverted if it causes missed checks.

## 6. Recommended controls before approval

| Control | Purpose |
|---|---|
| Require repository owner approval for CI workflow changes | Avoid silent CI policy drift. |
| Add a test fixture for documentation-only detection | Prevent overly broad skip conditions. |
| Keep the formatting job visible but mark it conditional | Preserve reviewer visibility. |
| Add a rollback note to the PR | Make recovery explicit. |
| Record the agent action decision in a trace | Make the decision replayable. |

## 7. Minimal decision record

```json
{
  "snapshot_version": "0.1",
  "workflow_type": "ai_coding_agent_ci_change",
  "action_type": "modify_ci_workflow",
  "decision": "ESCALATE",
  "stop_reasons": [
    "ESCALATE_REQUIRES_OWNER_REVIEW",
    "ESCALATE_POLICY_SCOPE_NOT_PROVEN",
    "ESCALATE_CI_BEHAVIOR_CHANGE",
    "ESCALATE_ROLLBACK_NOT_SPECIFIED"
  ],
  "evidence_checked": [
    "triggering_task",
    "proposed_action",
    "ci_failure_summary",
    "redacted_diff_excerpt",
    "repository_policy_notes"
  ],
  "missing_evidence": [
    "explicit_owner_approval",
    "bounded_skip_rule_proof",
    "rollback_plan"
  ],
  "sensitive_data_requested": false
}
```

## 8. Limitations

This snapshot does not prove that the proposed code is correct, secure, or complete. It does not simulate CI behavior, inspect private repository history, verify identity, or replace maintainers’ review process.

It only answers a narrower reviewer question:

```text
Before this AI-agent action proceeds, is the evidence sufficient to allow it, block it, or escalate it?
```

## 9. Follow-up request to a target team

If this example is useful, the next step is one bounded, non-sensitive workflow shape from your environment.

Useful examples include:

- AI reviewer suggests a PR change,
- agent proposes a config update,
- CI/autofix agent changes a workflow file,
- agent proposes a high-impact tool action.

No private logs, credentials, secrets, customer data, or production data are needed. A redacted workflow description is enough.
