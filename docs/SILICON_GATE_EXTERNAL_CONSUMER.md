# External Silicon Evidence Gate Consumer

This repository consumes the released PythiaLabs Silicon Evidence Gate from a separate repository and immutable tag:

```yaml
uses: safal207/ibex-agent-verification@v0.7.0
```

No gate implementation is copied into `pythiaLabs`. The consumer only creates evidence inputs and verifies the external action contract.

## Why this matters

A self-test inside `ibex-agent-verification` proves the action works in its source repository. This workflow proves the distribution boundary:

- another public repository resolves the immutable release tag;
- the released composite action runs from its own action path;
- evidence paths remain relative to the consumer workspace;
- outputs cross the repository boundary correctly;
- observe-only and enforcing policies behave as documented;
- the generated decision reports remain independently hashable.

## Scenarios

The consumer fixture builder creates two commit-bound requests.

### ALLOW

Evidence contains:

- architectural trace status `MATCH`;
- no timing regressions;
- no delayed redirect regressions;
- a manifest bound to the PythiaLabs workflow commit.

Expected result:

```text
ALLOW / NO_EVIDENCE_REGRESSION
```

### BLOCK

The architectural trace still matches and the manifest remains correctly bound. The only intentional defect is one new timing anomaly with `primary_cause: UNKNOWN`.

Expected result:

```text
BLOCK / NEW_UNEXPLAINED_TIMING_ANOMALY
```

The same BLOCK request is executed twice:

1. observe-only with `fail_on_block: "false"`, which publishes outputs without failing;
2. enforcing mode, which publishes the decision and then fails the composite action policy step.

## Workflow contract

The workflow verifies:

- `decision` and `reason_codes` outputs;
- SHA-256 of the generated reports;
- successful ALLOW execution;
- successful observe-only BLOCK execution;
- failed enforcing BLOCK execution;
- JSON reports for all three action calls.

It writes:

```text
artifacts/silicon-gate-consumer/
├── allow/
│   ├── evidence/
│   ├── gate-request.json
│   └── gate-decision.json
├── block/
│   ├── evidence/
│   ├── gate-request.json
│   ├── gate-observe-decision.json
│   └── gate-enforce-decision.json
├── consumer-input-summary.json
└── external-consumer-summary.json
```

The complete directory is uploaded for 14 days as:

```text
pythialabs-external-silicon-gate-<consumer-commit>
```

## Boundary

These generated fixtures validate packaging, distribution, policy behavior, outputs, and evidence integrity. They are not a hardware simulation and do not replace the real firmware and RTL demonstrations maintained in `ibex-agent-verification`.
