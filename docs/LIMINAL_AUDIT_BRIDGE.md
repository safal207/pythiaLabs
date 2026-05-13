# Liminal Audit Bridge

**Petri-like behavioral audit transcript -> T-Trace JSONL -> causal/risk checks -> Markdown audit report.**

Liminal Audit Bridge is a small integration module for turning external agent-audit transcripts into PythiaLabs-style evidence artifacts.

It does not assume privileged access to model internals. It works from behavioral evidence: messages, tool events, rollback markers, branch events, and judge scores.

## Why this belongs in PythiaLabs

PythiaLabs gates high-risk agent actions before tools are called. External audit systems can find suspicious behavior, but raw transcripts are often hard to replay, compare, or connect to deterministic action gates.

Liminal Audit Bridge adds the missing adapter layer:

```text
Behavioral audit run
  -> Petri-like transcript / Inspect-like sample
  -> T-Trace JSONL records with hash-chain seals
  -> Starter CML/CaPU-style checks
  -> Human-readable audit report
```

Core positioning:

> Petri-style audits find risky behavior. Liminal traces why it became possible.

## What it checks today

The first version is deliberately small and inspectable. It surfaces:

- high and medium judge-risk scores
- eval-awareness signals
- rollback / branch events
- tool or action-like events
- action-like events that appear before an explicit commit record
- low positive-behavior scores on dimensions such as helpfulness, honesty, or corrigibility

It emits CaPU-like decisions:

- `ACCEPT` — no material risk signal found by starter checks
- `HOLD` — needs review or stronger causal evidence
- `BLOCK` — high-risk audit evidence found

## Integration location

Code lives in:

```text
integrations/liminal_audit_bridge/
```

Quick command:

```bash
cd integrations/liminal_audit_bridge
PYTHONPATH=src python -m liminal_audit_bridge run examples/petri_like_transcript.json \
  --trace-out examples/audit.ttrace.jsonl \
  --decisions-out examples/decisions.json \
  --report-out examples/audit_report.md
```

## Next steps

1. Add a parser for real Inspect/Petri `.eval` exports once a sample is available.
2. Connect `ACTION_BEFORE_EXPLICIT_COMMIT` and related findings to canonical PythiaLabs / CML invariants.
3. Add trace verification compatibility with the broader T-Trace toolchain.
4. Publish generated reports as CI artifacts for reviewer-friendly demos.
5. Add a paid-pilot workflow: customer transcript/log sample -> audit bridge -> report -> hardening recommendations.

## Status

This is a deterministic local integration module, not a production safety verdict, certified compliance system, or final replacement for model evaluations.
