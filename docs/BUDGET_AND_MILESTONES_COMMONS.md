# Budget and Milestones for NGI Commons

## Grant request

```text
Application: 2026-06-133
Fund: NGI Zero Commons / Commons Fund
Project: PythiaLabs: Open Evidence Gates for High-Risk AI-Agent Actions
Requested amount: EUR 30,000
Repository: https://github.com/safal207/pythiaLabs
```

## Budget summary

| Area | Amount |
|---|---:|
| Evidence schema and specification | EUR 5,000 |
| CLI and library implementation | EUR 8,000 |
| Demo case library | EUR 8,000 |
| GitHub Actions prototype | EUR 4,000 |
| Documentation and reviewer report | EUR 5,000 |
| **Total** | **EUR 30,000** |

## Milestone 1 — Evidence schema v0.1

Duration: 1 month

Budget: EUR 5,000

Deliverables:

- JSON evidence schema v0.1;
- schema versioning notes;
- action proposal fields;
- authorization chain fields;
- evidence freshness fields;
- recovery and risk fields;
- decision output fields.

Acceptance checks:

- schema is public and documented;
- example ALLOW, BLOCK, and ESCALATE artifacts validate;
- limitations are explicit;
- reviewer can inspect evidence without running a hosted service.

## Milestone 2 — CLI and library path

Duration: 2 months

Budget: EUR 8,000

Deliverables:

- stable local command for evaluating evidence gates;
- library functions for gate evaluation;
- consistent decision output;
- stable stop reasons;
- basic packaging notes.

Acceptance checks:

- reviewer can run local commands;
- CLI returns deterministic output for fixtures;
- stop reasons are stable;
- invalid inputs fail safely.

## Milestone 3 — Demo case library

Duration: 2 months

Budget: EUR 8,000

Deliverables:

- at least 9 reproducible demo cases;
- 3 ALLOW cases;
- 3 BLOCK cases;
- 3 ESCALATE cases;
- coverage across AI coding, infrastructure, financial workflow, and public-sector or governance scenarios;
- expected output files.

Acceptance checks:

- each demo is replayable;
- each demo has expected output;
- evidence artifacts are generated;
- tampering or missing evidence changes the decision.

## Milestone 4 — GitHub Actions prototype

Duration: 1 month

Budget: EUR 4,000

Deliverables:

- reusable workflow prototype;
- CI evidence gate example;
- sample policy file;
- documentation for integration into a repository.

Acceptance checks:

- demo workflow can run in GitHub Actions;
- failing evidence causes a clear CI failure;
- passing evidence produces a clear CI success;
- limitations are documented.

## Milestone 5 — Documentation and public reviewer report

Duration: 1 month

Budget: EUR 5,000

Deliverables:

- README reviewer path;
- implementation guide;
- threat model;
- limitations document;
- public reviewer report;
- final grant report outline.

Acceptance checks:

- new reviewer can understand the project in under 10 minutes;
- docs distinguish validated behavior from targets;
- non-claims are explicit;
- roadmap is clear without overclaiming production readiness.

## Timeline

```text
Month 1: Evidence schema v0.1
Months 2-3: CLI and library path
Months 4-5: Demo case library
Month 6: GitHub Actions prototype and documentation/report
```

## Public outputs

The grant will produce:

- source code;
- schema files;
- CLI commands;
- reproducible demos;
- CI workflow prototype;
- expected output fixtures;
- evidence artifacts;
- threat model;
- reviewer report;
- implementation guide.

All outputs are intended to be released under libre/open-source licenses compatible with the submitted proposal.

## Success definition

The project is successful if an independent reviewer can clone the repository, run the demos, inspect evidence artifacts, observe ALLOW / BLOCK / ESCALATE decisions, and understand how to reuse the evidence-gate pattern in another open-source AI-agent project.
