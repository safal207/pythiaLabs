from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_caep import load_packet, validate_packet  # noqa: E402


class CaepValidatorTests(unittest.TestCase):
    def fixture(self, name: str):
        return load_packet(ROOT / "examples" / name)

    def assert_invalid_with(self, packet, fragment: str):
        errors, _warnings = validate_packet(packet)
        self.assertTrue(errors, "expected validation errors")
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected {fragment!r} in errors: {json.dumps(errors, indent=2)}",
        )

    def test_valid_synthetic_incident_packet(self):
        errors, warnings = validate_packet(
            self.fixture("hypothetical_sandbox_escape_episode.json")
        )
        self.assertEqual([], errors)
        self.assertTrue(any("below F3" in warning for warning in warnings))

    def test_parameter_drift_fails_closed(self):
        self.assert_invalid_with(
            self.fixture("invalid_parameter_drift.json"),
            "actual_params_hash does not match",
        )

    def test_missing_outcome_is_incident_signal(self):
        self.assert_invalid_with(
            self.fixture("invalid_missing_outcome.json"),
            "every dispatch must have exactly one terminal outcome",
        )

    def test_false_recovery_claim_is_rejected(self):
        self.assert_invalid_with(
            self.fixture("invalid_false_recovery.json"),
            "RECOVERED requires objective_met=true",
        )

    def test_unknown_verdict_fails_closed(self):
        packet = self.fixture("hypothetical_sandbox_escape_episode.json")
        packet["records"][1]["decision"] = "MAYBE"
        self.assert_invalid_with(packet, ".decision must be one of")

    def test_unauthorized_destination_is_rejected(self):
        packet = self.fixture("hypothetical_sandbox_escape_episode.json")
        packet["records"][2]["network_destination"] = "public.example:443"
        self.assert_invalid_with(packet, "outside authorized_network_destinations")

    def test_expired_authorization_is_rejected(self):
        packet = self.fixture("hypothetical_sandbox_escape_episode.json")
        packet["records"][1]["expiry"] = "2026-07-16T08:59:59Z"
        self.assert_invalid_with(packet, "after authorization expiry")

    def test_orphan_causal_parent_is_rejected(self):
        packet = self.fixture("hypothetical_sandbox_escape_episode.json")
        packet["records"][3]["causal_parent_record_ids"] = ["missing-dispatch"]
        self.assert_invalid_with(packet, "unknown causal parent")

    def test_f3_requires_integrity_proofs(self):
        packet = self.fixture("hypothetical_sandbox_escape_episode.json")
        packet["evidence_level"] = "F3"
        self.assert_invalid_with(packet, "F3 requires integrity_proof")

    def test_episode_ref_is_content_derived(self):
        packet = self.fixture("hypothetical_sandbox_escape_episode.json")
        packet["records"][0]["target_resource"] = "https://different.example/resource"
        self.assert_invalid_with(packet, "episode_ref does not match canonical intent binding")


if __name__ == "__main__":
    unittest.main()
