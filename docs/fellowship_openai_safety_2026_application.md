# PythiaLabs — OpenAI Safety Fellowship (pilot) — application draft

This file is a **submit-ready style draft** for the **OpenAI Safety Fellowship** announced April 6, 2026. **Program facts below are taken only from the official announcement**  
[Introducing the OpenAI Safety Fellowship](https://openai.com/index/introducing-openai-safety-fellowship/)  
(applications, dates, priority areas, expected outputs, contact). For eligibility, compensation, and the submission form, use the links on that page (including the **application form** and **openaifellows@constellation.org** for questions). This document is **not** affiliated with OpenAI; it is internal preparation for the maintainer.

---

## 1. Project title

**PythiaLabs: Deterministic Evidence Traces for Agentic Oversight**

---

## 2. Summary (one sentence)

PythiaLabs is a deterministic oversight layer for agentic actions: it evaluates proposed actions **before execution**, producing replayable decision traces, stable stop reasons, and tamper-checkable evidence artifacts so humans and external evaluators can see **why** a system was allowed, blocked, or should be escalated.

---

## 3. Core research question

**How can autonomous AI systems (and the workflows around them) produce deterministic, tamper-checkable evidence traces that let humans and external evaluators verify why a proposed action was allowed, blocked, or escalated before execution?**

Secondary questions:

- What trace and artifact schema is minimal yet sufficient for audit and regression testing?
- How do we benchmark “safe,” “unsafe,” “drifted,” and **tampered** cases in a way that is reproducible across runs?

---

## 4. Motivation

Agentic systems increasingly orchestrate real-world effects through tools, APIs, code, browsers, and operational workflows. The critical safety object is not only *what* the model said, but **whether a proposed effect should occur** and **what reasoning justified that gate**.

Without deterministic, reviewable **pre-execution** artifacts, oversight degrades: teams rely on ad hoc logs, post-hoc screenshots, or opaque scores. PythiaLabs targets **agentic oversight** and **safety evaluation** in the sense used in the official fellowship announcement: work that is **empirically grounded**, with explicit allow/deny boundaries, **robustness** to bad inputs, and **scalable** patterns (schema + verifier + tests) that others can reuse.

*Framing note:* the public repository includes **domain demos** (e.g. structured “treasury/governance” style scenarios) as **stress tests** for the same oversight primitives. The fellowship proposal is **not** “a Web3 product pitch”; it is **deterministic evidence and evaluation** for agentic action gating, with that domain as one evaluation surface.

---

## 5. Technical approach

**PythiaLabs (reference implementation).**

- **Pre-execution gate:** structured proposal → deterministic evaluation → allow/deny + **stable stop reasons** (reject paths are explainable, not a single scalar).
- **Traces:** chronological records of which checks ran and in what order (replay-oriented).
- **Evidence layer:** export traces; compute digests; verify; detect tamper; optional envelope-style packaging for reviewer workflows. Demos are **explicitly** non-production crypto (local, educational); see repository limitations.

**CML / LTP (conceptual stack).**  
*CML (Causal Memory Layer) and LTP (Liminal Thread Protocol)* name the broader research arc: connecting causal-temporal policy state to durable, replayable evaluation and auditable agent handoffs. These components are not production storage or enforcement systems in the current PythiaLabs MVP, but they inform the long-term direction for evidence objects, trace continuity, and agentic oversight.

**Evaluation stance:** property-style and scenario-based tests; emphasis on invariants (authorization windows, monotonicity of checks, tamper detection) over opaque end-to-end scores.

---

## 6. Existing work and links

| Resource | URL / pointer |
|----------|----------------|
| Source repository | `https://github.com/safal207/pythiaLabs` |
| License | Apache-2.0 (`LICENSE`, `docs/license_strategy.md`) |
| Reviewer-anchored release (example) | Tag `v0.1.0-pregrant` — `https://github.com/safal207/pythiaLabs/releases/tag/v0.1.0-pregrant` |
| Agent safety / oversight demos | `examples/agent_safety_showcase.exs`, `README.md` |
| Full trace + evidence path (demo) | `examples/web3_treasury_full_showcase.exs` + `docs/web3_treasury_full_showcase_expected_output.md` |
| Threat model (reason layer) | `docs/threat_model_web3_treasury_reason_layer.md` |
| Security posture | `SECURITY.md`, `docs/security_automation.md` |

*Fill before submit:* your GitHub handle, one-line CV link if used in the form.

---

## 7. Fellowship program dates (official)

Per [the announcement](https://openai.com/index/introducing-openai-safety-fellowship/):

- Program: **September 14, 2026** through **February 5, 2027**
- Applications **close May 3** (see current year on the live site and form)
- Successful applicants notified by **July 25**

Fellows are expected to produce a **substantial research output** (e.g. **paper, benchmark, or dataset**). Workspace in Berkeley (Constellation) is mentioned; **remote** work is also possible. **Reference contacts are required** on the application.

---

## 8. Five-month plan (aligned to Sep 14, 2026 – Feb 5, 2027)

| Month | Focus |
|-------|--------|
| **1 (Sep–Oct)** | Threat model and **taxonomy of agentic action failure modes** (misconfiguration, wrong authorization time, policy drift, tampered evidence). Tighten scope for a public benchmark. |
| **2 (Oct–Nov)** | **Benchmark fixtures**: accepted / blocked / drifted / tampered cases; **deterministic trace + artifact schema** (versioned). |
| **3 (Nov–Dec)** | **Verifier** and tamper/drift test harness; open **test vectors** and reproducible scripts. |
| **4 (Dec–Jan)** | **Evaluation** across scenario pack; document failure modes and coverage gaps. |
| **5 (Jan–Feb)** | **Technical report** (and/or short paper draft) + public benchmark release; integrate feedback from mentor cohort. |

---

## 9. Expected outputs (fellowship deliverables)

Aiming for outputs that match the program’s “paper, benchmark, or dataset” bar:

1. **Benchmark** of agentic action / gate scenarios: allowed, blocked, drifted, tampered, with **expected traces and outcomes**.  
2. **Deterministic verifier** (or verifier specification + reference implementation) for evidence artifacts and trace integrity.  
3. **Open test vectors** and reproducible evaluation commands (e.g. `mix test` + documented scenarios).  
4. **Technical report** (and optionally a short workshop-style paper) on **evidence for agentic oversight**: schema, invariants, and limitations.

---

## 10. Applicant profile (template — complete before submit)

*Replace this section with your own words and the exact details required on the form.*

**Draft narrative (align to your real CV):**

- Long-form **product QA / quality engineering** in high-stakes domains (e.g. fintech, trading, APIs, observability): practice finding systems that **look correct** while being **unsafe, inconsistent, or causally wrong** under edge loads and time boundaries.  
- Motivation: treat **agentic oversight** as a *systems* problem—explicit gates, traces, and tamper evidence—not only prompt tuning.  
- **Research ability** is shown through runnable code, test design, and clear threat modeling in-repo; the fellowship period focuses on **benchmarking and publication-style synthesis**, not only feature work.

*OpenAI’s announcement states they welcome varied backgrounds and **prioritize research ability, technical judgment, and execution** over specific credentials* — see the [official post](https://openai.com/index/introducing-openai-safety-fellowship/).

**Reference contacts:** required by the program — line up per application instructions.

---

## 11. Risks and limitations

**Project / technical**

- **Scope risk:** Over-building product features instead of a **reproducible benchmark + report**. Mitigation: time-box the reference implementation; prioritize scenario pack and verifier.  
- **Generalization risk:** One domain (e.g. structured governance-style demos) may not cover all agentic failure modes. Mitigation: abstract scenario template; at least one **domain-agnostic** example (e.g. generic “action with policy and time window”).  
- **MVP limits** (must stay explicit in any submission and papers): the repository **does not** claim production cryptography, wallet integration, on-chain execution, RPC/indexer integration, on-chain enforcement, production identity, or durable external storage. Demos are **local** and **reviewer-oriented**.

**Program / process**

- High competition; acceptance is not guaranteed.  
- Dates and form fields may change—**verify on the live announcement and application form** before submit.

---

## 12. Why this matches OpenAI’s stated priority areas

From the [fellowship announcement](https://openai.com/index/introducing-openai-safety-fellowship/), priority areas **include** (among others) **safety evaluation**, **robustness**, **scalable mitigations**, **privacy-preserving safety methods**, **agentic oversight**, and **high-severity misuse domains**.

This project maps most directly to:

- **Agentic oversight** — pre-execution gates, explainable reject paths, human-reviewable traces.  
- **Safety evaluation** — benchmark + verifier + invariants, not a single black-box score.  
- **Robustness / misuse-adjacent** — tamper and drift cases as first-class test categories.

---

## 13. Official links (program only)

- Announcement: [Introducing the OpenAI Safety Fellowship](https://openai.com/index/introducing-openai-safety-fellowship/)  
- Use the **application form** and contact email from that page (e.g. **openaifellows@constellation.org** for process questions)

---

## 14. Internal checklist before submit

- [ ] Reframe all copy toward **agentic oversight / safety evaluation**, not “Web3 treasury product.”  
- [ ] Re-read MVP **limitations** in `README.md` and mirror them in the fellowship form where relevant.  
- [ ] Confirm **deadline** and year on the live form (May 3, **year** as posted).  
- [ ] Attach or link **release/tag** and **one** primary demo command + expected output doc.  
- [ ] Complete **reference contacts** per form.  
- [ ] This file is a draft — **not** legal advice.
