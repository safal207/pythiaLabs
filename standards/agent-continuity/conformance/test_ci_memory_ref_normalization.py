import copy
import json
import unittest
from pathlib import Path

import ci_operational_checkpoint_reference as ref

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "ci-operational-checkpoint-v0.1.example.json"


class MemoryRefNormalizationTest(unittest.TestCase):
    def test_whitespace_prefixed_memory_refs_fail_closed(self):
        parent = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        current = copy.deepcopy(parent)
        current["verification"]["completed"][0]["evidence_refs"] = ["  memory://x"]
        current = ref.with_computed_digest(current)
        result = ref.evaluate_resume(current, current_workspace=current["workspace_state"])
        self.assertEqual(result["reason_code"], "MEMORY_IS_NOT_VERIFICATION")

        child = copy.deepcopy(parent)
        child["checkpoint_id"] = "checkpoint:memory-normalization"
        child["parent_checkpoint_id"] = parent["checkpoint_id"]
        child["sequence"] = 1
        child["created_at"] = "2026-07-03T13:30:00Z"
        child = ref.with_computed_digest(child)
        parent["verification"]["completed"][0]["evidence_refs"] = ["\n agent-memory://x"]
        parent = ref.with_computed_digest(parent)
        result = ref.evaluate_resume(child, current_workspace=child["workspace_state"], previous_checkpoint=parent)
        self.assertEqual(result["reason_code"], "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID")


if __name__ == "__main__":
    unittest.main()
