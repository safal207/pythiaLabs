# Contributor Task Map

Status: contributor-facing navigation note.

This document helps new contributors choose safe, bounded tasks in PythiaLabs.

## Why this exists

PythiaLabs contains demos, evidence artifacts, docs, site code, and research notes.

Not every task is equally safe for a first contribution.

Use this map to keep early contributions small, reviewable, and aligned with the project's scope boundaries.

## Level 1 — beginner-friendly docs tasks

Good first tasks usually involve navigation, links, typo fixes, small glossary improvements, and README/docs index cleanup.

Examples:

- add or fix a docs link;
- improve wording in a short documentation section;
- add a glossary cross-link;
- clarify a README navigation path;
- fix stale references in docs.

Rules:

- keep the PR small;
- prefer README-only or docs-only changes;
- avoid changing site/build/runtime files;
- avoid changing demo engine behavior;
- avoid changing pricing or commercial copy unless explicitly requested.

## Level 2 — reviewer workflow tasks

These tasks require more context, but should still remain docs/process-only unless the issue explicitly says otherwise.

Examples:

- add reviewer path tables;
- add docs-only PR review checklists;
- improve evidence artifact navigation;
- link reviewer docs from the docs index;
- clarify limitations and non-claims.

Rules:

- stay within the issue scope;
- use existing docs as source material;
- avoid introducing new safety/compliance claims;
- link to existing expected-output or schema docs when possible.

## Level 3 — advanced reviewer / research tasks

These tasks are more sensitive because they may touch grant framing, evaluation artifacts, safety boundaries, or reviewer-facing reports.

Examples:

- sample reviewer reports;
- deterministic artifact inspection checklists;
- synthetic evidence examples;
- grant-readiness docs;
- positioning documents;
- safety-boundary notes.

Rules:

- use conservative wording;
- include limitations / non-claims;
- use sanitized examples only;
- do not include real user data;
- do not claim production security, certified compliance, or complete agent safety;
- do not change runtime/demo behavior unless the issue explicitly requests it.

## Scope categories

| Scope | Safer for first PR? | Notes |
|---|---:|---|
| README-only | Yes | Best for first contributors. |
| Docs-only | Yes | Preferred for Level 1 and Level 2 tasks. |
| Site copy | Maybe | Requires checking build and localization impact. |
| Site build/layout | No | Needs maintainer review. |
| Demo examples | Maybe | Must preserve deterministic behavior. |
| Demo engine/runtime | No | Requires strong validation. |
| GitHub Actions/workflows | No | Security-sensitive. |
| Pricing/commercial offer | No | Requires explicit maintainer request. |
| Security/integration | No | Requires threat-model notes and narrow scope. |

## Maintainer review expectations

A good contributor PR should include:

- short summary;
- linked issue;
- scope statement;
- note on what was not changed;
- screenshots only if site/UI changed;
- validation command if relevant.

## Recommended first contribution format

```text
Summary:
- Added/updated docs link for <topic>.

Scope:
- Docs-only.
- No site/build/runtime/demo changes.

Validation:
- Markdown-only change; no runtime validation needed.
```

## Safety boundaries

Contributors should avoid claims that PythiaLabs provides:

- production security certification;
- regulatory compliance certification;
- wallet security;
- smart-contract auditing;
- transaction simulation;
- complete AI-agent safety;
- medical, legal, financial, or clinical advice.

For the full scope boundary, see:

```text
docs/NON_CLAIMS.md
```

## Bottom line

Small, careful, docs-only contributions are welcome.

The best first PR improves reviewer comprehension without expanding the project's claims.
