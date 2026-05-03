# PythiaLabs Pilot Use Cases

## Deterministic Evidence Gates for High-Risk AI-Agent Actions

PythiaLabs is an open-source MVP for evaluating whether high-risk AI-agent actions should be allowed, blocked, or escalated before execution.

This document describes practical pilot scenarios where deterministic evidence gates may be useful.

PythiaLabs is not currently presented as a production enforcement system, regulatory compliance product, or certified safety framework. These use cases are intended as research, prototype, and pilot directions.

---

## 1. AI-Agent Financial Approval Gate

### Scenario

An AI agent assists with financial operations such as approving refunds, releasing payments, adjusting account limits, or preparing internal transfer requests.

### Risk

A wrong action may cause financial loss, customer harm, audit failure, or unauthorized movement of funds.

### Evidence gate checks

- Is the operator authorized?
- Is the customer/account evidence fresh?
- Is the requested amount within policy limits?
- Is there a valid approval chain?
- Is the decision-time context complete?
- Is rollback or reversal possible?

### Possible decision outcomes

- **ALLOW** — evidence is fresh, authorization is valid, and policy constraints are satisfied.
- **BLOCK** — approval is missing, policy is violated, or evidence is stale.
- **ESCALATE** — evidence is incomplete or the financial risk is above the autonomous threshold.

### Relevant domains

- FinTech.
- RegTech.
- Banking operations.
- Internal financial controls.
- AI assurance for financial workflows.

---

## 2. AI-Agent Infrastructure Action Gate

### Scenario

An AI agent can suggest or execute infrastructure actions such as deleting a volume, changing deployment configuration, rotating credentials, restarting services, or modifying production resources.

### Risk

A destructive or poorly justified action may cause downtime, data loss, security exposure, or operational instability.

### Evidence gate checks

- Is the target environment production, staging, or development?
- Is the requested action destructive or reversible?
- Is there a current backup or rollback plan?
- Is the operator or agent authorized for this resource?
- Is the incident or change request linked and fresh?
- Are credentials valid and scope-limited?

### Possible decision outcomes

- **ALLOW** — low-risk or well-supported action with valid rollback evidence.
- **BLOCK** — destructive action without backup, authorization, or change context.
- **ESCALATE** — production-impacting action requiring human approval.

### Relevant domains

- DevOps.
- SRE.
- Cloud operations.
- Cybersecurity.
- AI coding and infrastructure agents.
- Enterprise AI governance.

---

## 3. AI-Assisted Web3 Treasury Governance Gate

### Scenario

An AI agent helps prepare, evaluate, or execute DAO treasury actions, including transfers, grants, or governance-controlled payouts.

### Risk

An invalid or malicious action may bypass quorum, voting windows, timelocks, treasury limits, or authorization constraints.

### Evidence gate checks

- Does the action match an approved proposal?
- Was quorum reached?
- Is the voting window valid?
- Has the timelock elapsed?
- Is the transfer still within its valid execution window?
- Is the evidence artifact intact and untampered?

### Possible decision outcomes

- **ALLOW** — governance constraints are satisfied.
- **BLOCK** — quorum, timelock, proposal matching, or temporal authorization fails.
- **ESCALATE** — governance evidence is ambiguous or incomplete.

### Relevant domains

- DAO governance.
- Web3 treasury safety.
- Agentic on-chain workflows.
- Governance audit tooling.
- Crypto risk controls.

---

## 4. AI-Agent Credential and Permission Boundary Gate

### Scenario

An AI agent requests access to credentials, API keys, internal tools, privileged commands, or sensitive datasets.

### Risk

A poorly controlled agent may overreach permissions, access sensitive data, leak credentials, or trigger unauthorized operations.

### Evidence gate checks

- What permission is being requested?
- Is the requested permission required for the stated task?
- Is the permission scoped and time-limited?
- Is the request tied to an approved workflow?
- Is there a record of who or what authorized the access?
- Can the permission be revoked or audited?

### Possible decision outcomes

- **ALLOW** — scoped, justified, time-bounded access with valid authorization.
- **BLOCK** — missing authorization, excessive scope, or unsupported task context.
- **ESCALATE** — sensitive permission requires explicit human review.

### Relevant domains

- AI security.
- Enterprise access governance.
- Internal developer platforms.
- Cybersecurity operations.
- Agent sandboxing.

---

## 5. Public-Sector AI Workflow Gate

### Scenario

An AI agent assists with public-sector workflows such as case routing, eligibility checks, procurement recommendations, document approval, or administrative decisions.

### Risk

An unsupported action may affect citizens, public funds, institutional accountability, or legal review processes.

