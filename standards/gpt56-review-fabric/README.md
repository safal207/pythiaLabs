# GPT-5.6 Review Fabric CI Standard v1

This standard turns every pull-request head into one deterministic, exact-head review request for five explicitly separated GPT-5.6 roles. It standardizes the **request, provenance, evidence, and authority boundary**. It does not pretend that CI itself performed an independent external review, and model output never grants approval or merge authority.

## Canonical roles

1. `causal_architect` — symptoms, causes, counterfactuals, downstream effects.
2. `temporal_provenance` — exact-head identity, freshness, ordering, supersession, valid/transaction time.
3. `adversarial_semantics` — ambiguous claims, hidden alternatives, semantic false positives, dissent.
4. `authority_safety` — review is not authorization; authorization is not execution; CI is not merge approval.
5. `ci_reliability` — deterministic checks, immutable dependencies, visible failures, recovery, artifact integrity.

## Non-negotiable CI principles

- Every required pull-request run checks out the full current head SHA from the actual head repository.
- Required workflows have no path filters: a skipped check cannot masquerade as success.
- Workflow-level permissions are empty; the called job receives only `contents: read`.
- `pull_request_target`, inherited secrets, write permissions, and `continue-on-error` are forbidden.
- The reusable workflow and every external action are pinned to full commit SHAs.
- The trusted validator is checked out from `job.workflow_repository` at `job.workflow_sha`, not from the caller PR.
- The repository profile cannot remove or rename roles, collapse fact/observation/hypothesis, or grant authority.
- The request is generated twice and compared byte-for-byte.
- Missing artifacts fail closed; retained artifacts are bound by SHA-256 manifest.
- GPT-5.6 output is advisory. A human maintainer still owns approval and merge.

## Adoption contract

Each repository adds:

- `.gpt56/review-profile.json` — bounded local focus, fixed roles, advisory-only authority;
- `.github/workflows/gpt56-review-fabric.yml` — a thin caller pinned to the exact standard commit SHA.

The central workflow emits:

- `exact-head.json`;
- `review-request.json`;
- `evidence-manifest.json`.

The artifact is a stable input for one GPT-5.6 Thinking model running the five role contracts. Any resulting panel must disclose single-model role simulation and preserve dissent. External-provider silence cannot be converted into independent-review evidence.

## Deliberate boundary

This v1 does not call a model API from CI, consume secrets, approve code, publish comments, or merge pull requests. That separation prevents untrusted PR content or probabilistic model output from becoming an execution authority. A later publisher may consume the exact-head request only after identity, freshness, stale-run, and mutation controls are independently proven.
