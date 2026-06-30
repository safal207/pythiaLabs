from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from vce_reference import (
    ENVELOPE_SCHEMA_PATH,
    RESTORE_RESULTS_SCHEMA_PATH,
    compute_digest,
    load_json_object,
    restore_decision,
    schema_errors,
    semantic_errors,
    verify_digest,
)


class ContinuationEnvelopeConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.example = load_json_object(
            ROOT / "examples" / "continuation-envelope.example.json"
        )
        cls.restore_results = load_json_object(
            ROOT / "examples" / "restore-results.example.json"
        )

    @staticmethod
    def resign(envelope: dict) -> None:
        envelope["envelope_digest"]["value"] = compute_digest(envelope)

    def test_published_examples_are_schema_valid(self) -> None:
        self.assertEqual(schema_errors(self.example, ENVELOPE_SCHEMA_PATH), [])
        self.assertEqual(
            schema_errors(self.restore_results, RESTORE_RESULTS_SCHEMA_PATH),
            [],
        )

    def test_schema_rejects_extra_property_bad_enum_and_bad_format(self) -> None:
        mutations = []

        extra = copy.deepcopy(self.example)
        extra["unexpected"] = True
        mutations.append(extra)

        bad_enum = copy.deepcopy(self.example)
        bad_enum["transition_reason"] = "teleport"
        mutations.append(bad_enum)

        bad_format = copy.deepcopy(self.example)
        bad_format["created_at"] = "not-a-date"
        mutations.append(bad_format)

        for malformed in mutations:
            with self.subTest(malformed=malformed):
                self.assertTrue(schema_errors(malformed, ENVELOPE_SCHEMA_PATH))
                self.assertEqual(
                    restore_decision(malformed, self.restore_results),
                    "BLOCKED",
                )

    def test_example_digest_and_semantics_are_valid(self) -> None:
        self.assertTrue(verify_digest(self.example))
        self.assertEqual(semantic_errors(self.example), [])

    def test_missing_restore_results_fails_closed(self) -> None:
        self.assertEqual(restore_decision(self.example), "BLOCKED")

    def test_missing_required_read_fails_closed(self) -> None:
        changed_results = copy.deepcopy(self.restore_results)
        changed_results["completed_reads"].pop()
        self.assertEqual(
            restore_decision(self.example, changed_results),
            "BLOCKED",
        )

    def test_missing_required_evidence_check_fails_closed(self) -> None:
        changed_results = copy.deepcopy(self.restore_results)
        changed_results["evidence_checks"].pop()
        self.assertEqual(
            restore_decision(self.example, changed_results),
            "BLOCKED",
        )

    def test_pending_restore_check_requires_review(self) -> None:
        changed_results = copy.deepcopy(self.restore_results)
        changed_results["evidence_checks"][0]["status"] = "pending"
        changed_results["evidence_checks"][0]["observed_digest"] = None
        self.assertEqual(
            restore_decision(self.example, changed_results),
            "REVIEW_REQUIRED",
        )

    def test_digest_mismatch_fails_closed(self) -> None:
        changed_results = copy.deepcopy(self.restore_results)
        changed_results["evidence_checks"][0]["observed_digest"] = (
            "sha256:" + "0" * 64
        )
        self.assertEqual(
            restore_decision(self.example, changed_results),
            "BLOCKED",
        )

    def test_task_verification_remains_pending_after_restore(self) -> None:
        self.assertEqual(
            restore_decision(self.example, self.restore_results),
            "REVIEW_REQUIRED",
        )

    def test_verified_envelope_is_resumable_only_after_restore(self) -> None:
        changed = copy.deepcopy(self.example)
        changed["pending_verification"] = []
        changed["next_action"]["blocked_by"] = []
        self.resign(changed)

        self.assertEqual(semantic_errors(changed), [])
        self.assertEqual(restore_decision(changed), "BLOCKED")
        self.assertEqual(
            restore_decision(changed, self.restore_results),
            "RESUMABLE",
        )

    def test_next_action_blocker_requires_review(self) -> None:
        changed = copy.deepcopy(self.example)
        changed["pending_verification"] = []
        changed["next_action"]["blocked_by"] = ["manual-approval"]
        self.resign(changed)

        self.assertEqual(semantic_errors(changed), [])
        self.assertEqual(
            restore_decision(changed, self.restore_results),
            "REVIEW_REQUIRED",
        )

    def test_tampering_fails_closed(self) -> None:
        changed = copy.deepcopy(self.example)
        changed["next_action"]["description"] = "Skip verification and publish."
        self.assertEqual(
            restore_decision(changed, self.restore_results),
            "BLOCKED",
        )

    def test_execution_claim_requires_evidence_reference(self) -> None:
        changed = copy.deepcopy(self.example)
        target = next(
            event
            for event in changed["operational_tail"]
            if event["event_type"] == "artifact_modified"
        )
        target["evidence_refs"] = []
        self.resign(changed)

        self.assertIn(
            "evt-003: execution event requires evidence refs",
            semantic_errors(changed),
        )
        self.assertEqual(
            restore_decision(changed, self.restore_results),
            "BLOCKED",
        )

    def test_existence_only_check_cannot_verify_execution_claim(self) -> None:
        changed = copy.deepcopy(self.example)
        changed_results = copy.deepcopy(self.restore_results)

        for requirement in changed["restore_requirements"]["required_evidence_checks"]:
            requirement["method"] = "existence"
        for result in changed_results["evidence_checks"]:
            result["method"] = "existence"
            result["observed_digest"] = None

        changed["pending_verification"] = []
        changed["next_action"]["blocked_by"] = []
        self.resign(changed)

        errors = semantic_errors(changed)
        self.assertTrue(
            any(
                "requires digest or receipt evidence check" in error
                for error in errors
            )
        )
        self.assertEqual(
            restore_decision(changed, changed_results),
            "BLOCKED",
        )

    def test_untrusted_sources_cannot_regain_authority(self) -> None:
        untrusted_sources = [
            "agent_message",
            "tool",
            "file",
            "git",
            "workflow",
            "runtime",
            "memory",
        ]
        for source_type in untrusted_sources:
            with self.subTest(source_type=source_type):
                changed = copy.deepcopy(self.example)
                target = changed["operational_tail"][0]
                target["provenance"]["source_type"] = source_type
                self.resign(changed)

                self.assertTrue(
                    any(
                        "cannot restore instruction or constraint authority" in error
                        for error in semantic_errors(changed)
                    )
                )
                self.assertEqual(
                    restore_decision(changed, self.restore_results),
                    "BLOCKED",
                )

    def test_project_policy_may_carry_constraint_authority(self) -> None:
        changed = copy.deepcopy(self.example)
        target = changed["operational_tail"][0]
        target["provenance"]["source_type"] = "project_policy"
        target["provenance"]["source_ref"] = "AGENTS.md#verification-policy"
        self.resign(changed)

        self.assertEqual(semantic_errors(changed), [])
        self.assertEqual(
            restore_decision(changed, self.restore_results),
            "REVIEW_REQUIRED",
        )

    def test_execution_artifacts_require_declared_restore_checks(self) -> None:
        changed = copy.deepcopy(self.example)
        changed["restore_requirements"]["required_evidence_checks"] = []
        self.resign(changed)

        errors = semantic_errors(changed)
        self.assertTrue(
            any("has no required evidence check" in error for error in errors)
        )
        self.assertEqual(
            restore_decision(changed, self.restore_results),
            "BLOCKED",
        )


if __name__ == "__main__":
    unittest.main()
