# PythiaLabs Threat Model

This document is the public threat model for PythiaLabs, the pre-execution
evidence gate for AI-agent actions. It is intended for grant reviewers,
security researchers, and design partners who need to evaluate where the
gate sits in the trust boundary and what it does and does not protect
against.

## Scope

PythiaLabs evaluates a **proposed agent action** before any tool executes.
Inputs are the action description, decision-time evidence, and gate
configuration. Outputs are a deterministic `ALLOW / BLOCK / ESCALATE`
decision plus a reviewable evidence artifact.

In scope:

- AI agents that can call tools touching code, infrastructure, money,
  or governance.
- Pre-execution decisions where the gate is the last reviewable step
  before a tool runs.
- Evidence artifacts shared with human reviewers, CI, or compliance.

Out of scope:

- Post-hoc log analysis only (PythiaLabs is pre-execution, not forensic).
- Model-level alignment, prompt-injection defense inside the model, or
  fine-tuning safety.
- Network, OS, or container hardening of the host where the agent runs.

## Trust boundaries

```
[ user / orchestrator ]
        │
        ▼
[ AI agent / planner ]
        │  proposed action + evidence
        ▼
[ PythiaLabs gate ]  ◄── decision-time evidence
        │  ALLOW / BLOCK / ESCALATE + artifact
        ▼
[ tool executor / external system ]
```

The gate trusts:

- Its own configuration and policy code.
- Decision-time evidence collected through declared collectors.
- The integrity of the artifact it emits.

The gate does **not** trust:

- The agent's natural-language rationale alone.
- Stale evidence pulled from caches without freshness checks.
- Tool side effects after a decision is made (out of scope).

## Assets

| Asset | Why it matters |
| --- | --- |
| Decision artifact (JSON) | Reviewer-facing evidence; integrity is critical. |
| Gate policy code | Determines ALLOW / BLOCK / ESCALATE outcomes. |
| Evidence collectors | Source of truth at decision time. |
| Action schema | Defines what the gate can reason about. |

## Adversaries and motivations

1. **Malicious user.** Tries to coerce the agent into executing a tool
   call that bypasses authorization, exfiltrates data, or moves funds.
2. **Compromised upstream component.** A tampered planner or tool
   adapter feeds the gate misleading inputs.
3. **Insider with policy access.** An operator with commit access to
   gate policy could weaken checks.
4. **Stale-state attacker.** Relies on evidence that was true earlier
   but is no longer true at decision time (replay-like behavior at
   the evidence layer).

## Top threats

### T1 — Prompt-injected tool call

An attacker injects content (via web data, document, message) that
causes the agent to propose a high-impact tool call.

- **Mitigation.** The gate evaluates the proposed action against
  authorization, blast-radius, and evidence checks regardless of how
  the agent decided. Decisions are deterministic over evidence, not
  over agent rationale.
- **Residual risk.** If the action falsely passes all required
  evidence (e.g. attacker also controls evidence source), it can be
  ALLOWed. Mitigation: independent evidence sources, ESCALATE on
  insufficient corroboration.

### T2 — Stale evidence

Authorization, balances, quorum, or policy state has changed since
the evidence was last fetched.

- **Mitigation.** Evidence has freshness requirements and decision
  time is included in the artifact. Stale evidence triggers
  ESCALATE or BLOCK with a `stop_reason`.
- **Residual risk.** Misconfigured freshness windows. Tracked via
  config review and reproducible runs.

### T3 — Blast-radius underestimation

An action that looks bounded actually has a larger downstream impact
(e.g. infra change cascades, transfer hits a hot wallet).

- **Mitigation.** Action schema includes blast-radius classification.
  ESCALATE is the default for unclassified high-impact verbs.
- **Residual risk.** Classification gaps. Mitigated by review of
  schema additions and pilot feedback.

### T4 — Policy regression

A policy change weakens checks (e.g. lowering quorum, broadening
allow-list).

- **Mitigation.** Policy changes are code-reviewed; demo and
  evaluator runs catch regressions on shipped scenarios. Artifact
  includes policy digest.
- **Residual risk.** Insider with merge rights. Mitigated by branch
  protection and review requirements.

### T5 — Artifact tampering

A reviewer sees a different artifact than what the gate actually
produced.

- **Mitigation.** Artifact carries digest metadata. Reviewer-facing
  flows are encouraged to verify digests against the gate output.
- **Residual risk.** End-to-end signing and external anchoring are
  on the roadmap; not yet enforced by default.

### T6 — Reproducibility loss

A reviewer cannot re-run the same decision and get the same outcome.

- **Mitigation.** `make demo` reproduces the shipped scenarios with
  the same toolchain as CI. Decision artifact includes inputs needed
  to replay.
- **Residual risk.** Drift in upstream evidence sources. Mitigated by
  declaring collectors and pinning versions.

## Reproducibility commitment

Every shipped decision is intended to be reproducible by an external
reviewer with `git clone` plus `mix deps.get` plus `make demo`. Where
external services are involved, the gate documents how to mock or
replay them.

## Reporting and disclosure

Security issues should be reported following `SECURITY.md` in the
repository. We aim to acknowledge within two business days and to
publish remediation notes in `CHANGELOG.md`.

## Roadmap items relevant to threat model

- Artifact signing and external anchoring.
- Independent evidence-source corroboration policy.
- Expanded evaluator coverage for high-risk verbs.
- Pilot deployments with documented threat boundaries per integration.

This document is versioned alongside the codebase. It will be updated
as scope, mitigations, and pilot scenarios evolve.
