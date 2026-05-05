# Expected output: Paid review demo

Run:

```bash
make demo
```

Expected reviewer-facing terminal output:

```text
PythiaLabs Demo: Web3 treasury action

Proposed action:
  transfer_25000_usdc

Checks:
  authorization ........ PASS
  wallet_allowlist ..... PASS
  quorum_approval ...... FAIL
  policy_freshness ..... FAIL
  action_risk .......... REVIEW

Decision:
  ESCALATE

Execution allowed:
  false

Stop reason:
  missing_quorum_approval_and_stale_policy_state

Artifact:
  examples/output/paid_review_demo_artifact.json

Result:
  PASS — expected ESCALATE, got ESCALATE
```
