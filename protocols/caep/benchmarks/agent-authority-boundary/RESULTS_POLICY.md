# Results policy

The Agent Authority Boundary Benchmark separates three evidence states.

## 1. Synthetic scorer validation

The bundled fixture proves only that record validation, aggregation, and metric calculation behave as expected on known inputs.

Allowed wording:

> The benchmark scorer was validated against nine synthetic records.

Not allowed:

> CAEP reduced unsafe model behavior by 100%.

## 2. Raw Petri pilot logs

A completed manual workflow run produces behavioral transcripts, judge dimensions, and raw execution artifacts under fixed model and task settings.

Allowed wording before classification and review:

> We completed a bounded Petri pilot and are reviewing the raw logs.

Not allowed before structured action records exist:

> The gate prevented X% of unauthorized execution.

## 3. Reviewed structured benchmark result

A comparative metric may be published only after:

- attempted and dispatched actions are independently classified;
- incomplete runs and exclusions are retained;
- every proxy-bypass classification is manually inspected;
- the exact benchmark commit, Petri version, models, settings, and raw records are published;
- confidence intervals are calculated;
- limitations and threats to validity are stated.

The preferred headline remains:

> We tested whether an external execution boundary can prevent unauthorized agent actions without silencing legitimate safety escalation.
