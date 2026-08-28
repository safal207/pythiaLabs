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
    CONTINUE,
    REJECT_LINEAGE_MISMATCH,
    evaluate_resume,
    with_computed_digest,
)

EXAMPLE = ROOT / "examples" / "ci-operational-checkpoint-v0.1.example.json"


def load_example():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def child_of(parent):
    child = copy.deepcopy(parent)
    child["checkpoint_id"] = "checkpoint:issue-218:child"
    child["parent_checkpoint_id"] = parent["checkpoint_id"]
    child["sequence"] = parent["sequence"] + 1
    child["created_at"] = "2026-07-02T11:45:00Z"
    return with_computed_digest(child)


class ParentRequirementTest(unittest.TestCase):
    def evaluate(self, checkpoint, **kwargs):
        return evaluate_resume(
            checkpoint,
            current_workspace=copy.deepcopy(checkpoint["workspace_state"]),
            **kwargs,
        )

    def test_full_parent_allows_non_root_resume(self):
        parent = load_example()
        result = self.evaluate(child_of(parent), previous_checkpoint=parent)
        self.assertEqual((result["outcome"], result["reason_code"]), (CONTINUE, "CONTINUE_OK"))

    def test_known_parent_id_is_not_enough(self):
        parent = load_example()
        result = self.evaluate(
            child_of(parent),
            known_parent_ids={parent["checkpoint_id"]},
        )
        self.assertEqual(
            (result["outcome"], result["reason_code"]),
            (REJECT_LINEAGE_MISMATCH, "PREVIOUS_CHECKPOINT_REQUIRED"),
        )

    def test_unknown_parent_is_rejected(self):
        parent = load_example()
        result = self.evaluate(child_of(parent))
        self.assertEqual(
            (result["outcome"], result["reason_code"]),
            (REJECT_LINEAGE_MISMATCH, "PARENT_NOT_FOUND"),
        )


if __name__ == "__main__":
    unittest.main()
