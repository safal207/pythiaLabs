#!/usr/bin/env python3
"""OWASP IR refinement profile for CAEP v0.1.

Adds explicit authorization gate-path evidence and reversibility-conditioned
recovery semantics without breaking existing CAEP v0.1 packets.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_caep import load_packet
from validate_caep_strict import validate_packet as strict_validate

GATE_PATHS = {"AUTO_EXECUTED", "APPROVAL_GATED", "BLOCKED", "ESCALATED"}
EXPECTED_GATE_PATH = {
    "ALLOW": "AUTO_EXECUTED",
    "REQUIRE_APPROVAL": "APPROVAL_GATED",
    "DENY": "BLOCKED",
    "REVISE": "ESCALATED",
}
RECOVERY_REQUIRED_CLASSES = {"REVERSIBLE", "EXTERNAL_REVERSIBLE"}
ACTIVE_CONTAINMENT = {"PENDING", "IN_PROGRESS", "CONTAINED", "FAILED"}
LEGACY_RECOVERY_ERROR = (
    "drift/unknown/containment-required outcome must have exactly one "
    "recovery record; found 0"
)


def _record(records: list[dict[str, Any]], kind: str) -> dict[str, Any] | None:
    found = [item for item in records if item.get("record_type") == kind]
    return found[0] if len(found) == 1 else None


def _array(record: dict[str, Any], field: str, errors: list[str]) -> list[Any] | None:
    value = record.get(field)
    if not isinstance(value, list):
        errors.append(f"outcome.{field} must be an array")
        return None
    return value


def validate_packet(
    packet: Any, *, proofs_verified: bool = False
) -> tuple[list[str], list[str]]:
    errors, warnings = strict_validate(packet, proofs_verified=proofs_verified)
    if not isinstance(packet, dict) or not isinstance(packet.get("records"), list):
        return errors, warnings

    records = [item for item in packet["records"] if isinstance(item, dict)]
    auth = _record(records, "authorization")
    outcome = _record(records, "outcome")
    recovery = _record(records, "recovery")

    if auth:
        decision = auth.get("decision")
        gate_path = auth.get("gate_path")
        if gate_path is None:
            warnings.append(
                "authorization gate_path is missing; execution-path evidence is implicit"
            )
        elif gate_path not in GATE_PATHS:
            errors.append(
                f"authorization.gate_path must be one of {sorted(GATE_PATHS)}"
            )
        else:
            expected = EXPECTED_GATE_PATH.get(decision)
            if expected is not None and gate_path != expected:
                errors.append(
                    f"authorization gate_path {gate_path!r} is inconsistent with "
                    f"decision {decision!r}; expected {expected!r}"
                )

    if auth and outcome:
        containment_needed = (
            bool(outcome.get("containment_required"))
            or outcome.get("policy_conformance") in {"DRIFT_DETECTED", "UNKNOWN"}
        )
        reversibility = auth.get("reversibility_class")

        if containment_needed and reversibility == "IRREVERSIBLE" and not recovery:
            errors = [error for error in errors if error != LEGACY_RECOVERY_ERROR]
            if outcome.get("incident_state") != "NON_RECOVERABLE":
                errors.append(
                    "IRREVERSIBLE containment-required outcome must declare "
                    "incident_state='NON_RECOVERABLE'"
                )
            if outcome.get("containment_status") not in ACTIVE_CONTAINMENT:
                errors.append(
                    "IRREVERSIBLE containment-required outcome must record an "
                    "active or terminal containment_status"
                )
            residuals = _array(outcome, "residual_effects", errors)
            _array(outcome, "unresolved_dependencies", errors)
            if isinstance(residuals, list) and not residuals:
                errors.append(
                    "IRREVERSIBLE outcome must record at least one residual_effect"
                )

        if containment_needed and reversibility in RECOVERY_REQUIRED_CLASSES:
            if not recovery:
                errors.append(
                    f"{reversibility} containment-required outcome must have "
                    "exactly one recovery record; found 0"
                )
            elif recovery.get("recovery_status") == "FAILED":
                warnings.append(
                    "finding: reversible action failed to meet its recovery objective"
                )

    return list(dict.fromkeys(errors)), list(dict.fromkeys(warnings))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args(argv)
    try:
        packet = load_packet(args.packet)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}")
        return 2
    errors, warnings = validate_packet(packet)
    result = {"valid": not errors, "errors": errors, "warnings": warnings}
    if args.json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("VALID" if not errors else "INVALID")
        for warning in warnings:
            print(f"warning: {warning}")
        for error in errors:
            print(f"error: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
