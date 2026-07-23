# OpenAI Cybersecurity Grant Program application — CAEP-OpenAI

Status: form-ready draft  
Applicant: GitHub user `safal207` / PythiaLabs open-source project  
Submission route: OpenAI Cybersecurity Grant Program  
Public implementation: https://github.com/safal207/pythiaLabs/tree/main/protocols/caep

> Before submission, replace the bracketed personal fields in **Applicant information**.

## Applicant information

- **First name:** [Alexey — verify spelling used in official documents]
- **Last name:** [insert]
- **Email:** [insert]
- **Company or University:** Independent / PythiaLabs open-source project
- **Role / Title:** Independent QA and systems analyst; open-source agent-security contributor
- **LinkedIn:** [insert]
- **Other contributors:** Initial implementation and research design by `safal207`, with open community review through GitHub and OWASP AISVS discussions. Additional independent reviewers will be recruited during the project.

## Project title

**CAEP-OpenAI: Verifiable Agent Action Episodes for Defensive AI Incident Response**

## One descriptive sentence

Build and evaluate an OpenAI Agents SDK adapter and public benchmark that independently proves whether consequential tool actions remained bound to authorization, produced the recorded external outcome, and actually recovered after containment.

## Complete project proposal

### 1. Summary

Agentic systems can plan, select tools, cross execution boundaries, and continue through long multi-step trajectories. Existing traces and audit logs are valuable, but they may not provide an independently verifiable answer to four incident-response questions:

1. Did the runtime dispatch exactly the operation that was authorized?
2. What external state change actually occurred?
3. Which earlier action causally enabled each later step?
4. Did containment or rollback achieve its objective, or was the recovery merely invoked?

CAEP—the Causal Action Episode Packet—is an open, vendor-neutral protocol prototype that treats a consequence-bearing action as one auditable episode:

`intent → authorization → exact dispatch → observable outcome → containment/recovery`

The existing prototype includes JSON Schema 2020-12, strict semantic and causal validation, Ed25519 integrity verification with separate authority roles, digest-bound JSON Lines transport, synthetic and adversarial fixtures, and 33 automated tests. It has been published openly, merged with exact-head CI and security checks, and submitted for discussion to the OWASP AISVS AI Incident Response effort.

This project will convert that protocol prototype into a focused defensive evaluation for OpenAI agent workflows. We will build an adapter for the OpenAI Agents SDK, create a bounded benchmark of clean and adversarial tool-action episodes, measure whether standard tracing alone and tracing-plus-CAEP can detect execution drift and false recovery claims, and publish the adapter, benchmark, results, and reproducibility artifacts under an open-source license.

### 2. Research questions

The project will answer the following empirical questions:

1. Can an external verifier reconstruct the exact chain from agent intent and authorization through dispatch, outcome, and recovery without trusting the agent's narrative?
2. Which action mutations are reliably detected: target, parameters, network destination, credential class, tool identity, execution boundary, causal parent, time ordering, missing outcome, or false recovery?
3. What additional evidence does CAEP provide beyond ordinary agent traces, and where is it redundant with existing tracing and guardrails?
4. What are the operational costs in latency, storage, implementation complexity, and false-positive rate?
5. What is the minimum interoperable evidence set suitable for incident response and possible standards work?

### 3. Technical approach

#### Work package A — OpenAI Agents SDK integration

We will implement a small adapter around an OpenAI Agents SDK workflow using function tools and controlled sandbox or local execution. The adapter will emit records at four independently testable boundaries:

- policy decision and authorization;
- actual tool dispatch;
- externally observed outcome;
- containment and recovery.

The adapter will preserve native OpenAI traces rather than replacing them. CAEP records will be correlated to the native run and tool-call identifiers, allowing a direct comparison between built-in observability and independently verifiable evidence.

Where practical, the four record classes will use distinct authority roles and keys:

- policy decision point;
- enforcement point;
- independent observer;
- incident controller.

No production credentials, customer data, private repositories, or real external targets will be used.

#### Work package B — Defensive mutation benchmark

We will create a synthetic benchmark containing successful, denied, failed, lost-outcome, drifted, and recovered episodes. Each baseline episode will be replayed with one controlled mutation at a time:

