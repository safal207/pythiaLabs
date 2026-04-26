# Threat Model — Web3 Treasury Reason Layer

This document describes deterministic, pre-execution threats for the current PythiaLabs Web3 treasury reasoning demos.

> Scope note: this is a documentation threat model for local deterministic demos, not a claim of production smart-contract, wallet, RPC, or cryptographic security.

## Threat table

| Threat | Example | Current mitigation | Remaining gap | Future work |
|---|---|---|---|---|
| unauthorized agent action | An automated agent proposes a transfer without valid permission context. | Deterministic authorization checks in showcase pipelines produce explicit deny with traceable stop reason. | Authorization model is demo-scoped and not integrated with live identity/role systems. | Add richer policy adapters and formal authorization source mapping for real governance environments. |
| quorum bypass | Transfer is marked as passed despite insufficient votes. | Quorum gate is explicitly evaluated before allow decision in treasury showcase logic. | Demo inputs are local and trusted; no adversarial vote data source is modeled. | Add adversarial fixtures and independent vote-source reconciliation rules. |
| voting window bypass | Action is accepted after voting end or before voting start. | Deterministic voting-window checks enforce temporal constraints. | Local clock/input assumptions may not reflect distributed or delayed event ingestion. | Add clock-skew modeling, ingestion-latency scenarios, and stricter temporal validation boundaries. |
| timelock bypass | Proposal executes before required timelock delay elapses. | Timelock check is included as a mandatory gate with explicit reject reason. | Timelock proof source is simulated; no chain-derived evidence in MVP. | Define verifiable timelock evidence interface for future integrations. |
| authorization expired | Permission existed historically but expired before action time. | Bitemporal logic evaluates validity interval at action_time. | Demo does not integrate revocation registries or external attestation feeds. | Add revocation event modeling and external attestation adapters. |
| authorization valid but unknown at decision time | Permission was valid at action_time but not yet known by decision_time. | Decision-time knowledge checks deny or flag based on temporal knowledge boundary. | No distributed knowledge synchronization model in local demo. | Add event-ordering, ingestion delay, and eventual-consistency simulation suite. |
| evidence payload tampering | Trace/evidence JSON is altered after generation to hide a failed check. | Deterministic evidence artifact flow includes hash-based integrity demonstration and local verification scripts. | Demonstration is local and not a production cryptographic attestation framework. | Add stronger envelope integrity specification and independent verifier implementations. |
| signature field injection | Extra fields are inserted into a signature structure to mislead verifiers. | Envelope format is shape-validated in demo flows and tests. | Canonicalization and strict signed-field policies are limited in MVP docs/demo. | Define canonical field ordering and strict allowlist/denylist signature schema rules. |
| hidden envelope fields | A malicious producer includes hidden/ignored fields that alter interpretation downstream. | Deterministic envelope handling illustrates expected fields and validation steps. | Unknown-field rejection is not yet formalized as a strict interoperability profile. | Introduce strict schema mode with explicit unknown-field rejection and compatibility levels. |
| stale/replay action | Previously approved action is replayed later under changed governance conditions. | Temporal checks and transfer expiration logic reduce stale approvals in demos. | No global nonce/replay database in current local-only architecture. | Add replay-protection identifiers and persistent anti-replay ledger interfaces. |
| malformed evidence envelope | Evidence bundle is structurally invalid or missing required components. | Deterministic validation path rejects malformed inputs with explicit stop reasons. | Validation profile is evolving and not yet standardized across external tools. | Publish versioned envelope schema and conformance test vectors. |

## Implementation posture
- Current posture is deterministic safety reasoning for demonstrations and testing.
- The system is intentionally local-first to keep audits reproducible during MVP.
- Production cryptography, on-chain enforcement, and live signer infrastructure are out of current scope.
