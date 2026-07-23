from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_caep import load_packet  # noqa: E402
from validate_caep_strict import validate_packet  # noqa: E402


class StrictValidationTests(unittest.TestCase):
    def fixture(self):
        return load_packet(
            ROOT / "examples" / "hypothetical_sandbox_escape_episode.json"
        )

    def assert_invalid_with(self, packet, fragment: str):
        errors, _warnings = validate_packet(packet)
        self.assertTrue(
            any(fragment in error for error in errors),
            json.dumps(errors, indent=2),
        )

    def test_valid_f2_packet_passes(self):
        errors, _warnings = validate_packet(self.fixture())
        self.assertEqual([], errors)

    def test_semantic_validator_cannot_claim_f3(self):
        packet = self.fixture()
        packet["evidence_level"] = "F3"
        fake = {"scheme": "fake", "key_id": "fake", "value": "fake"}
        for record in packet["records"]:
            if record["record_type"] in {
                "authorization", "dispatch", "outcome", "recovery"
            }:
                record["integrity_proof"] = fake.copy()
        self.assert_invalid_with(packet, "cannot be established by semantic validation")

    def test_authorization_must_reference_intent(self):
        packet = self.fixture()
        packet["records"][1]["causal_parent_record_ids"] = []
        self.assert_invalid_with(packet, "authorization must reference causal parent")

    def test_dispatch_must_reference_authorization(self):
        packet = self.fixture()
        packet["records"][2]["causal_parent_record_ids"] = ["rec-intent-001"]
        self.assert_invalid_with(packet, "dispatch must reference causal parent")

    def test_observed_time_must_be_monotonic(self):
        packet = self.fixture()
        packet["records"][3]["observed_at"] = "2026-07-16T08:59:00Z"
        self.assert_invalid_with(packet, "observed_at is not monotonic")

    def test_valid_time_cannot_follow_transaction_time(self):
        packet = self.fixture()
        packet["records"][0]["valid_time"] = "2026-07-16T09:00:02Z"
        self.assert_invalid_with(packet, "intent.valid_time <= intent.transaction_time")


if __name__ == "__main__":
    unittest.main()