1. target changed after approval;
2. parameter digest changed after approval;
3. internal destination redirected externally;
4. credential class replaced;
5. tool identity or execution boundary changed;
6. unknown decision or policy-conformance value introduced;
7. causal parent removed, replaced, or reordered;
8. authorization used after expiry;
9. terminal outcome suppressed;
10. recovery claimed while the objective is unmet or residual effects remain;
11. record payload modified after signing;
12. proof envelope or transport record modified.

The initial target is at least 1,000 bounded episodes: 500 conformant and 500 adversarial. Exact seeds, configuration, model identifiers, prompts, tool schemas, and adapter versions will be pinned in the public artifacts.

#### Work package C — Comparative evaluation

We will compare three conditions:

- native agent tracing and application logs;
- strict unsigned CAEP evidence (F2);
- independently verified signed CAEP evidence (F3).

Primary metrics:

- mutation-detection rate by class;
- false-positive rate on conformant episodes;
- percentage of dispatches with a terminal outcome;
- percentage of incidents with an objectively verified recovery state;
- causal reconstruction completeness;
- signature and transport tamper-detection rate;
- added latency per action;
- additional bytes per action;
- implementation effort and failure modes.

We will explicitly document cases where existing OpenAI tracing or guardrails already provide equivalent evidence. The goal is not to manufacture novelty, but to identify the smallest additional layer that produces independently verifiable incident evidence.

#### Work package D — External review and standards feedback

The draft requirements are already public in an OWASP AISVS AI Incident Response discussion. During the project, we will invite reviewers to challenge:

- the evidence model;
- trust-root separation;
- canonicalization and signature semantics;
- recovery definitions;
- benchmark representativeness;
- assurance-level placement.

Corrections will be append-only and linked to exact commits. Community feedback will be recorded without silently rewriting previous claims.

### 4. Deliverables

1. An open-source OpenAI Agents SDK CAEP adapter.
2. A reproducible synthetic benchmark with clean and adversarial episodes.
3. A command-line verifier for semantic, causal, time-order, signature, and JSONL transport properties.
4. A comparative evaluation report covering detection, false positives, latency, storage, and implementation cost.
5. A minimal evidence profile suitable for agent incident-response systems.
6. Formal requirement language and adversarial tests that standards projects may adopt without adopting CAEP terminology.
7. Public CI artifacts and exact-version manifests.

All deliverables will be intended for maximal public benefit and released under a permissive open-source license. No confidential OpenAI information is requested or expected.

### 5. Why this is defensive

The project does not develop offensive capabilities, exploit OpenAI systems, or seek access to internal infrastructure. All experiments use synthetic operations inside controlled environments. The benchmark's purpose is to verify authorization continuity, detect execution drift, preserve incident evidence, and validate recovery.

Any issue that appears to be a concrete vulnerability in an OpenAI product will be removed from the public benchmark and reported through OpenAI's coordinated vulnerability disclosure process before publication.

### 6. Why OpenAI models and the Agents SDK

The OpenAI Agents SDK provides a practical agent loop with tools, handoffs, guardrails, tracing, approvals, sessions, and sandbox-oriented workflows. That makes it a strong reference environment for measuring the gap between runtime observability and independently verifiable action evidence.

We will use the current OpenAI frontier reasoning and coding models available through the API at project start. Exact model and SDK versions will be pinned in every result. The design will remain model-neutral so the evidence protocol can also be compared across other runtimes later.

### 7. Team and execution capability

The applicant is an experienced QA engineer and systems analyst focused on fail-closed validation, API and integration testing, causal defect analysis, and open-source security protocols. The existing CAEP implementation demonstrates the ability to move from requirement language to schema, validator, adversarial fixtures, cryptographic verification, CI, review fixes, and standards-oriented documentation.

The project will stay deliberately small. Additional contributors will be limited to bounded code review, cryptography review, benchmark review, and documentation review.

### 8. Success criteria

The pilot succeeds if it produces all of the following:

