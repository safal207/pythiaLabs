from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_caep import load_packet  # noqa: E402
from validate_caep_ir import validate_packet  # noqa: E402


class OwaspIrFeedbackTests(unittest.TestCase):
    def fixture(self):
        return load_packet(
            ROOT / "examples" / "hypothetical_sandbox_escape_episode.json"
        )

    @staticmethod
    def authorization(packet):
        return next(
            record for record in packet["records"]
            if record["record_type"] == "authorization"
        )

    @staticmethod
    def outcome(packet):
        return next(
            record for record in packet["records"]
            if record["record_type"] == "outcome"
        )

    @staticmethod
    def recovery(packet):
        return next(
            record for record in packet["records"]
            if record["record_type"] == "recovery"
        )

    def test_missing_gate_path_is_an_explicit_evidence_warning(self):
        errors, warnings = validate_packet(self.fixture())
        self.assertEqual([], errors)
        self.assertTrue(
            any("gate_path is missing" in warning for warning in warnings),
            warnings,
        )

    def test_gate_path_must_match_decision(self):
        packet = self.fixture()
        self.authorization(packet)["gate_path"] = "BLOCKED"

        errors, _ = validate_packet(packet)

        self.assertTrue(
            any("gate_path" in error and "inconsistent" in error for error in errors),
            errors,
        )

    def test_irreversible_action_can_omit_recovery_with_explicit_incident_evidence(self):
        packet = self.fixture()
        auth = self.authorization(packet)
        outcome = self.outcome(packet)
        auth["gate_path"] = "AUTO_EXECUTED"
        auth["reversibility_class"] = "IRREVERSIBLE"
        outcome["incident_state"] = "NON_RECOVERABLE"
        outcome["containment_status"] = "CONTAINED"
        outcome["residual_effects"] = [
            "external disclosure cannot be recalled by the producing runtime"
        ]
        outcome["unresolved_dependencies"] = [
            "recipient-side deletion confirmation"
        ]
        packet["records"] = [
            record for record in packet["records"]
            if record["record_type"] != "recovery"
        ]

        errors, _ = validate_packet(packet)

        self.assertEqual([], errors)

    def test_irreversible_action_requires_non_recoverable_incident_state(self):
        packet = self.fixture()
        auth = self.authorization(packet)
        outcome = self.outcome(packet)
        auth["gate_path"] = "AUTO_EXECUTED"
        auth["reversibility_class"] = "IRREVERSIBLE"
        outcome["containment_status"] = "CONTAINED"
        outcome["residual_effects"] = ["external effect remains"]
        outcome["unresolved_dependencies"] = []
        packet["records"] = [
            record for record in packet["records"]
            if record["record_type"] != "recovery"
        ]

        errors, _ = validate_packet(packet)

        self.assertTrue(
            any("NON_RECOVERABLE" in error for error in errors),
            errors,
        )

    def test_reversible_action_still_requires_terminal_recovery(self):
        packet = self.fixture()
        self.authorization(packet)["gate_path"] = "AUTO_EXECUTED"
        packet["records"] = [
            record for record in packet["records"]
            if record["record_type"] != "recovery"
        ]

        errors, _ = validate_packet(packet)

        self.assertTrue(
            any("EXTERNAL_REVERSIBLE" in error and "recovery" in error for error in errors),
            errors,
        )

    def test_failed_reversible_recovery_is_reported_as_finding(self):
        packet = self.fixture()
        self.authorization(packet)["gate_path"] = "AUTO_EXECUTED"
        recovery = self.recovery(packet)
        recovery["recovery_status"] = "FAILED"
        recovery["objective_met"] = False

        errors, warnings = validate_packet(packet)

        self.assertEqual([], errors)
        self.assertTrue(
            any("finding: reversible action failed" in warning for warning in warnings),
            warnings,
        )


if __name__ == "__main__":
    unittest.main()
