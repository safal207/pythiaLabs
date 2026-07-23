# Lotus Family audit result codes

| Outcome | Reason code | Meaning |
|---|---|---|
| `PASS` | `LOTUS_CONTRACT_CONFORMANT` | Every configured invariant passed for the supplied snapshot and caller-provided identity claims. |
| `DRIFT` | `LOTUS_CONTRACT_DRIFT` | A required contract, test, or executable CI discovery invariant is missing. |
| `UNKNOWN` | `SNAPSHOT_UNAVAILABLE` | The repository snapshot is unavailable. |
| `UNKNOWN` | `COMMIT_SHA_INVALID` | The supplied commit claim is not a lowercase 40-character SHA. |
| `UNKNOWN` | `REPOSITORY_REF_MISSING` | The repository ref claim was not supplied. |
| `UNKNOWN` | `REPOSITORY_NOT_CONFIGURED` | No manifest adapter exists for the repository ID. |
| `UNKNOWN` | `MANIFEST_INVALID` | The manifest cannot be parsed or violates the audit-only boundary. |

Consumers must branch on `outcome` and `reason_code`, not on human-readable detail.
A `PASS` does not verify remote provenance and grants no ownership, approval,
execution, delivery, deployment, or merge authority.
