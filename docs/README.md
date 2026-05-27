# PythiaLabs Documentation

Welcome to the PythiaLabs documentation index. Use this page to quickly find
the most important docs whether you are a new contributor, reviewer, or grantmaker.

---

## Reviewer Paths

| Reviewer intent | Start here |
|---|---|
| Understand the project quickly | [One-page summary](PYTHIALABS_ONE_PAGE_SUMMARY.md) |
| Understand the portfolio role | [Portfolio relationship](PORTFOLIO_RELATIONSHIP.md) |
| Understand the action-gate flow | [Action Gate Architecture Diagram](architecture_diagram.md) |
| Verify demo evidence artifacts | [Paid Review Demo Reviewer Checklist](paid_review_demo_reviewer_checklist.md), [Evidence Artifact Schema](evidence_artifact_schema.md), and [Artifact Inspection Checklist](artifact_inspection_checklist.md) |
| Read a sample reviewer deliverable | [Paid Review Demo Sample Reviewer Report](paid_review_demo_sample_reviewer_report.md) |
| Check scope boundaries / non-claims | [Non-Claims](NON_CLAIMS.md) |
| Avoid Web3 misclassification | [Positioning vs. Transaction Simulation Tools](positioning_vs_transaction_simulation.md) |
| Review OTF / internet freedom framing | [OTF Reviewer Path](OTF_REVIEWER_PATH.md) |
| Understand ProofPath continuation | [ProofPath Continuation for Reviewers](PROOFPATH_CONTINUATION_FOR_REVIEWERS.md) |
| Evaluate commercial pilot path | [Agent Action Audit Sample Report](AGENT_ACTION_AUDIT_SAMPLE_REPORT.md) |

---

## Architecture

- [Action Gate Architecture Diagram](architecture_diagram.md) — compact visual flow from proposed action to evidence checks, ALLOW / BLOCK / ESCALATE, and reviewer-facing artifacts.
- [Evidence Artifact Schema](evidence_artifact_schema.md) — high-level schema guide for current deterministic demo evidence artifacts, digests, decisions, and stop reasons.
- [Glossary](glossary.md) — concise definitions for core decision terms such as ALLOW, BLOCK, ESCALATE, evidence artifact, stop reason, and replayable trace.
- [Liminal Evidence Stack](LIMINAL_EVIDENCE_STACK.md) — cross-stack overview connecting PythiaLabs, DRP, LTP, CML, and LiminalDB as one deterministic oversight program.
- [Liminal Audit Bridge](LIMINAL_AUDIT_BRIDGE.md) — Petri-like behavioral audit transcript -> T-Trace JSONL -> causal/risk checks -> reviewer-facing report.
- [Database Architecture](database_architecture.md) — Postgres, TimescaleDB, and LiminalDB as three kinds of truth.
- [Persistent Reasoning Memory](persistent_reasoning_memory.md) — append-only reasoning memory roadmap.
- [Agent Memory vs. Action Gates](agent_memory_vs_action_gate.md) — why PythiaLabs is not an organizational memory product.
- [Temporal-Causal Memory Stack](temporal_causal_memory_stack.md) — broader memory and replay architecture.
- [Design Principles](design_principles.md)
- [Web3 Consensus Reason Layer](web3_consensus_reason_layer.md)

---

## Research and Positioning

