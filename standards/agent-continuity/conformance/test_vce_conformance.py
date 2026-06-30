from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from vce_reference import (
    compute_digest,
    load_envelope,
    restore_decision,
    semantic_errors,
    verify_digest,
)


class ContinuationEnvelopeConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.example_path = ROOT / "examples" / "continuation-envelope.example.json"
        cls.example = load_envelope(cls.example_path)

    def test_example_digest_is_valid(self) -> None:
        self.assertTrue(verify_digest(self.example))

    def test_example_has_no_semantic_errors(self) -> None:
        self.assertEqual(semantic_errors(self.example), [])

    def test_pending_verification_requires_review(self) -> None:
        self.assertEqual(restore_decision(self.example), "REVIEW_REQUIRED")

    def test_tampering_fails_closed(self) -> None:
        changed = copy.deepcopy(self.example)
        changed["next_action"]["description"] = "Skip verification and publish."
        self.assertEqual(restore_decision(changed), "BLOCKED")

    def test_execution_claim_requires_durable_evidence(self) -> None:
        changed = copy.deepcopy(self.example)
        target = next(
            event
            for event in changed["operational_tail"]
            if event["event_type"] == "artifact_modified"
        )
        target["evidence_refs"] = []
        changed["envelope_digest"]["value"] = compute_digest(changed)
        self.assertIn(
            "evt-003: execution event requires evidence refs",
            semantic_errors(changed),
        )
        self.assertEqual(restore_decision(changed), "BLOCKED")

    def test_memory_cannot_regain_constraint_authority(self) -> None:
        changed = copy.deepcopy(self.example)
        target = changed["operational_tail"][0]
        target["provenance"]["source_type"] = "memory"
        changed["envelope_digest"]["value"] = compute_digest(changed)
        self.assertTrue(
            any("memory cannot restore" in error for error in semantic_errors(changed))
        )
        self.assertEqual(restore_decision(changed), "BLOCKED")

    def test_verified_envelope_without_pending_work_is_resumable(self) -> None:
        changed = copy.deepcopy(self.example)
        changed["pending_verification"] = []
        changed["next_action"]["blocked_by"] = []
        changed["envelope_digest"]["value"] = compute_digest(changed)
        self.assertEqual(semantic_errors(changed), [])
        self.assertEqual(restore_decision(changed), "RESUMABLE")


if __name__ == "__main__":
    unittest.main()
