# External Research One-Pager: Independent Verification of AI-Agent Actions

**Public pre-submission research concept — October 18, 2026**  
**Author:** [Aleksei Safonov](https://github.com/safal207)  
**Repository:** [PythiaLabs](https://github.com/safal207/pythiaLabs)  
**Status:** Research/evaluation concept; **not a new grant submission, lab endorsement or accepted paper.**  
**Theme:** AI control · agentic oversight · secure tool execution · reproducible evaluations

## 1. Research question

**When an AI agent reports success after a tool/API call, can independent structured verification distinguish an authorized action from an actually observed outcome—under retries, stale authorization and incomplete evidence—more reliably than simple status-based checks?**

A secondary question is how much additional false-positive rate, latency, evidence-storage cost and review complexity the verification introduces.

## 2. Existing work vs. proposed study

**Already implemented in public code:**

- [PythiaLabs](https://github.com/safal207/pythiaLabs): experimental pre-execution evidence gates returning `ALLOW`, `BLOCK` or `ESCALATE`, with local demos, replayable traces and stable stop reasons.
- [CAEP — Causal Action Episode Packet](../protocols/caep/README.md): an experimental vendor-neutral episode format connecting `intent → authorization → dispatch → outcome → recovery`, strict validators and synthetic negative/tamper fixtures.
- [Causal Memory Layer](https://github.com/safal207/Causal-Memory-Layer): a separate causal audit/history project with its own scope and verification claims.

These are **related but independent software surfaces**. Their existence does **not** demonstrate a completed integrated, production-hardened system or improvement over baselines.

**Proposed, not yet demonstrated:** a frozen comparative study with identical synthetic scenarios, pre-registered metrics and independent reruns.

## 3. Proposed minimal evaluation

The study would use a publicly documented set of safe synthetic action episodes. Example failure categories:

1. **Stale authorization:** decision permits action at `t0`, authority expires or changes before execution at `t1`.
2. **Action drift:** executed target/parameters differ from what was authorized.
3. **False success:** HTTP 200/accepted response is observed, but the intended external state transition is missing or unknown.
4. **Duplicate/replayed execution:** repeated request would cause a second consequential effect.
5. **Missing recovery evidence:** a rollback/containment function is called, but no verifiable corrected state is observed.
6. **Tampered trace:** evidence fields or causal links are modified after generation.

**Baseline A:** HTTP-status or agent-narrative-only pass/fail.

**Baseline B:** ordinary structured trace review without additional independent verification.

**Candidate C:** deterministic pre-execution policy gates plus an offline, independently supplied evidence/episode verifier where integrations genuinely exist. **Do not treat a separate CAEP verifier and PythiaLabs gate as an already deployed adapter.**

Keep fixtures balanced enough to compute a confusion matrix. Publish exact dataset size, inclusion rules and seeds *before* measuring. Add an `UNKNOWN / insufficient evidence` outcome rather than turning an absent event into proof of failure.

## 4. Pre-registered outcomes and evidence

| Outcome | Proposed method | Current status |
| --- | --- | --- |
| Dangerous action detection | TP/FP/FN/TN on labeled synthetic fixtures | Not measured in this one-pager |
| False-success detection | Compare claimed outcome to declared authoritative simulator state | Not measured |
| Duplicate-effect avoidance | Validate logical operation ID and authoritative effect count | Not measured |
| Runtime overhead | Same-run latency and storage measurements with environment pinned | Not measured |
| Review burden | Independent reviewer effort/timing protocol | Not measured |
| Repeatability | Re-run frozen fixtures on a clean checkout and report all exceptions | Not measured |

Report means, intervals or uncertainty where appropriate; publish negative results and false positives. Do not infer general production security from a synthetic benchmark.

## 5. Reviewer quick path for existing pieces

These are **commands described by the repository**, not a claim that the proposed comparison is already runnable:

```bash
git clone https://github.com/safal207/pythiaLabs.git
cd pythiaLabs
mix deps.get
mix test
make demo
```

Strict CAEP reference example:

```bash
python3 protocols/caep/tools/validate_caep_strict.py \
  protocols/caep/examples/hypothetical_sandbox_escape_episode.json
```

Core documentation: [Grant Evidence](GRANT_EVIDENCE.md) · [Reviewer path](REVIEWER_PATH.md) · [CAEP scope](../protocols/caep/README.md) · [Limitations](LIMITATIONS.md).

## 6. Candidate public outputs (work plan, not a funding promise)

| Phase | Planned artifact |
| --- | --- |
| 1 | Frozen scope, synthetic fixture schema, baseline definitions, reproducibility instructions |
| 2 | Paired benchmark runner for feasible baseline/candidate paths |
| 3 | False-positive/error taxonomy, replay stability and resource-cost measurements |
| 4 | Open data/fixture pack, limitations, independent reproduction notes, short technical report |

Any integration using external provider models should be separately scoped, authorized and costed. A proposal can remain entirely offline/synthetic until eligibility and lawful access are confirmed.

## 7. Collaboration request, fitted to the actual channel

> We seek **methodology feedback or collaboration** on evidence-grounded verification of AI-agent tool actions. We have an open-source experimental verifier and are preparing a bounded synthetic comparison against status-based and trace-only baselines. We would value feedback on the most important failure categories, credible baselines, and independent reproduction requirements. The attached repositories are prototypes with published limitations; we do not claim to have proved universal safety or completed this benchmark.

The above is a *template*, not an email already sent. It must be adapted to an actual lab program. **No external recipient is implied to review unsolicited GitHub links.**

## 8. Important submission and eligibility guardrails

- An earlier [CAEP-OpenAI Cybersecurity Grant proposal](../protocols/caep/OPENAI_CYBERSECURITY_GRANT_PROPOSAL.md) was **recorded as submitted on July 23, 2026** in [issue #248](https://github.com/safal207/pythiaLabs/issues/248#issuecomment-5057425053). Do **not** submit a duplicate as new; a revised complete proposal would need materially changed scope and explicit revision status.
- [OpenAI Researcher Access](https://openai.com/form/researcher-access-program/) is for qualifying research API credits; active research/nonprofit affiliation and residence in an [API-supported country](https://developers.openai.com/api/docs/supported-countries) matter. It is not a general product pitch route.
- The [OpenAI Safety Fellowship 2026](https://alignment.openai.com/safety-fellowship/) application deadline was **May 3, 2026**; that cohort is not an open target on October 18, 2026.
- The [Anthropic Fellows 2026 description](https://job-boards.greenhouse.io/anthropic/jobs/5183044008) requires **work authorization and location in the US, UK, or Canada**, full-time participation, and provides **no visa sponsorship** for Fellows. October 18 is the published January-cohort deadline, but geographic/work-authorization eligibility must be satisfied first.
- [Google DeepMind Student Researcher](https://deepmind.google/student-researcher-program/) requires current enrollment in Bachelor's, Master's or PhD and in-person availability.
- A public [Hugging Face Space](https://huggingface.co/docs/hub/en/spaces-overview) is a practical portfolio/demo channel, not an acceptance or endorsement by a research team.
- Check all dates/requirements again at the application time; these links describe program types, not a promise of acceptance.
- Do not include privileged credentials, personal data, private security findings or code with unverified re-use rights.

## 9. Stop conditions

Do not send or automate outreach until the human author approves the **exact destination, wording, disclosure, and attachments**. Check past sent messages and GitHub issue tracking first. Do not claim a response/partnership unless independently documented.
