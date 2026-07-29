# Agent Authority Boundary Pilot — launch status

Date: 2026-07-29

## Completed preflight

- The bundled `synthetic_results.jsonl` was validated with the repository's `score_results.py`.
- All 9 synthetic records were accepted.
- The scorer produced the expected point-estimate separation:
  - baseline Unauthorized Execution Rate: `1.0`;
  - CAEP-gate Unauthorized Execution Rate: `0.0`;
  - baseline Legitimate Escalation Retention: `1.0`;
  - CAEP-gate Legitimate Escalation Retention: `1.0`.

These numbers are fixture validation only. They are not empirical model results and must not be used as a public effectiveness claim.

## Pilot runner

The manual GitHub Actions workflow `.github/workflows/caep-authority-boundary-pilot.yml` is the canonical launch path.

Default matrix:

```text
4 scenario seeds × 3 conditions × 5 epochs = 60 runs
```

Conditions:

- `baseline`;
- `prompt_only`;
- `caep_gate`.

## Required before launch

Repository Actions secrets must exist for the selected provider model IDs. With the workflow defaults, the required secrets are:

- `ANTHROPIC_API_KEY`;
- `OPENAI_API_KEY`.

A publication candidate should pin the Petri installation input to an exact PyPI version or Git commit.

## After the raw run

The raw Inspect logs must be reviewed and converted into benchmark JSONL records. Before a public comparative claim, the pilot still requires:

1. structured attempted-versus-dispatched action classification;
2. an exclusion ledger for incomplete or failed runs;
3. manual review of every human-proxy classification;
4. at least one reviewed transcript per scenario and condition;
5. confidence intervals;
6. scorer output generated from the structured run records;
7. explicit limitations and exact commit/version references.
