# Lotus Family causal traceability

The causality graph is the primary behavioral model. This table is the human-readable coverage ledger. A route is valid only when each adjacent node pair is an edge in `lotus-family-causality-v0.1.json`, and the route executes to the declared outcome in `test_causality_model.py`.

## Policy

- New blockers add or reuse a causal node before a regression route is accepted.
- `PASS` routes must reach evidence produced from the same bytes that were evaluated.
- `DRIFT` routes model a broken invariant or a false-positive CI path.
- `UNKNOWN` routes model evidence that cannot be evaluated safely.
- All outcomes remain advisory and grant no merge or execution authority.

## Routes

| Route | Repository | Scenario | Expected | Causal path |
|---|---|---|---|---|
| `CML-PASS-001` | `cml` | `valid` | `PASS` | input.snapshot_present → input.identity_claims_well_formed → limitation.identity_unverified → control.manifest_valid → control.contract_terms_present → control.workflow_job_runnable → control.step_enabled → control.direct_run → control.test_env_clean → control.shell_straight_line → control.contract_test_selected → evidence.same_bytes_hashed → outcome.pass → authority.advisory_only |
| `LS-PASS-001` | `ls` | `valid` | `PASS` | input.snapshot_present → input.identity_claims_well_formed → limitation.identity_unverified → control.manifest_valid → control.contract_terms_present → control.workflow_job_runnable → control.step_enabled → control.direct_run → control.test_env_clean → control.shell_straight_line → control.contract_test_selected → evidence.same_bytes_hashed → outcome.pass → authority.advisory_only |
| `PYTHIA-PASS-001` | `pythia` | `valid` | `PASS` | input.snapshot_present → input.identity_claims_well_formed → limitation.identity_unverified → control.manifest_valid → control.contract_terms_present → control.workflow_job_runnable → control.step_enabled → control.direct_run → control.test_env_clean → control.shell_straight_line → control.contract_test_selected → evidence.same_bytes_hashed → outcome.pass → authority.advisory_only |
| `CI-NONRUN-001` | `cml` | `workflow` | `DRIFT` | input.snapshot_present → input.identity_claims_well_formed → limitation.identity_unverified → control.manifest_valid → control.contract_terms_present → control.workflow_job_runnable → control.step_enabled → control.non_run_text → risk.false_ci_pass → outcome.drift |
| `CI-STEP-SKIP-001` | `cml` | `workflow` | `DRIFT` | input.snapshot_present → input.identity_claims_well_formed → limitation.identity_unverified → control.manifest_valid → control.contract_terms_present → control.workflow_job_runnable → control.step_skipped → risk.false_ci_pass → outcome.drift |
| `CI-JOB-SKIP-001` | `cml` | `workflow` | `DRIFT` | input.snapshot_present → input.identity_claims_well_formed → limitation.identity_unverified → control.manifest_valid → control.contract_terms_present → control.workflow_job_not_runnable → risk.false_ci_pass → outcome.drift |
| `CI-NO-RUNNER-001` | `cml` | `workflow` | `DRIFT` | input.snapshot_present → input.identity_claims_well_formed → limitation.identity_unverified → control.manifest_valid → control.contract_terms_present → control.workflow_job_not_runnable → risk.false_ci_pass → outcome.drift |
| `CI-QUOTED-ENV-001` | `cml` | `workflow` | `DRIFT` | input.snapshot_present → input.identity_claims_well_formed → limitation.identity_unverified → control.manifest_valid → control.contract_terms_present → control.workflow_job_runnable → control.step_enabled → control.direct_run → control.test_env_override → risk.false_ci_pass → outcome.drift |
| `CI-SHELL-CONTROL-001` | `cml` | `workflow` | `DRIFT` | input.snapshot_present → input.identity_claims_well_formed → limitation.identity_unverified → control.manifest_valid → control.contract_terms_present → control.workflow_job_runnable → control.step_enabled → control.direct_run → control.test_env_clean → control.shell_control_flow → risk.false_ci_pass → outcome.drift |
| `CML-SUBSET-001` | `cml` | `workflow` | `DRIFT` | input.snapshot_present → input.identity_claims_well_formed → limitation.identity_unverified → control.manifest_valid → control.contract_terms_present → control.workflow_job_runnable → control.step_enabled → control.direct_run → control.test_env_clean → control.shell_straight_line → control.contract_test_excluded → risk.false_ci_pass → outcome.drift |
| `PYTHIA-SUBSET-001` | `pythia` | `workflow` | `DRIFT` | input.snapshot_present → input.identity_claims_well_formed → limitation.identity_unverified → control.manifest_valid → control.contract_terms_present → control.workflow_job_runnable → control.step_enabled → control.direct_run → control.test_env_clean → control.shell_straight_line → control.contract_test_excluded → risk.false_ci_pass → outcome.drift |
| `CI-FAKE-STEPS-001` | `cml` | `workflow` | `DRIFT` | input.snapshot_present → input.identity_claims_well_formed → limitation.identity_unverified → control.manifest_valid → control.contract_terms_present → control.workflow_job_not_runnable → risk.false_ci_pass → outcome.drift |
| `IDENTITY-INVALID-001` | `cml` | `invalid_commit` | `UNKNOWN` | input.snapshot_present → input.identity_claims_invalid → outcome.unknown |
| `SNAPSHOT-MISSING-001` | `cml` | `missing_snapshot` | `UNKNOWN` | input.snapshot_missing → outcome.unknown |
| `CONTRACT-DRIFT-001` | `cml` | `missing_term` | `DRIFT` | input.snapshot_present → input.identity_claims_well_formed → limitation.identity_unverified → control.manifest_valid → control.contract_terms_missing → outcome.drift |
| `IDENTITY-LIMIT-001` | `cml` | `valid` | `PASS` | input.snapshot_present → input.identity_claims_well_formed → limitation.identity_unverified → risk.identity_overclaim → authority.advisory_only |
| `MANIFEST-INVALID-001` | `cml` | `invalid_manifest` | `UNKNOWN` | control.manifest_invalid → outcome.unknown |

## Coverage interpretation

Node coverage shows that a condition or decision is represented. Edge coverage shows that a causal relationship is exercised. Route coverage shows that an end-to-end behavioral path reaches the expected `PASS`, `DRIFT`, or `UNKNOWN` result. The matrix remains useful for review and audit, but it is derived from the causal routes rather than acting as the source of truth.
