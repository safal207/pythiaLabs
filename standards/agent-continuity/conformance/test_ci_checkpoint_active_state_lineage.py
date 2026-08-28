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

from ci_operational_checkpoint_reference import (  # noqa: E402
    REJECT_LINEAGE_MISMATCH,
    REJECT_UNVERIFIED_COMPLETION,
    evaluate_resume,
    with_computed_digest,
)

EXAMPLE = ROOT / "examples" / "ci-operational-checkpoint-v0.1.example.json"


def load_example():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def child_of(parent):
    child = copy.deepcopy(parent)
    child["checkpoint_id"] = "checkpoint:issue-218:active-state"
    child["parent_checkpoint_id"] = parent["checkpoint_id"]
    child["sequence"] = parent["sequence"] + 1
    child["created_at"] = "2026-07-02T12:05:00Z"
    return child


def evaluate(child, parent):
    return evaluate_resume(
        with_computed_digest(child),
        current_workspace=copy.deepcopy(child["workspace_state"]),
        previous_checkpoint=parent,
    )


class ActiveStateLineageTest(unittest.TestCase):
    def test_creation_time_cannot_move_backwards(self):
        parent = load_example()
        child = child_of(parent)
        child["created_at"] = "2026-07-02T09:00:00Z"
        result = evaluate(child, parent)
        self.assertEqual(
            (result["outcome"], result["reason_code"]),
            (REJECT_LINEAGE_MISMATCH, "CREATION_TIME_REGRESSED"),
        )

    def test_objective_cannot_change_within_trajectory(self):
        parent = load_example()
        child = child_of(parent)
        child["objective"]["goal"] = "Different goal"
        result = evaluate(child, parent)
        self.assertEqual(
            (result["outcome"], result["reason_code"]),
            (REJECT_LINEAGE_MISMATCH, "OBJECTIVE_CHANGED"),
        )

    def test_active_constraint_cannot_disappear(self):
        parent = load_example()
        child = child_of(parent)
        child["constraints"]["must"] = []
        result = evaluate(child, parent)
        self.assertEqual(
            (result["outcome"], result["reason_code"]),
            (REJECT_LINEAGE_MISMATCH, "CONSTRAINT_LOST"),
        )

    def test_pending_verification_cannot_disappear(self):
        parent = load_example()
        child = child_of(parent)
        child["verification"]["required"].remove("verification:conformance")
        child["verification"]["pending"] = []
        result = evaluate(child, parent)
        self.assertEqual(
            (result["outcome"], result["reason_code"]),
            (REJECT_UNVERIFIED_COMPLETION, "PENDING_VERIFICATION_LOST"),
        )

    def test_pending_verification_target_cannot_change(self):
        parent = load_example()
        child = child_of(parent)
        child["verification"]["pending"][0]["target"] = "Different target"
        result = evaluate(child, parent)
        self.assertEqual(
            (result["outcome"], result["reason_code"]),
            (REJECT_UNVERIFIED_COMPLETION, "PENDING_VERIFICATION_CHANGED"),
        )


if __name__ == "__main__":
    unittest.main()
