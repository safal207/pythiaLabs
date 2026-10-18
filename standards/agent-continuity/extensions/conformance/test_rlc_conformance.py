from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VCE_ROOT = ROOT.parent
sys.path.insert(0, str(HERE))

from rlc_reference import (
    ENVELOPE_SCHEMA_PATH,
    RESTORE_RESULTS_SCHEMA_PATH,
    compute_extension_digest,
    compute_lane_digest,
    load_json_object,
    rlc_decision,
    schema_errors,
    semantic_errors,
    verify_extension_digest,
)


class ResponsibilityLaneContinuityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        accepted = load_json_object(ROOT / "fixtures" / "rlc-accepted.json")
        rejected = load_json_object(
            ROOT / "fixtures" / "rlc-rejected-lane-conflation.json"
        )
        cls.extension = accepted["extension"]
        cls.restore_results = accepted["restore_results"]
        cls.rejected_conflation = rejected["extension"]
        cls.vce = load_json_object(
            VCE_ROOT / "examples" / "continuation-envelope.example.json"
        )

    @staticmethod
    def resign(extension: dict) -> None:
        extension["extension_digest"]["value"] = compute_extension_digest(extension)

    @staticmethod
    def relane(extension: dict, lane_index: int) -> None:
        lane = extension["responsibility_lanes"][lane_index]
        lane["lane_digest"] = compute_lane_digest(lane)

    def test_published_fixture_documents_are_schema_valid(self) -> None:
        self.assertEqual(schema_errors(self.extension, ENVELOPE_SCHEMA_PATH), [])
        self.assertEqual(
            schema_errors(self.restore_results, RESTORE_RESULTS_SCHEMA_PATH),
            [],
        )

    def test_example_digest_and_semantics_are_valid(self) -> None:
        self.assertTrue(verify_extension_digest(self.extension))
        self.assertEqual(semantic_errors(self.extension, self.vce), [])

    def test_accepted_fixture_passes_lane_restore(self) -> None:
        self.assertEqual(
            rlc_decision(self.extension, self.restore_results, self.vce),
            "PASSED",
        )

    def test_missing_restore_results_fails_closed(self) -> None:
        self.assertEqual(rlc_decision(self.extension, None, self.vce), "BLOCKED")

    def test_wrong_extension_id_fails_closed(self) -> None:
        changed = copy.deepcopy(self.restore_results)
        changed["extension_id"] = "another-extension"
        self.assertEqual(
            rlc_decision(self.extension, changed, self.vce),
            "BLOCKED",
        )

    def test_lane_conflation_fixture_fails_closed(self) -> None:
        errors = semantic_errors(self.rejected_conflation, self.vce)
        self.assertTrue(
            any(
                "effect refs outside lane allowlist" in error
                or "explicitly denied" in error
                for error in errors
            )
        )
        self.assertEqual(
            rlc_decision(
                self.rejected_conflation,
                self.restore_results,
                self.vce,
            ),
            "BLOCKED",
        )

    def test_active_lane_must_exist(self) -> None:
        changed = copy.deepcopy(self.extension)
        changed["active_lane_id"] = "missing"
        self.resign(changed)
        self.assertTrue(
            any(
                "active_lane_id references unknown lane" in error
                for error in semantic_errors(changed, self.vce)
            )
        )
        self.assertEqual(rlc_decision(changed, self.restore_results, self.vce), "BLOCKED")

    def test_next_action_must_stay_inside_lane_scope(self) -> None:
        changed = copy.deepcopy(self.extension)
        changed["next_action"]["effect_refs"] = ["artifact-rfc"]
        self.resign(changed)
        self.assertTrue(
            any(
                "next_action: effect refs outside lane allowlist" in error
                for error in semantic_errors(changed, self.vce)
            )
        )
        self.assertEqual(rlc_decision(changed, self.restore_results, self.vce), "BLOCKED")

    def test_unknown_binding_lane_fails_closed(self) -> None:
        changed = copy.deepcopy(self.extension)
        changed["event_bindings"][0]["lane_id"] = "missing"
        self.resign(changed)
        self.assertTrue(
            any(
                "binding references unknown lane" in error
                for error in semantic_errors(changed, self.vce)
            )
        )
        self.assertEqual(rlc_decision(changed, self.restore_results, self.vce), "BLOCKED")

    def test_material_event_must_have_lane_binding(self) -> None:
        changed = copy.deepcopy(self.extension)
        changed["event_bindings"] = [
            row for row in changed["event_bindings"] if row["event_id"] != "evt-003"
        ]
        self.resign(changed)
        self.assertTrue(
            any(
                "material VCE events missing responsibility-lane binding" in error
                for error in semantic_errors(changed, self.vce)
            )
        )
        self.assertEqual(rlc_decision(changed, self.restore_results, self.vce), "BLOCKED")

    def test_lane_digest_mismatch_fails_closed(self) -> None:
        changed = copy.deepcopy(self.extension)
        changed["responsibility_lanes"][0]["objective"] = "Silently changed objective."
        self.resign(changed)
        self.assertTrue(
            any("lane digest mismatch" in error for error in semantic_errors(changed, self.vce))
        )
        self.assertEqual(rlc_decision(changed, self.restore_results, self.vce), "BLOCKED")

    def test_extension_tampering_fails_closed(self) -> None:
        changed = copy.deepcopy(self.extension)
        changed["next_action"]["lane_id"] = "spec-authoring"
        self.assertEqual(rlc_decision(changed, self.restore_results, self.vce), "BLOCKED")

    def test_pending_lane_check_requires_review(self) -> None:
        changed = copy.deepcopy(self.restore_results)
        changed["lane_checks"][1]["status"] = "pending"
        changed["lane_checks"][1]["observed_lane_digest"] = None
        self.assertEqual(
            rlc_decision(self.extension, changed, self.vce),
            "REVIEW_REQUIRED",
        )

    def test_conflicting_lane_restore_fails_closed(self) -> None:
        changed = copy.deepcopy(self.restore_results)
        changed["lane_checks"][1]["status"] = "conflict"
        changed["lane_checks"][1]["conflict_refs"] = ["sot:owner:A", "sot:owner:B"]
        self.assertEqual(
            rlc_decision(self.extension, changed, self.vce),
            "BLOCKED",
        )

    def test_missing_source_revalidation_fails_closed(self) -> None:
        changed = copy.deepcopy(self.restore_results)
        changed["lane_checks"][1]["source_refs_checked"].pop()
        self.assertEqual(
            rlc_decision(self.extension, changed, self.vce),
            "BLOCKED",
        )

    def test_wrong_observed_lane_digest_fails_closed(self) -> None:
        changed = copy.deepcopy(self.restore_results)
        changed["lane_checks"][1]["observed_lane_digest"] = "sha256:" + "0" * 64
        self.assertEqual(
            rlc_decision(self.extension, changed, self.vce),
            "BLOCKED",
        )

    def test_duplicate_lane_id_fails_closed(self) -> None:
        changed = copy.deepcopy(self.extension)
        changed["responsibility_lanes"][1]["lane_id"] = "spec-authoring"
        self.relane(changed, 1)
        self.resign(changed)
        self.assertTrue(
            any("duplicate lane_id" in error for error in semantic_errors(changed, self.vce))
        )
        self.assertEqual(rlc_decision(changed, self.restore_results, self.vce), "BLOCKED")

    def test_unknown_lane_dependency_fails_closed(self) -> None:
        changed = copy.deepcopy(self.extension)
        changed["responsibility_lanes"][1]["depends_on"] = ["missing"]
        self.relane(changed, 1)
        self.resign(changed)
        self.assertTrue(
            any(
                "unknown dependency lane" in error
                for error in semantic_errors(changed, self.vce)
            )
        )
        self.assertEqual(rlc_decision(changed, self.restore_results, self.vce), "BLOCKED")

    def test_scope_allow_deny_overlap_fails_closed(self) -> None:
        changed = copy.deepcopy(self.extension)
        changed["responsibility_lanes"][1]["mutation_scope"]["denied_refs"].append(
            "capability:verify"
        )
        self.relane(changed, 1)
        self.resign(changed)
        self.assertTrue(
            any(
                "mutation scope overlaps allow/deny" in error
                for error in semantic_errors(changed, self.vce)
            )
        )
        self.assertEqual(rlc_decision(changed, self.restore_results, self.vce), "BLOCKED")

    def test_every_non_superseded_lane_requires_revalidation(self) -> None:
        changed = copy.deepcopy(self.extension)
        changed["restore_requirements"]["required_lane_checks"].pop(0)
        self.resign(changed)
        self.assertTrue(
            any(
                "non-superseded lanes missing source revalidation" in error
                for error in semantic_errors(changed, self.vce)
            )
        )
        self.assertEqual(rlc_decision(changed, self.restore_results, self.vce), "BLOCKED")

    def test_bound_event_must_exist_in_vce(self) -> None:
        changed = copy.deepcopy(self.extension)
        changed["event_bindings"][0]["event_id"] = "evt-does-not-exist"
        self.resign(changed)
        self.assertTrue(
            any(
                "event binding references unknown VCE event" in error
                for error in semantic_errors(changed, self.vce)
            )
        )
        self.assertEqual(rlc_decision(changed, self.restore_results, self.vce), "BLOCKED")


if __name__ == "__main__":
    unittest.main()