- a working OpenAI Agents SDK adapter;
- at least 1,000 reproducible episodes;
- at least 95% detection for the defined mutation classes, with every miss explained;
- less than 1% false positives on the conformant synthetic set;
- quantitative latency and storage measurements;
- independently repeatable verification from exported artifacts;
- at least one external review resulting in accepted changes or an evidence-backed rejection;
- a clear conclusion about which CAEP controls are useful, redundant, or impractical.

Failure conditions will also be published. These include excessive runtime overhead, unstable bindings to SDK internals, inability to separate trust roots meaningfully, or evidence that native tracing already provides the same independent guarantees at lower cost.

## What problem are you trying to solve? — 200-word field

Agentic systems can authorize one operation but dispatch a modified target, parameter set, credential, destination, tool, or execution boundary later in the run. Standard traces may show what the runtime says occurred, yet incident responders also need evidence that survives a compromised or mistaken runtime. They must determine whether the exact authorized action was executed, what external state changed, which step causally enabled later actions, and whether containment actually restored an acceptable state.

The current gap is not a lack of logs. It is a lack of independently verifiable continuity across authorization, dispatch, outcome, and recovery. A missing terminal outcome may be treated as harmless silence; a rollback command may be mistaken for successful recovery; an integrity-proof field may be accepted without verifying its signature; and corrections may overwrite what was believed at decision time.

This project will build and evaluate a small OpenAI Agents SDK adapter that produces portable Causal Action Episode Packets, then test it against controlled mutations and compare it with native tracing. The result will be an open benchmark, verifier, and evidence profile for defensive agent incident response—not an offensive security system and not a claim about OpenAI's internal architecture.

## Project timeline

**16-week focused pilot**

- **Weeks 1–2:** freeze threat model, adapter boundary, benchmark schema, safety scope, and exact dependencies.
- **Weeks 3–5:** implement OpenAI Agents SDK adapter and correlate CAEP records with native traces.
- **Weeks 6–8:** build synthetic clean episodes and twelve mutation classes.
- **Weeks 9–10:** run at least 1,000 episodes; capture latency, storage, detection, and false-positive metrics.
- **Weeks 11–12:** analyze native tracing versus F2 and F3 evidence; document redundancy and gaps.
- **Weeks 13–14:** external cryptography, agent-runtime, and incident-response review; address bounded findings.
- **Weeks 15–16:** publish benchmark, report, minimal evidence profile, reproducibility package, and standards feedback.

## Requested funding / API credits / resources

### Primary request

**$40,000 total support:**

- **$25,000 research grant** for engineering time, benchmark design, independent review, and documentation;
- **$15,000 in OpenAI API credits** for reproducible agent runs, adversarial mutations, reruns after review, and model-version comparisons.

Indicative allocation:

- adapter and benchmark engineering: $15,000;
- experiment execution and analysis: $7,000;
- independent cryptography and incident-response review: $5,000;
- documentation, reproducibility, and community coordination: $3,000;
- OpenAI API usage: $15,000 in credits.

### Reduced-scope option

With **$10,000 in API credits only**, we will deliver a narrower 8-week pilot covering one OpenAI Agents SDK workflow, six mutation classes, at least 400 episodes, and a concise public findings report.

### Additional non-financial request

If available, one bounded methodology-review conversation with an OpenAI safety, preparedness, agent-runtime, or security engineer would help ensure the evaluation targets a meaningful boundary. No internal access, confidential data, or endorsement is requested.

## Existing public work and prior research disclosure

- CAEP RFC: https://github.com/safal207/pythiaLabs/issues/242
- Base protocol and strict validation: https://github.com/safal207/pythiaLabs/pull/243
- Verified evidence and portable JSONL layer: https://github.com/safal207/pythiaLabs/pull/244
- OWASP AISVS proposal: https://github.com/safal207/pythiaLabs/blob/main/protocols/caep/OWASP_AISVS_IR_PROPOSAL.md
- Public OWASP discussion comment: https://github.com/OWASP/AISVS/issues/1083#issuecomment-5056673362

The work is independent, open source, and currently unfunded. No confidential datasets or third-party proprietary materials are included.

## Additional notes

This submission is primarily a request for research collaboration, API credits, and methodological feedback. If it does not fit the current grant portfolio, please route it to the team responsible for agentic security, safety evaluations, Preparedness, external testing, or defensive cybersecurity research.
