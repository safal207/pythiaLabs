from __future__ import annotations

import copy
import importlib
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
    child["checkpoint_id"] = "checkpoint:issue-218:reload"
    child["parent_checkpoint_id"] = parent["checkpoint_id"]
    child["sequence"] = parent["sequence"] + 1
    child["created_at"] = "2026-07-02T13:20:00Z"
    return core.with_computed_digest(child)


class ReloadIdempotencyTest(unittest.TestCase):
    def test_reloading_core_twice_does_not_recurse(self):
        parent = load_example()
        child = child_of(parent)

        importlib.reload(core)
        importlib.reload(core)
        result = core.evaluate_resume(
            child,
            current_workspace=copy.deepcopy(child["workspace_state"]),
            previous_checkpoint=parent,
        )

        self.assertEqual(
            (result["outcome"], result["reason_code"]),
            (core.CONTINUE, "CONTINUE_OK"),
        )


if __name__ == "__main__":
    unittest.main()
