from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import ci_operational_checkpoint_reference_core as core  # noqa: E402

EXAMPLE = ROOT / "examples" / "ci-operational-checkpoint-v0.1.example.json"


def load_example():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def child_of(parent):
    child = copy.deepcopy(parent)
    child["checkpoint_id"] = "checkpoint:issue-218:core-guard"
    child["parent_checkpoint_id"] = parent["checkpoint_id"]
    child["sequence"] = parent["sequence"] + 1
    child["created_at"] = "2026-07-02T13:15:00Z"
    return core.with_computed_digest(child)


def semantic_invalid_parent():
    parent = load_example()
    parent["rejected_approaches"].append(
        copy.deepcopy(parent["rejected_approaches"][0])
    )
    return core.with_computed_digest(parent)


def evaluate(checkpoint, previous=None, **kwargs):
    return core.evaluate_resume(
        checkpoint,
        current_workspace=copy.deepcopy(checkpoint["workspace_state"]),
        previous_checkpoint=previous,
        **kwargs,
    )


class CoreIntegrityGuardTest(unittest.TestCase):
    def assert_result(self, result, outcome, reason_code):
        self.assertEqual(
            (result["outcome"], result["reason_code"]),
            (outcome, reason_code),
        )

    def test_core_rejects_impossible_parent_lineage(self):
        parent = load_example()
        child = child_of(parent)
        invalid_parent = copy.deepcopy(parent)
        invalid_parent["parent_checkpoint_id"] = "checkpoint:unexpected-parent"
        invalid_parent = core.with_computed_digest(invalid_parent)

        result = evaluate(child, invalid_parent)

        self.assert_result(
            result,
            core.REJECT_LINEAGE_MISMATCH,
            "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
        )

    def test_core_rejects_empty_parent_completion_evidence(self):
        parent = load_example()
        child = child_of(parent)
        invalid_parent = copy.deepcopy(parent)
        invalid_parent["verification"]["completed"][0]["evidence_refs"] = []
        invalid_parent = core.with_computed_digest(invalid_parent)

        result = evaluate(child, invalid_parent)

        self.assert_result(
            result,
            core.REJECT_LINEAGE_MISMATCH,
            "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
        )

    def test_authority_error_wins_over_unrelated_schema_error(self):
        checkpoint = load_example()
        checkpoint["authority"] = "merge_allowed"
        checkpoint["unexpected"] = True
        checkpoint = core.with_computed_digest(checkpoint)

        result = evaluate(checkpoint)

        self.assert_result(
            result,
            core.REJECT_INVALID_AUTHORITY,
            "AUTHORITY_NOT_CONTEXT_ONLY",
        )

    def test_current_digest_mismatch_wins_over_invalid_parent(self):
        parent = semantic_invalid_parent()
        child = child_of(load_example())
        child["objective"]["goal"] = "tampered without recomputing digest"

        result = evaluate(child, parent)

        self.assert_result(result, core.RESTART_REQUIRED, "DIGEST_MISMATCH")

    def test_current_replay_wins_over_invalid_parent(self):
        parent = semantic_invalid_parent()
        child = child_of(load_example())

        result = evaluate(
            child,
            parent,
            seen_checkpoint_ids={child["checkpoint_id"]},
        )

        self.assert_result(
            result,
            core.IDEMPOTENT_REPLAY,
            "CHECKPOINT_ALREADY_CONSUMED",
        )

    def test_current_root_lineage_error_wins_over_invalid_parent(self):
        checkpoint = load_example()
        checkpoint["parent_checkpoint_id"] = "checkpoint:unexpected-parent"
        checkpoint = core.with_computed_digest(checkpoint)

        result = evaluate(checkpoint, semantic_invalid_parent())

        self.assert_result(
            result,
            core.REJECT_LINEAGE_MISMATCH,
            "ROOT_HAS_PARENT",
        )

    def test_parent_schema_error_wins_over_empty_evidence(self):
        parent = load_example()
        child = child_of(parent)
        invalid_parent = copy.deepcopy(parent)
        invalid_parent.pop("authority")
        invalid_parent["verification"]["completed"][0]["evidence_refs"] = []
        invalid_parent = core.with_computed_digest(invalid_parent)

        result = evaluate(child, invalid_parent)

        self.assert_result(
            result,
            core.REJECT_LINEAGE_MISMATCH,
            "PREVIOUS_CHECKPOINT_SCHEMA_INVALID",
        )

    def test_checkpoint_id_reuse_is_rejected_after_canonical_validation(self):
        parent = load_example()
        child = child_of(parent)
        child["checkpoint_id"] = parent["checkpoint_id"]
        child = core.with_computed_digest(child)

        result = evaluate(child, parent)

        self.assert_result(
            result,
            core.REJECT_LINEAGE_MISMATCH,
            "CHECKPOINT_ID_REUSED",
        )


if __name__ == "__main__":
    unittest.main()
