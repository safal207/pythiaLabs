from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_caep import load_packet, validate_packet  # noqa: E402


class ValidatorRegressionTests(unittest.TestCase):
    def fixture(self):
        return load_packet(
            ROOT / "examples" / "hypothetical_sandbox_escape_episode.json"
        )

    def test_unknown_outcome_status_fails_closed(self):
        packet = self.fixture()
        packet["records"][3]["status"] = "MAYBE"
        errors, _ = validate_packet(packet)
        self.assertTrue(any(".status must be one of" in error for error in errors))

    def test_unknown_policy_conformance_fails_closed(self):
        packet = self.fixture()
        packet["records"][3]["policy_conformance"] = "MAYBE"
        packet["records"][3]["containment_required"] = False
        packet["records"].pop()
        errors, _ = validate_packet(packet)
        self.assertTrue(
            any(".policy_conformance must be one of" in error for error in errors)
        )

    def test_explicit_unknown_conformance_requires_recovery(self):
        packet = self.fixture()
        packet["records"][3]["policy_conformance"] = "UNKNOWN"
        packet["records"][3]["containment_required"] = False
        packet["records"].pop()
        errors, _ = validate_packet(packet)
        self.assertTrue(
            any("unknown/containment-required" in error for error in errors)
        )

    def test_malformed_parent_sequence_does_not_crash(self):
        packet = self.fixture()
        packet["records"][1]["sequence"] = None
        errors, _ = validate_packet(packet)
        self.assertTrue(any(".sequence must be an integer" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