- [Agent Action Audit Kit](AGENT_ACTION_AUDIT_KIT.md) — sales-facing pilot wedge for auditing one AI-agent workflow and turning opaque behavior into a structured evidence chain.
- [Agent Action Audit Snapshot](AGENT_ACTION_AUDIT_SNAPSHOT.md) — small paid OTO / entry offer for one workflow before a full audit pilot.
- [Agent Action Audit Snapshot Plus](AGENT_ACTION_AUDIT_SNAPSHOT_PLUS.md) — $497 upsell with live walkthrough and prioritized hardening roadmap after the Snapshot.
- [Agent Action Audit Outreach Pack](AGENT_ACTION_AUDIT_OUTREACH.md) — outbound messages, discovery-call structure, qualification questions, and objection handling for first pilots.
- [Agent Action Audit Snapshot Outreach Sequence](AGENT_ACTION_AUDIT_SNAPSHOT_OUTREACH.md) — short DM, cold email, follow-up, and objection scripts for the $197/$497 offer ladder.
- [Agent Action Audit Report Template](AGENT_ACTION_AUDIT_REPORT_TEMPLATE.md) — customer-facing pilot deliverable template for one workflow, action class, or trace/log sample.
- [Agent Action Audit Sample Report](AGENT_ACTION_AUDIT_SAMPLE_REPORT.md) — filled synthetic report for a coding-agent CI autofix workflow showing the expected customer-facing output.
- [Research Roadmap](research_roadmap.md)
- [Open Agentic Models Need Evidence Gates](open_agentic_models_need_evidence_gates.md)
- [Related Prototype: ProofPath](related_proofpath.md) — explains how ProofPath serves as a separate runnable protocol/gateway lab for the PythiaLabs evidence-gate idea.
- [Positioning vs. Transaction Simulation Tools](positioning_vs_transaction_simulation.md) — clarifies that PythiaLabs is not a Web3 transaction simulator; it is a pre-execution evidence gate for AI-agent proposed actions before tools are called.
- [Non-Claims](NON_CLAIMS.md) — explicit scope boundaries: not production security certification, not compliance certification, not a transaction simulator, and not a replacement for human review.
- [AI Coding Agents and CI Autofix Use Case](ai_coding_agents_ci_autofix_use_case.md) — documents how PythiaLabs can gate autonomous coding-agent and CI autofix actions before tools are called.

---

## Demos and Expected Outputs

- [Paid Review Demo Reviewer Checklist](paid_review_demo_reviewer_checklist.md) — concise review steps for running `make demo`, checking expected decisions, verifying evidence, and inspecting the artifact bundle.
- [Artifact Inspection Checklist](artifact_inspection_checklist.md) — checklist for inspecting generated evidence artifacts without trusting terminal output alone.
- [Paid Review Demo Sample Reviewer Report](paid_review_demo_sample_reviewer_report.md) — example Markdown report a reviewer could produce after running the deterministic paid review demo.
- [Support-safety gate demo](https://youtu.be/A6UAR3e2r3k) — deterministic support-safety gate: sanitized trace → safety boundary → scenario checks → evidence → PASS
- [Paid Review Demo Expected Output](../examples/paid_review_demo_expected_output.md)
- [Agent Infrastructure Showcase Expected Output](agent_infra_action_showcase_expected_output.md)
- [Banking AI Risk Showcase Expected Output](banking_ai_risk_showcase_expected_output.md)
- [Web3 Treasury Showcase Expected Output](web3_treasury_full_showcase_expected_output.md)

---

## Funding and Support

- [Grant Evidence Package](GRANT_EVIDENCE.md) — reviewer-facing evidence matrix, reproducible commands, architecture sketch, current limitations, and grant roadmap.
- [Grant Readiness](grant_readiness.md)
- [Grant One-Pager — Web3 Treasury Reason Layer](grant_one_pager_web3_treasury_reason_layer.md)
- [Grant Application Summary](grant_application_summary.md)
- [Threat Model — Web3 Treasury Reason Layer](threat_model_web3_treasury_reason_layer.md)
- [Sponsorship and Paid Pilots](SPONSORSHIP.md)
- [License Strategy](license_strategy.md)

---

## Contributor Onboarding

- [Contributor Task Map](contributor_task_map.md) — explains Level 1 / Level 2 / Level 3 task types and safe first-contribution boundaries.
- [Docs PR Review Checklist](docs_pr_review_checklist.md) — maintainer checklist for reviewing docs-only PRs without inflating safety, compliance, or production claims.

---

## Security and Governance

- [Security Policy](../SECURITY.md)
- [Code of Conduct](../CODE_OF_CONDUCT.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Security Automation](security_automation.md)
