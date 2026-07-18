## What changed?

Briefly describe the changed gate, evidence path, policy surface, or documentation.

## Type of change

- [ ] Documentation
- [ ] Gate or verdict semantics
- [ ] Evidence artifact or verifier
- [ ] Authorization / credential / environment handling
- [ ] Recovery or escalation behavior
- [ ] Tests / CI / tooling

## Why it matters

Explain the reviewer, operator, safety, reproducibility, or human-governance value.

## Exact-head validation

**Exact PR head SHA validated:**

<!-- Paste the full 40-character PR head SHA covered by the evidence below. -->

**Validation command:**

```text

```

- [ ] Validation was run or rerun after the most recent PR head change.
- [ ] Evidence, screenshots, and expected output apply to the exact SHA above.

> Evidence becomes stale when the PR head, evaluated inputs, policy, environment, authorization, credential, or recovery context changes. Rerun validation before review or merge.

## Lotus judgment check 🌸

> **Does this judgment show its evidence, preserve uncertainty, and leave consequential action under explicit authority?**

- [ ] `ALLOW` is supported by positive authorization and evidence, not merely the absence of a blocking signal.
- [ ] Missing, stale, conflicting, or unavailable evidence remains visible and is not converted into confidence.
- [ ] The verdict does not secretly execute the proposed external action or manufacture authority.
- [ ] Stop reasons and evidence traces remain stable, replayable, and open to human challenge.

**Lotus note — one concrete sentence:**

<!-- Describe a real design choice or tradeoff. Example: "A missing recovery proof now produces ESCALATE with a stable stop reason instead of falling through to ALLOW." Write "Not applicable" only for genuinely routine maintenance. See LOTUS.md. -->

## Compatibility and authority

Describe changes to verdict semantics, schemas, policy inputs, authorization, credentials, replayability, or backward compatibility. State explicitly when there is no impact.

## Evidence

Add exact-head test output, replay traces, evidence artifacts, counterfactuals, or before/after examples.
