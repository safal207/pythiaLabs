# Agent Infrastructure Action Safety Showcase — Expected Output

This guide describes the expected output sections for:

```bash
mix run examples/agent_infra_action_showcase.exs
```

The showcase is deterministic and local. It demonstrates decision-time replay / pre-execution reasoning and does not implement production infrastructure controls.

## Header

Expected top lines include:

- `Production Volume Deletion Safety Showcase`
- A disclaimer that this is deterministic local reasoning only

## Scenario Sections and Expected Stop Reasons

The script prints these sections in order:

1. `A. Rejected destructive production volume delete: missing explicit approval`
   - expected `status: rejected`
   - expected `stop_reason: destructive_action_requires_explicit_approval`

2. `B. Rejected destructive production volume delete: credential scope too broad`
   - expected `status: rejected`
   - expected `stop_reason: credential_scope_too_broad`

3. `C. Rejected destructive production volume delete: backup not isolated from target`
   - expected `status: rejected`
   - expected `stop_reason: backup_not_isolated_from_target`

4. `D. Rejected destructive production volume delete: documentation not verified`
   - expected `status: rejected`
   - expected `stop_reason: documentation_not_verified`

5. `E. Accepted non-production action with safe scoped credentials and approval`
   - expected `status: accepted`
   - expected `stop_reason: agent_infra_action_accepted`

6. `F. Evidence export`
   - expected `export_status: accepted`
   - expected `export_stop_reason: agent_infra_action_accepted`

7. `G. Evidence digest`
   - expected `algorithm: sha256`
   - expected digest as lowercase 64-char hex

8. `H. Evidence verification`
   - expected `verification_status: verified`

9. `I. Tampered evidence rejection`
   - expected `verification_status: rejected`
   - expected `reason: digest_mismatch`

## Notes for Reviewers

- Stop reasons are stable and deterministic for each scenario.
- Evidence verification is fail-closed for malformed or tampered evidence.
- The showcase does not claim cloud-provider integration, IAM enforcement, backup management, or cybersecurity protection.
