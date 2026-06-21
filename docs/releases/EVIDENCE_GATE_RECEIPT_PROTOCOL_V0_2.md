# Evidence Gate Receipt Protocol v0.2

Released to `main` on 2026-06-21 via PR #200.

## What changed

- Added `EvidenceGateDecisionEvent` v0.2 with shared `receipt_id` and `verification_required`.
- Preserved the v0.1 decision schema as a compatibility snapshot.
- Added append-only `EvidenceGateVerificationEvent` for post-action checks.
- Added reviewer-facing `EvidenceGateReceipt` projection.
- Added linked JSON examples for decision, verification, and receipt.
- Expanded the OpenHands interoperability mapping and non-claims.

## Protocol flow

```text
pre-action decision
-> action / observation
-> post-action verification
-> reviewer receipt projection
```

The original authorization record is not mutated after dispatch.

## Scope

This is an experimental interoperability proposal. It is not an OpenHands feature or endorsement, and it does not claim production authorization, cryptographic assurance, security certification, or compliance.
