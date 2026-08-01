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
    child["checkpoint_id"] = "checkpoint:issue-218:validated-parent"
    child["parent_checkpoint_id"] = parent["checkpoint_id"]
    child["sequence"] = parent["sequence"] + 1
    child["created_at"] = "2026-07-02T11:46:00Z"
    return with_computed_digest(child)


def evaluate(child, parent=None):
    return evaluate_resume(
        child,
        current_workspace=copy.deepcopy(child["workspace_state"]),
        previous_checkpoint=parent,
    )


class ParentValidationTest(unittest.TestCase):
    def test_parent_schema_is_checked(self):
        parent = load_example()
        child = child_of(parent)
        invalid_parent = copy.deepcopy(parent)
        invalid_parent.pop("authority")
        invalid_parent = with_computed_digest(invalid_parent)
        result = evaluate(child, invalid_parent)
        self.assertEqual(
            (result["outcome"], result["reason_code"]),
            (REJECT_LINEAGE_MISMATCH, "PREVIOUS_CHECKPOINT_SCHEMA_INVALID"),
        )

    def test_parent_digest_is_checked(self):
        parent = load_example()
        child = child_of(parent)
        changed_parent = copy.deepcopy(parent)
        changed_parent["objective"]["goal"] = "Changed parent goal"
        result = evaluate(child, changed_parent)
        self.assertEqual(
            (result["outcome"], result["reason_code"]),
            (REJECT_LINEAGE_MISMATCH, "PREVIOUS_CHECKPOINT_DIGEST_MISMATCH"),
        )

    def test_duplicate_rejected_ids_are_rejected(self):
        checkpoint = load_example()
        checkpoint["rejected_approaches"].append(
            copy.deepcopy(checkpoint["rejected_approaches"][0])
        )
        checkpoint = with_computed_digest(checkpoint)
        result = evaluate(checkpoint)
        self.assertEqual(
            (result["outcome"], result["reason_code"]),
            (REJECT_LINEAGE_MISMATCH, "REJECTED_APPROACH_ID_DUPLICATED"),
        )

    def test_ambiguous_parent_is_rejected(self):
        parent = load_example()
        child = child_of(parent)
        ambiguous_parent = copy.deepcopy(parent)
        ambiguous_parent["rejected_approaches"].append(
            copy.deepcopy(ambiguous_parent["rejected_approaches"][0])
        )
        ambiguous_parent = with_computed_digest(ambiguous_parent)
        result = evaluate(child, ambiguous_parent)
        self.assertEqual(
            (result["outcome"], result["reason_code"]),
            (REJECT_LINEAGE_MISMATCH, "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID"),
        )


if __name__ == "__main__":
    unittest.main()
