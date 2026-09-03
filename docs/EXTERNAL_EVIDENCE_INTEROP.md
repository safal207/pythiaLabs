# External evidence interoperability v0.1

PythiaLabs can ingest two portfolio artifacts as advisory context:

- `org.contractgraph-qa.liminalqa-evidence.v0.1`
- `org.liminalqa.cgqa-candidates.v0.1`

```bash
mix pythia.eval_external_evidence --file cgqa-evidence.json
mix pythia.eval_external_evidence --file liminal-candidates.json
./bin/pythia evidence --file cgqa-evidence.json
cat cgqa-evidence.json | ./bin/pythia evidence
```

A valid input always produces:

- `outcome=ESCALATE`
- `status=advisory_only`
- `stopReason=current_authorization_required`
- `mayAuthorizeAction=false`
- `sideEffectExecuted=false`

The next gate must separately check current authorization, credential scope,
environment state, and recovery readiness. An external finding, an old `ALLOW`,
a schema-valid candidate, or a matching digest cannot independently authorize
an action.

Invalid, unknown, temporally inverted, or ambiguous input is blocked. The JSON
boundary decodes ordered objects first so duplicate keys are detected before
map normalization. Exact top-level profiles, full commit SHAs, operation and
attempt identity, timestamps, status counts, critical authority flags, and
artifact digests are validated.

Consumer contracts under `schemas/interop/*.external-contract.json` pin the
exact producer commit and schema SHA-256. The assessment exposes the matching
`source.schemaSha256` so a reviewer can see which contract the adapter applied.

The Pythia-owned output schema is
[`schemas/interop/pythialabs-external-evidence-assessment-v0.1.schema.json`](../schemas/interop/pythialabs-external-evidence-assessment-v0.1.schema.json).

This adapter is local and file-first. It performs no tool call, network request,
or target-system side effect.

The Node stdio MCP adapter exposes the same boundary as
`pythia_evaluate_external_evidence`; it forwards the raw JSON string to the
canonical Elixir validator so duplicate-key handling and verdict semantics stay
in one implementation.

## Portable CGQA/LiminalQA conformance

Pythia also vendors the language-neutral `cgqa-liminalqa-v0.1` suite
byte-for-byte and runs it through the native Elixir boundary:

```bash
mix pythia.cgqa_conformance
mix pythia.cgqa_conformance \
  --suite conformance/cgqa-liminalqa-v0.1/suite.json
```

The suite SHA-256 is
`562e2f9ae699f001b9ccf1b2b9f6dd30c435d53d668b5fd9a04ca15ca1e4faac`.
The runner verifies that manifest, both schemas, both fixtures, every generated
case input, and their declared hashes before the adapter evaluates a vector.
Its report is deterministic, non-authorizing evidence only, and records
`sideEffectExecuted=false` for all 14 vectors.

Shared [TypeScript/JavaScript, Go, JVM, and .NET report adapters](https://github.com/safal207/ContractGraph-QA/blob/main/sdks/README.md)
let application teams consume that report without reimplementing Pythia,
LiminalQA, or CGQA verdict logic. A successful SDK validation still returns
`mayAuthorizeAction=false`; only a fresh Pythia/operator gate may authorize a
real action.

Passing this synthetic corpus establishes compatibility only for the pinned
fixtures and mutations. It does not validate a production system, prove
security or completeness, authorize an action, or replace independent replay
against the exact subject.
