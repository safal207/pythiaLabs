# Agent Authority Boundary Benchmark — launch checklist

Use this checklist for the first empirical pilot. It does not replace issue #252.

## Before running

- [ ] Merge the manual workflow runner.
- [ ] Add provider API keys as GitHub Actions repository secrets.
- [ ] Pin `petri_install_spec` to an exact version or commit.
- [ ] Confirm the auditor, target, and judge model IDs.
- [ ] Keep `epochs=5`, `max_turns=24`, and the same provider settings across all conditions.
- [ ] Record a budget ceiling with the account owner before starting the 60-run job.

## During the run

- [ ] Preserve failed and incomplete runs.
- [ ] Do not restart only inconvenient samples.
- [ ] Keep baseline, prompt-only, and CAEP-gate settings identical except for the registered treatment.
- [ ] Retain raw Inspect logs and the workflow manifest.

## After the run

- [ ] Build structured benchmark JSONL records.
- [ ] Verify dispatched counts never exceed attempted counts.
- [ ] Review all human-proxy classifications manually.
- [ ] Create an exclusion ledger.
- [ ] Select one transcript per scenario and condition for review.
- [ ] Run `score_results.py` on the structured records.
- [ ] Add confidence intervals before any comparative headline.
- [ ] Publish exact repository and Petri commits, models, settings, raw counts, exclusions, and limitations.

## Claim boundary

Until the structured records and review steps are complete, describe the output only as raw Petri pilot logs. Do not claim measured CAEP effectiveness from the bundled synthetic fixture.
