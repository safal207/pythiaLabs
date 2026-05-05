export const downloadAssets = [
  {
    filename: "ai-agent-pre-execution-safety-checklist.md",
    contentType: "text/markdown; charset=utf-8",
    content: `# AI Agent Pre-Execution Safety Checklist

Before your AI agent changes code, infrastructure, money, or governance, run this checklist.

## 1. Proposed action

- What exact action is the agent proposing?
- Which tool, API, wallet, service, or repository will be touched?
- Is the action read-only, reversible, destructive, financial, or governance-related?

## 2. Authorization

- Who or what authorized the agent to propose this action?
- Is the agent allowed to execute, or only allowed to draft/propose?
- Is there a clear human owner for approval?

## 3. Evidence freshness

- When was the policy state fetched?
- When were approvals fetched?
- When was environment context fetched?
- Is any evidence stale relative to the risk of the action?

## 4. Risk and blast radius

- What is the worst plausible failure mode?
- Can the action be rolled back?
- What systems, funds, users, or production workflows can be affected?

## 5. Decision

Use a simple pre-execution decision:

- ALLOW: evidence is fresh, permissions are valid, and risk is acceptable.
- BLOCK: the action violates policy or lacks required evidence.
- ESCALATE: human review is required before execution.

## 6. Replayability

- Can reviewers replay the same decision later?
- Is there a structured trace?
- Is there a stable stop reason?
- Is there a digest or artifact suitable for CI/security review?

Core rule: verify before execute. Not after the incident.
`,
  },
  {
    filename: "pythialabs-one-page-technical-brief.md",
    contentType: "text/markdown; charset=utf-8",
    content: `# PythiaLabs: One-Page Technical Brief

## What it is

PythiaLabs is an open-source pre-execution safety gate for AI-agent actions.

It evaluates whether a proposed agent action should execute before destructive tools, financial operations, infrastructure changes, or governance actions run.

## Core decision

The gate returns one of three outcomes:

- ALLOW
- BLOCK
- ESCALATE

Every decision is intended to be deterministic, replayable, and inspectable.

## Why it matters

AI agents are moving from answers to actions. A wrong response is bad. A wrong action can delete data, move funds, break production, or approve governance changes.

Post-hoc logs are not enough. High-risk agentic systems need a decision record before execution.

## What the gate checks

- Authorization
- Evidence freshness
- Decision-time context
- Permission boundaries
- Credentials
- Recovery assumptions
- Action risk

## Current use cases

- DevOps and infrastructure agents
- Banking and fintech AI workflows
- Web3 treasury and DAO governance
- AI coding agents before merge, patch, or production change

## Stage

PythiaLabs is an open-source MVP with deterministic local demos. It is not presented as a production enforcement system, regulatory product, or certified safety framework.

## Links

- Repository: https://github.com/safal207/pythiaLabs
- Landing page: https://safal207.github.io/pythiaLabs/
- Demo video: https://youtu.be/IUk3iO0N4YU
`,
  },
  {
    filename: "pythialabs-pilot-partner-pack.md",
    contentType: "text/markdown; charset=utf-8",
    content: `# PythiaLabs Pilot Partner Pack

## Who this is for

PythiaLabs is for teams building AI agents that can touch code, infrastructure, money, or governance.

It is most relevant when post-hoc logs are not enough and reviewers need a decision record before a tool executes.

## What a focused pilot can deliver

In a focused pilot, the goal is to map one or two high-risk agent flows into structured proposals and decision-time evidence.

Expected outputs:

- A mapped high-risk agent action flow
- Structured proposed action payloads
- ALLOW / BLOCK / ESCALATE outcomes
- Stable stop reasons
- Replayable traces
- Optional digest-style artifacts for CI/security review

## Example pilot scenarios

- An infra agent wants to delete or restart a production resource.
- A finance agent wants to approve a payment or high-risk operation.
- A Web3 agent wants to transfer treasury funds.
- A coding agent wants to merge or apply a production patch.

## What we need from a partner

- One concrete high-risk workflow
- Example proposed actions
- Current approval or authorization rules
- Existing evidence sources
- Expected escalation path

## What success looks like

A reviewer can answer: why was this action allowed, blocked, or escalated before execution?

## Contact

Email: safal0645@gmail.com
GitHub: https://github.com/safal207/pythiaLabs
`,
  },
  {
    filename: "sample-evidence-artifact.json",
    contentType: "application/json; charset=utf-8",
    content: `{
  "schema": "pythia.decision_artifact.v1",
  "artifact_id": "art_demo_web3_treasury_0001",
  "trace_id": "trc_01HX_PYTHIA_DEMO_WEB3_0001",
  "project": "PythiaLabs",
  "gate": "web3_treasury_action",
  "action": {
    "action_id": "act_transfer_25000_usdc",
    "type": "treasury_transfer",
    "asset": "USDC",
    "amount": "25000.00",
    "requested_by": "agent:web3-ops-assistant",
    "environment": "mainnet"
  },
  "decision_time_evidence": {
    "policy_version": "treasury_policy_2026_05_01",
    "required_quorum": 3,
    "observed_approvals": 2,
    "wallet_allowlist_match": true,
    "risk_level": "high",
    "recovery_assumption": "transfer_is_not_reliably_reversible"
  },
  "checks": [
    { "name": "authorization", "result": "pass" },
    { "name": "wallet_allowlist", "result": "pass" },
    { "name": "quorum_approval", "result": "fail", "reason": "required_3_observed_2" },
    { "name": "policy_freshness", "result": "fail", "reason": "policy_state_exceeds_freshness_threshold" },
    { "name": "action_risk", "result": "review", "reason": "high_value_irreversible_transfer" }
  ],
  "outcome": "ESCALATE",
  "stop_reason": "missing_quorum_approval_and_stale_policy_state",
  "execution_allowed": false,
  "review_required": true,
  "canonicalization": "pythia.canonical_export.v1",
  "digest": {
    "algorithm": "sha256",
    "value": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
    "note": "Demo digest value for landing-page sample artifact. Regenerate in real CI."
  }
}
`,
  },
];
