# Agent Action Workflow Intake Template

> Use this template to share one bounded, redacted workflow shape for an Agent Action Audit Snapshot. Do not include secrets, credentials, customer data, production logs, private source code, or sensitive internal details.

## 1. Workflow identity

**Workflow name:**

```text
Example: AI coding agent proposes a CI workflow change
```

**Organization / product context:**

```text
Example: AI code review platform, developer tooling, CI/autofix workflow, internal tool-calling agent
```

**Agent type:**

```text
Example: coding agent, PR review agent, CI autofix agent, support agent, internal automation agent
```

## 2. High-impact action

**Proposed action:**

```text
Example: modify a CI workflow file, open a PR, run a shell command, update a config, call an external API
```

**Why this action matters:**

```text
Example: could affect future checks, modify repository behavior, trigger deployment-adjacent workflow, expose data, or require owner approval
```

**Action category:**

- [ ] Code change
- [ ] Shell command
- [ ] CI / workflow change
- [ ] Config change
- [ ] Browser action
- [ ] External API / tool call
- [ ] Repository / PR action
- [ ] Data access
- [ ] Other: `...`

## 3. Triggering task

**What triggered the agent action?**

```text
Example: failing CI check, user request, incident response task, stale dependency, support ticket, reviewer request
```

**Who or what requested the action?**

```text
Example: user, maintainer, automated workflow, support operator, CI system, scheduled job
```

## 4. Evidence available before action

List only redacted, non-sensitive evidence.

| Evidence item | Available? | Notes |
|---|---:|---|
| Triggering task description | Yes / No | ... |
| Proposed action summary | Yes / No | ... |
| Redacted diff / command / tool call preview | Yes / No | ... |
| Policy or rule reference | Yes / No | ... |
| Owner / reviewer approval | Yes / No | ... |
| Rollback or recovery plan | Yes / No | ... |
| Prior failure context | Yes / No | ... |
| Environment / scope boundary | Yes / No | ... |

## 5. Expected gate behavior

**When should the action be ALLOW?**

```text
Example: when the action is low-impact, scoped, authorized, and has sufficient evidence and rollback path
```

**When should the action be BLOCK?**

```text
Example: when authorization is missing, the action is out of scope, evidence contradicts the request, or sensitive data would be exposed
```

**When should the action be ESCALATE?**

```text
Example: when the action may be valid but requires owner review, policy confirmation, or additional evidence
```

## 6. Stop reasons you would expect

Select or add relevant stop reasons.

- [ ] `BLOCK_AUTHORIZATION_MISSING`
- [ ] `BLOCK_SCOPE_MISMATCH`
- [ ] `BLOCK_SENSITIVE_DATA_RISK`
- [ ] `BLOCK_UNSAFE_TOOL_CALL`
- [ ] `ESCALATE_OWNER_REVIEW_REQUIRED`
- [ ] `ESCALATE_POLICY_SCOPE_NOT_PROVEN`
- [ ] `ESCALATE_HIGH_IMPACT_ACTION`
- [ ] `ESCALATE_ROLLBACK_NOT_SPECIFIED`
- [ ] Other: `...`

## 7. Data that must stay excluded

Confirm exclusions.

- [ ] No secrets or tokens
- [ ] No private customer data
- [ ] No production logs
- [ ] No private source code beyond a redacted shape
- [ ] No personal data
- [ ] No internal incident details
- [ ] No credentials or access keys

Additional exclusions:

```text
...
```

## 8. Desired output format

What would be most useful for reviewers?

- [ ] One-page markdown snapshot
- [ ] JSON decision record
- [ ] Trace / event log excerpt
- [ ] Reviewer checklist
- [ ] GitHub PR comment format
- [ ] CI artifact format
- [ ] Other: `...`

## 9. Success criteria

A useful snapshot should help reviewers answer:

```text
Before this AI-agent action proceeds, is the available evidence sufficient to allow it, block it, or escalate it?
```

**What would make the snapshot useful for your team?**

```text
...
```

**What would make it not useful?**

```text
...
```

## 10. Contact / follow-up preference

**Preferred follow-up format:**

- [ ] GitHub comment
- [ ] Email
- [ ] Short call
- [ ] Async notes only
- [ ] Other: `...`

**Any timing constraints?**

```text
...
```
