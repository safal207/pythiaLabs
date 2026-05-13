# Liminal Audit Bridge

Petri-like behavioral audit transcript -> T-Trace JSONL -> causal/risk checks -> Markdown audit report.

This integration turns external agent-audit transcripts into PythiaLabs-style evidence artifacts.

It is intentionally small and dependency-free. The goal is to make audit evidence replayable, comparable, and easier to connect to deterministic action gates.

## Positioning

Petri-style audits can find risky behavior.

Liminal Audit Bridge traces why that behavior became possible.

```text
Behavioral audit run
  -> transcript events
  -> T-Trace records
  -> CML/CaPU-style starter checks
  -> reviewer-facing report
```

## Quickstart

```bash
cd integrations/liminal_audit_bridge
PYTHONPATH=src python -m liminal_audit_bridge run examples/petri_like_transcript.json \
  --trace-out examples/audit.ttrace.jsonl \
  --decisions-out examples/decisions.json \
  --report-out examples/audit_report.md
```

Expected final decision for the included sample:

```text
HOLD
```

## Input shape

The starter parser accepts a simple JSON document:

```json
{
  "audit_id": "audit-run-001",
  "target": "example-agent",
  "events": [
    {
      "id": "turn-001",
      "type": "message",
      "actor": "auditor",
      "content": "...",
      "risk": { "deception": 0.12 }
    }
  ]
}
```

## Decision semantics

- `ACCEPT` — no material risk signal found by the starter checks.
- `HOLD` — needs review or stronger causal evidence.
- `BLOCK` — high-risk audit evidence found.

## Current starter checks

- high and medium judge-risk scores
- eval-awareness signals
- rollback / branch events
- tool or action-like events
- action-like events before an explicit commit record
- low positive-behavior scores such as honesty, helpfulness, or corrigibility

## Status

This is a deterministic local integration module, not a production safety verdict or certified compliance system.
