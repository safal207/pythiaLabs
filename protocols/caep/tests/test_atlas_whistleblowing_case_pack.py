from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CAEP_DIR = ROOT / "protocols" / "caep"
CASE_DIR = CAEP_DIR / "cases" / "atlas-whistleblowing"
sys.path.insert(0, str(CAEP_DIR / "tools"))

from validate_caep_strict import validate_packet  # noqa: E402


def load_fixture(name: str) -> dict:
    with (CASE_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


class AtlasWhistleblowingCasePackTests(unittest.TestCase):
    def test_all_published_fixtures_validate(self) -> None:
        for name in (
            "internal_escalation_allowed.json",
            "external_disclosure_denied.json",
            "human_proxy_disclosure_denied.json",
        ):
            with self.subTest(name=name):
                errors, warnings = validate_packet(load_fixture(name))
                self.assertEqual([], errors)
                self.assertEqual([], warnings)

    def test_internal_escalation_is_allowed_and_observed(self) -> None:
        packet = load_fixture("internal_escalation_allowed.json")
        record_types = [record["record_type"] for record in packet["records"]]
        authorization = next(
            record for record in packet["records"]
            if record["record_type"] == "authorization"
        )
        outcome = next(
            record for record in packet["records"]
            if record["record_type"] == "outcome"
        )

        self.assertEqual("ALLOW", authorization["decision"])
        self.assertEqual(
            ["intent", "authorization", "dispatch", "outcome"],
            record_types,
        )
        self.assertEqual("CONFORMANT", outcome["policy_conformance"])

    def test_external_disclosure_is_denied_without_dispatch(self) -> None:
        packet = load_fixture("external_disclosure_denied.json")
        authorization = next(
            record for record in packet["records"]
            if record["record_type"] == "authorization"
        )

        self.assertEqual("DENY", authorization["decision"])
        self.assertNotIn(
            "dispatch",
            {record["record_type"] for record in packet["records"]},
        )

    def test_human_proxy_bypass_is_denied_without_dispatch(self) -> None:
        packet = load_fixture("human_proxy_disclosure_denied.json")
        intent = next(
            record for record in packet["records"]
            if record["record_type"] == "intent"
        )
        authorization = next(
            record for record in packet["records"]
            if record["record_type"] == "authorization"
        )

        self.assertIn("human_proxy.external_disclosure", intent["requested_capabilities"])
        self.assertEqual("DENY", authorization["decision"])
        self.assertNotIn(
            "dispatch",
            {record["record_type"] for record in packet["records"]},
        )

    def test_post_authorization_recipient_drift_fails_closed(self) -> None:
        packet = copy.deepcopy(load_fixture("internal_escalation_allowed.json"))
        dispatch = next(
            record for record in packet["records"]
            if record["record_type"] == "dispatch"
        )
        dispatch["actual_target_resource"] = "mailto:external-audit-team@example.org"
        dispatch["network_destination"] = "external-audit-team.example.org:443"

        errors, _ = validate_packet(packet)

        self.assertTrue(
            any("actual_target_resource" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("network_destination" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
