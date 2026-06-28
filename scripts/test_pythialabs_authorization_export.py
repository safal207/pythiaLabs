#!/usr/bin/env python3
"""Adversarial checks for the PythiaLabs authorization export verifier."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

CHECKER_PATH = Path("scripts/check_pythialabs_authorization_export.py")
FIXTURE_PATH = Path("conformance/pythialabs-authorization-export-v0.1.json")


def load_checker() -> Any:
    """Load the checker as a module without changing its CLI contract."""
    spec = importlib.util.spec_from_file_location("pythia_export_checker", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load authorization export checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_case(data: dict[str, Any], case_id: str) -> dict[str, Any]:
    """Return a deep copy of one fixture case."""
    for case in data["cases"]:
        if case["case_id"] == case_id:
            return copy.deepcopy(case)
    raise AssertionError(f"missing case: {case_id}")


def require_failure(
    checker: Any,
    case: dict[str, Any],
    validator: Any,
    adapters: dict[str, Any],
    expected_fragment: str,
) -> None:
    """Assert that a tampered case is rejected for the intended reason."""
    try:
        checker.verify(case, validator, adapters)
    except checker.FixtureError as error:
        if expected_fragment not in str(error):
            raise AssertionError(
                f"unexpected rejection: {error}; wanted {expected_fragment!r}"
            ) from error
        return
    raise AssertionError(f"tampered case unexpectedly passed: {case['case_id']}")


def main() -> int:
    """Run canonicalization, state, join, and schema negative checks."""
    checker = load_checker()
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    validator = checker.load_schema_validator()
    adapters = data["showcase_adapters"]

    if checker.canonical({"x": 1e-7}) != b'{"x":1e-7}':
        raise AssertionError("RFC 8785 number canonicalization regression")

    expired = find_case(data, "expired_temporal_authorization")
    expired["expected"]["authority_state"] = "ACTIVE"
    require_failure(
        checker,
        expired,
        validator,
        adapters,
        "authority_state mismatch",
    )

    contradicted = find_case(data, "accepted_with_contradicted_external_response")
    contradicted["handoff"]["expected_join"] = "MATCH"
    require_failure(
        checker,
        contradicted,
        validator,
        adapters,
        "expected_join mismatch",
    )

    malformed = find_case(data, "accepted_reversible_infrastructure")
    malformed["input"]["source_showcase"] = "unknown-showcase"
    require_failure(
        checker,
        malformed,
        validator,
        adapters,
        "schema violation",
    )

    print("Adversarial PythiaLabs authorization export checks passed: 4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
