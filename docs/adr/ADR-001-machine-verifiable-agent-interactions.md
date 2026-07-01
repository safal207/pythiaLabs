# ADR-001: Critical Agent Interactions Must Be Machine-Verifiable

- **Status:** Proposed
- **Date:** 2026-07-01
- **Decision owners:** PythiaLabs maintainers
- **Related market signal:** [`../market_signals/VINT_CERF_AGENT_PROTOCOLS.md`](../market_signals/VINT_CERF_AGENT_PROTOCOLS.md)

## Context

AI agents increasingly propose or perform actions with external side effects: infrastructure changes, financial operations, governance decisions, code modifications, messages, and tool calls.

Natural-language instructions and model-generated explanations are not reliable execution contracts. They can be ambiguous, incomplete, stale, or inconsistent across agents and frameworks. A reviewer also cannot safely infer authorization, evidence freshness, or recovery readiness from prose alone.

PythiaLabs therefore needs a stable architectural rule that applies across its action gates, demos, protocol experiments, and framework adapters.

## Decision

Every critical agent interaction evaluated by PythiaLabs must be representable as a versioned, machine-verifiable action contract.

At minimum, the contract should be able to express:

- protocol or schema version;
- action identifier;
- actor and agent identity;
- requested capability and operation;
- target resource and environment;
- authorization or delegation context;
- required preconditions;
- evidence references, provenance, and freshness;
- expected state transition;
- idempotency or replay-protection data;
- recovery or rollback declaration;
- deterministic decision outcome;
- stable stop reasons;
- generated audit-artifact references.

Free-form natural language may accompany the contract, but it must not replace the fields required to make the critical decision.

## Decision flow

```text
Proposed action
    -> schema validation
    -> identity and capability checks
    -> authorization checks
    -> precondition and environment checks
    -> evidence validation
    -> recovery-context checks
    -> ALLOW / BLOCK / ESCALATE
    -> replayable audit artifact
```

## Consequences

### Positive

- Decisions can be reproduced without trusting an agent's narrative.
- Different framework adapters can converge on one semantic contract.
- Stop reasons remain stable enough for testing and audit.
- Stale, missing, or mismatched evidence can fail closed.
- Idempotency and replay protection can become explicit rather than implicit.
- Reviewers can inspect artifacts independently of terminal output.

### Costs and trade-offs

- Schema evolution and compatibility rules must be maintained.
- Integrations need translation layers from framework-native tool calls.
- Some actions will require domain-specific extensions.
- Strict validation may reject underspecified actions that a human would understand.
- A machine-verifiable contract does not by itself provide production security, trustworthy identity, regulatory compliance, or correct policy design.

## Initial conformance target

A first conformance suite should verify that:

1. unknown schema versions are rejected;
2. required identity and action fields are present;
3. malformed authorization context is rejected;
4. evidence is bound to the intended action;
5. stale evidence is rejected where freshness is required;
6. duplicate action identifiers are detected where replay protection applies;
7. unreachable or undeclared state transitions are rejected;
8. `ALLOW`, `BLOCK`, and `ESCALATE` produce stable reason codes;
9. the emitted artifact can be independently verified;
10. adapters do not silently discard required fields.

## Non-goals

This ADR does not claim that PythiaLabs currently provides:

- a universal inter-agent standard;
- production-grade identity or cryptography;
- cloud, wallet, or banking enforcement;
- regulatory certification;
- safe autonomous execution without human governance;
- compatibility with every agent framework.

## Follow-up work

- Define a minimal `ActionEnvelopeV1` schema.
- Define stable decision and stop-reason registries.
- Add conformance fixtures for valid, invalid, stale, replayed, and mismatched actions.
- Map the current showcases to the envelope fields.
- Document extension points for domain-specific evidence.
- Add one framework adapter that preserves the full contract.
- Keep public claims aligned with [`../NON_CLAIMS.md`](../NON_CLAIMS.md).