### Evidence gate checks

- Is the action within the permitted administrative scope?
- Is the underlying evidence fresh and attributable?
- Is human approval required by policy?
- Are affected parties, records, or public funds involved?
- Is the action reviewable after execution?
- Are uncertainty and missing evidence explicitly represented?

### Possible decision outcomes

- **ALLOW** — low-risk administrative action with clear evidence and authority.
- **BLOCK** — missing evidence, unsupported authority, or policy violation.
- **ESCALATE** — citizen-impacting or public-funds-related action requiring human review.

### Relevant domains

- GovTech.
- Public-sector AI.
- Digital public infrastructure.
- AI governance.
- Institutional auditability.

---

## 6. AI Coding Agent Merge or Deployment Gate

### Scenario

An AI coding agent proposes code changes, opens a pull request, modifies tests, changes CI configuration, or suggests deployment.

### Risk

An AI-generated change may pass superficial checks while introducing security, reliability, compliance, or production-readiness risks.

### Evidence gate checks

- Are tests present and relevant?
- Did CI pass?
- Does the change affect security-sensitive files?
- Does the change modify infrastructure, secrets, permissions, or deployment config?
- Is there reviewer approval?
- Is rollback possible?

### Possible decision outcomes

- **ALLOW** — low-risk change with tests, CI, and review evidence.
- **BLOCK** — missing tests, failed CI, secret exposure, or unsafe deployment path.
- **ESCALATE** — high-risk code path or infrastructure change requiring senior review.

### Relevant domains

- AI coding agents.
- DevSecOps.
- Developer tooling.
- Software QA.
- CI/CD governance.

---

## 7. AI-Agent Incident Response Gate

### Scenario

An AI agent assists with incident response: restarting services, disabling features, changing routing, blocking traffic, or applying emergency mitigations.

### Risk

An incorrect incident action may worsen the outage, hide evidence, affect customers, or introduce new failure modes.

### Evidence gate checks

- Is there an active incident or alert?
- Is the proposed action linked to the incident context?
- Is the action reversible?
- Does the action affect production traffic?
- Is there a human incident commander approval for high-impact actions?
- Is the action logged with a stable reason?

### Possible decision outcomes

- **ALLOW** — low-impact, reversible mitigation with active incident context.
- **BLOCK** — unsupported action unrelated to the incident or lacking authorization.
- **ESCALATE** — high-impact mitigation requiring incident commander approval.

### Relevant domains

- SRE.
- Incident response.
- Reliability engineering.
- AI operations.
- Enterprise infrastructure safety.

---

## 8. Pilot Evaluation Criteria

A useful PythiaLabs pilot should be evaluated on:

- clarity of ALLOW / BLOCK / ESCALATE outcomes;
- quality and stability of stop reasons;
- reproducibility of traces;
- ability to detect stale, missing, or conflicting evidence;
- usefulness of evidence artifacts for human reviewers;
- false allow and false block behavior;
- integration friction with existing workflows;
- reviewer time saved or reviewer confidence improved.

---

## 9. Suggested First Pilot Shape

A minimal pilot should include:

1. A small set of high-risk action examples.
2. At least one ALLOW case.
3. At least one BLOCK case.
4. At least one ESCALATE case.
5. Deterministic JSON evidence inputs.
6. Replayable decision traces.
7. Stable stop reasons.
8. Tamper-checkable evidence artifacts.
9. A short reviewer-facing report.

---

## 10. Current Best-Fit Pilot Areas

The strongest near-term pilot areas are:

1. **AI-agent infrastructure action safety**  
   Destructive or production-impacting DevOps actions.

2. **Banking / FinTech AI risk workflows**  
   Pre-execution checks for financial or approval actions.

3. **Web3 treasury governance**  
   Evidence gates for DAO treasury and governance actions.

4. **AI coding agent governance**  
   Review gates for code, CI, deployment, and permission-sensitive changes.

5. **GovTech AI workflow review**  
   Public-sector actions where traceability and institutional accountability matter.

---

## 11. Related Documents

- [`PYTHIALABS_ONE_PAGE_SUMMARY.md`](PYTHIALABS_ONE_PAGE_SUMMARY.md)
- [`RESEARCH_QUESTIONS.md`](RESEARCH_QUESTIONS.md)
- [`agent_infra_action_showcase_expected_output.md`](agent_infra_action_showcase_expected_output.md)
- [`banking_ai_risk_showcase_expected_output.md`](banking_ai_risk_showcase_expected_output.md)
- [`web3_treasury_full_showcase_expected_output.md`](web3_treasury_full_showcase_expected_output.md)
