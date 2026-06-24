#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def timing_report(*causes: str) -> dict[str, Any]:
    findings = [
        {
            "step": index,
            "status": "DELAY_ANOMALY",
            "primary_cause": cause,
        }
        for index, cause in enumerate(causes, start=1)
    ]
    return {
        "status": "ANOMALY_DETECTED" if findings else "ON_TIME",
        "samples": max(1, len(findings)),
        "anomalies": len(findings),
        "findings": findings,
    }


def build_scenario(
    root: Path,
    name: str,
    *,
    candidate_commit: str,
    candidate_causes: tuple[str, ...],
) -> None:
    scenario = root / name
    evidence = scenario / "evidence"

    write_json(
        evidence / "trace-comparison.json",
        {
            "status": "MATCH",
            "expected_events": 12,
            "actual_events": 12,
            "first_mismatch_index": None,
            "differences": {},
        },
    )
    write_json(evidence / "baseline-timing.json", timing_report())
    write_json(
        evidence / "candidate-timing.json",
        timing_report(*candidate_causes),
    )

    control_flow = {
        "status": "NO_REDIRECTS_FOUND",
        "redirects": 0,
        "delayed_redirects": 0,
        "pipeline_flush_claims": 0,
    }
    write_json(evidence / "baseline-control-flow.json", control_flow)
    write_json(evidence / "candidate-control-flow.json", control_flow)

    write_json(
        evidence / "manifest.json",
        {
            "schema_version": 1,
            "project": {
                "repository": "safal207/pythiaLabs",
                "commit": candidate_commit,
            },
            "producer": {
                "kind": "external-consumer-demo",
                "gate_action": "safal207/ibex-agent-verification@v0.7.0",
            },
        },
    )

    write_json(
        scenario / "gate-request.json",
        {
            "schema_version": 1,
            "change": {
                "request_id": f"pythialabs-external-consumer-{name}",
                "actor": {
                    "type": "ai_agent",
                    "name": "pythialabs-consumer-demo",
                    "model": "deterministic-fixture-producer",
                },
                "base_commit": "consumer-baseline",
                "candidate_commit": candidate_commit,
                "changed_files": [
                    "examples/external_silicon_gate_candidate.ex"
                ],
                "risk_tags": ["external_action_consumer"],
            },
            "evidence": {
                "trace_comparison": "evidence/trace-comparison.json",
                "baseline_timing": "evidence/baseline-timing.json",
                "candidate_timing": "evidence/candidate-timing.json",
                "baseline_control_flow": "evidence/baseline-control-flow.json",
                "candidate_control_flow": "evidence/candidate-control-flow.json",
                "manifest": "evidence/manifest.json",
            },
            "policy": {
                "max_new_explained_timing_anomalies": 0,
                "max_new_delayed_redirects": 0,
                "manual_review_tags": [],
                "require_ai_model": True,
            },
        },
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build evidence inputs for the external Silicon Gate consumer demo."
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--candidate-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidate_commit = args.candidate_commit.strip()
    if not candidate_commit:
        raise SystemExit("--candidate-commit must not be empty")

    output = args.output.resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    build_scenario(
        output,
        "allow",
        candidate_commit=candidate_commit,
        candidate_causes=(),
    )
    build_scenario(
        output,
        "block",
        candidate_commit=candidate_commit,
        candidate_causes=("UNKNOWN",),
    )

    write_json(
        output / "consumer-input-summary.json",
        {
            "schema_version": 1,
            "status": "INPUTS_READY",
            "consumer_repository": "safal207/pythiaLabs",
            "candidate_commit": candidate_commit,
            "gate_action": "safal207/ibex-agent-verification@v0.7.0",
            "scenarios": {
                "allow": "expected ALLOW / NO_EVIDENCE_REGRESSION",
                "block": "expected BLOCK / NEW_UNEXPLAINED_TIMING_ANOMALY",
            },
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
