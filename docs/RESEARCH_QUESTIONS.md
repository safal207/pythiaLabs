# PythiaLabs Research Questions

## Deterministic Evidence Gates for High-Risk AI-Agent Actions

PythiaLabs explores a practical research and engineering question:

> Before an AI agent executes a high-risk action, what evidence should be required to allow, block, or escalate that action?

This document lists research questions that can guide future development, evaluation, collaboration, and external review.

---

## 1. Evidence Requirements

### Core question

What evidence is sufficient before a high-risk AI-agent action is allowed to execute?

### Sub-questions

- Which evidence dimensions are necessary for different action classes?
- How should authorization, evidence freshness, environment context, credentials, and recovery assumptions be represented?
- How should missing evidence differ from stale evidence?
- How should conflicting evidence be handled?
- What evidence should always require human review?
- How should evidence requirements change across domains such as finance, infrastructure, Web3 governance, and public-sector workflows?

---

## 2. Stop Reasons and Decision Semantics

### Core question

How should ALLOW, BLOCK, and ESCALATE decisions be made legible, stable, and reviewable?

### Sub-questions

- What stop reasons are most useful for human reviewers?
- Which stop reasons should be domain-specific and which should be universal?
- How should multiple simultaneous failure reasons be ranked?
- Should a gate return one primary stop reason or a structured set of contributing reasons?
- How should confidence or uncertainty be represented without pretending to be more precise than the system can justify?
- How can stop reasons remain stable across software versions and benchmark runs?

---

## 3. Replayability and Auditability

### Core question

How can AI-agent action traces be made replayable and tamper-checkable?

### Sub-questions

- What minimum trace structure is required for deterministic replay?
- How should action intent, evidence inputs, gate decisions, and stop reasons be recorded?
- How should evidence artifacts be hashed or sealed?
- What should be considered tampering in an evidence artifact?
- How can replay help distinguish model failure, tool failure, policy failure, and evidence failure?
- How can reviewers compare two versions of the same action trace?

---

## 4. Deterministic Gates and Probabilistic AI Evaluations

### Core question

How can deterministic control layers complement probabilistic AI evaluations?

### Sub-questions

- Which risks are better handled by deterministic gates rather than model-based evaluation?
- Where should model judgment still be used?
- How should deterministic checks interact with LLM monitors, classifiers, or policy models?
- Can deterministic gates reduce the burden on human reviewers?
- Can evidence gates improve evaluation integrity by making action context explicit?
- How should deterministic gates behave when upstream model output is ambiguous?

---

## 5. Agent Control and Oversight

### Core question

Can pre-execution evidence gates improve control over increasingly autonomous AI agents?

### Sub-questions

- Which agent actions should never bypass a gate?
- How should the system define high-risk actions?
- How can the gate prevent privilege escalation, stale authorization, or unsupported destructive actions?
- How should the system distinguish reversible and irreversible actions?
- What actions should default to ESCALATE rather than BLOCK?
- How can a gate support human oversight without creating unnecessary friction?

---

## 6. Benchmark Design

### Core question

What benchmark tasks best represent high-risk AI-agent actions?

### Candidate benchmark classes

- Financial approval or transfer actions.
- Infrastructure deletion or production deployment actions.
- Credential access or permission-boundary actions.
- DAO treasury or governance actions.
- Public-sector workflow approvals.
- Security-sensitive automation tasks.
- Recovery-sensitive actions where rollback assumptions are critical.

### Sub-questions

- What should a minimal benchmark fixture include?
- How should ALLOW, BLOCK, and ESCALATE examples be balanced?
- How should false allows and false blocks be measured?
- How should benchmark cases represent ambiguity rather than only obvious failures?
- How can benchmark results remain reproducible across environments?

---

## 7. Human Review and Escalation

### Core question

When should an AI-agent action be escalated to a human reviewer?

### Sub-questions

- What information should a reviewer see first?
- How much trace detail is enough for a reviewer to make a decision?
- How should reviewer decisions feed back into future evidence requirements?
- How should the system avoid overwhelming reviewers with low-value escalations?
- How should escalation differ across domains with different risk tolerances?

---

## 8. Domain Adaptation

### Core question

How can a general evidence-gate pattern adapt across domains without losing rigor?

### Candidate domains

- AI safety research.
- Enterprise AI governance.
- FinTech and RegTech.
- GovTech and public-sector AI.
- Cybersecurity and infrastructure automation.
- Web3 governance and treasury safety.
- Developer tooling for autonomous coding agents.

### Sub-questions

- Which gate dimensions are shared across domains?
- Which dimensions require domain-specific policies?
- How should domain rules be configured, tested, and audited?
- How should external regulatory or organizational policies map into deterministic gate logic?

---

## 9. Current Research Hypothesis

PythiaLabs is based on the following working hypothesis:

> High-risk AI-agent actions should pass through deterministic evidence gates before execution, producing replayable traces and stable stop reasons that make action governance reviewable, auditable, and improvable over time.

This hypothesis does not claim to solve AI alignment, replace human oversight, or provide production-grade enforcement. It proposes a focused control layer that can complement existing AI safety, governance, and evaluation approaches.

---

## 10. Collaboration Directions

PythiaLabs is open to feedback and collaboration around:

- benchmark design;
- evidence schema design;
- stop-reason taxonomy;
- agent monitoring and evaluation integrity;
- AI control and oversight research;
- RegTech / GovTech use cases;
- enterprise pilot scenarios;
- reproducible demo cases for high-risk agent actions.

For a concise overview, see:

- [`PYTHIALABS_ONE_PAGE_SUMMARY.md`](PYTHIALABS_ONE_PAGE_SUMMARY.md)
