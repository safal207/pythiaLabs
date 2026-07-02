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
    evaluate_resume,
    with_computed_digest,
)

EXAMPLE = ROOT / "examples" / "ci-operational-checkpoint-v0.1.example.json"


def load_example():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def child_of(parent):
    child = copy.deepcopy(parent)
    child["checkpoint_id"] = "checkpoint:issue-218:link-invariant"
    child["parent_checkpoint_id"] = parent["checkpoint_id"]
    child["sequence"] = parent["sequence"] + 1
    child["created_at"] = "2026-07-02T12:30:00Z"
    return with_computed_digest(child)


def evaluate(child, parent):
    return evaluate_resume(
        child,
        current_workspace=copy.deepcopy(child["workspace_state"]),
        previous_checkpoint=parent,
    )


class CheckpointLinkInvariantTest(unittest.TestCase):
    def assert_reason(self, result, reason_code):
        self.assertEqual(
            (result["outcome"], result["reason_code"]),
            (REJECT_LINEAGE_MISMATCH, reason_code),
        )

    def test_root_parent_cannot_declare_its_own_parent(self):
        parent = load_example()
        child = child_of(parent)
        invalid_parent = copy.deepcopy(parent)
        invalid_parent["parent_checkpoint_id"] = "checkpoint:unexpected-parent"
        invalid_parent = with_computed_digest(invalid_parent)
        self.assert_reason(
            evaluate(child, invalid_parent),
            "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
        )

    def test_non_root_parent_requires_parent_id(self):
        parent = load_example()
        child = child_of(parent)
        invalid_parent = copy.deepcopy(parent)
        invalid_parent["sequence"] = 1
        invalid_parent["parent_checkpoint_id"] = None
        invalid_parent = with_computed_digest(invalid_parent)
        self.assert_reason(
            evaluate(child, invalid_parent),
            "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
        )

    def test_child_cannot_reuse_parent_checkpoint_id(self):
        parent = load_example()
        child = child_of(parent)
        child["checkpoint_id"] = parent["checkpoint_id"]
        child = with_computed_digest(child)
        self.assert_reason(evaluate(child, parent), "CHECKPOINT_ID_REUSED")


if __name__ == "__main__":
    unittest.main()
