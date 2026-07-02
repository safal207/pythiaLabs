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
    IDEMPOTENT_REPLAY,
    REJECT_INVALID_AUTHORITY,
    REJECT_LINEAGE_MISMATCH,
    REJECT_UNVERIFIED_COMPLETION,
    RESTART_REQUIRED,
    REVALIDATE_WORKSPACE,
    evaluate_resume,
    with_computed_digest,
)

EXAMPLE_PATH = ROOT / "examples" / "ci-operational-checkpoint-v0.1.example.json"


def load_example():
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


def current_workspace(checkpoint):
    return copy.deepcopy(checkpoint["workspace_state"])


def next_checkpoint(previous):
    checkpoint = copy.deepcopy(previous)
    checkpoint["checkpoint_id"] = "checkpoint:issue-218:next"
    checkpoint["parent_checkpoint_id"] = previous["checkpoint_id"]
    checkpoint["sequence"] = previous["sequence"] + 1
    checkpoint["created_at"] = "2026-07-02T09:31:00Z"
    return with_computed_digest(checkpoint)


class CiOperationalCheckpointTest(unittest.TestCase):
    def assert_outcome(self, checkpoint, expected, **kwargs):
        workspace = kwargs.pop("current_workspace", current_workspace(checkpoint))
        result = evaluate_resume(
            checkpoint,
            current_workspace=workspace,
            **kwargs,
        )
        self.assertEqual(result["outcome"], expected, result)
        return result

    def test_valid_root_checkpoint_continues(self):
        self.assert_outcome(load_example(), CONTINUE)

    def test_changed_head_requires_workspace_revalidation(self):
        checkpoint = load_example()
        workspace = current_workspace(checkpoint)
        workspace["head_sha"] = "f" * 40

        result = self.assert_outcome(
            checkpoint,
            REVALIDATE_WORKSPACE,
            current_workspace=workspace,
        )

        self.assertEqual(result["reason_code"], "WORKSPACE_STATE_CHANGED")

    def test_changed_base_requires_workspace_revalidation(self):
        checkpoint = load_example()
        workspace = current_workspace(checkpoint)
        workspace["base_ref"] = "release"

        self.assert_outcome(
            checkpoint,
            REVALIDATE_WORKSPACE,
            current_workspace=workspace,
        )

    def test_changed_dirty_state_requires_workspace_revalidation(self):
        checkpoint = load_example()
        workspace = current_workspace(checkpoint)
        workspace["dirty_state_digest"] = "sha256:" + "1" * 64

        self.assert_outcome(
            checkpoint,
            REVALIDATE_WORKSPACE,
            current_workspace=workspace,
        )

    def test_changed_repository_requires_restart(self):
        checkpoint = load_example()
        workspace = current_workspace(checkpoint)
        workspace["repository"] = "safal207/other"

        self.assert_outcome(
            checkpoint,
            RESTART_REQUIRED,
            current_workspace=workspace,
        )

    def test_duplicate_checkpoint_is_idempotent_replay(self):
        checkpoint = load_example()

        self.assert_outcome(
            checkpoint,
            IDEMPOTENT_REPLAY,
            seen_checkpoint_ids={checkpoint["checkpoint_id"]},
        )

    def test_non_root_checkpoint_requires_parent(self):
        checkpoint = load_example()
        checkpoint["sequence"] = 1
        checkpoint = with_computed_digest(checkpoint)

        self.assert_outcome(checkpoint, REJECT_LINEAGE_MISMATCH)

    def test_parent_must_match_previous_checkpoint(self):
        previous = load_example()
        checkpoint = next_checkpoint(previous)
        checkpoint["parent_checkpoint_id"] = "checkpoint:wrong"
        checkpoint = with_computed_digest(checkpoint)

        self.assert_outcome(
            checkpoint,
            REJECT_LINEAGE_MISMATCH,
            previous_checkpoint=previous,
        )

    def test_rejected_approach_cannot_disappear(self):
        previous = load_example()
        checkpoint = next_checkpoint(previous)
        checkpoint["rejected_approaches"] = []
        checkpoint = with_computed_digest(checkpoint)

        result = self.assert_outcome(
            checkpoint,
            REJECT_LINEAGE_MISMATCH,
            previous_checkpoint=previous,
        )

        self.assertEqual(result["reason_code"], "REJECTED_APPROACH_LOST")

    def test_completed_verification_requires_evidence(self):
        checkpoint = load_example()
        checkpoint["verification"]["completed"][0]["evidence_refs"] = []
        checkpoint = with_computed_digest(checkpoint)

        self.assert_outcome(checkpoint, REJECT_UNVERIFIED_COMPLETION)

    def test_memory_cannot_become_verification(self):
        checkpoint = load_example()
        checkpoint["verification"]["completed"][0]["evidence_refs"] = [
            "memory://the-agent-remembers-ci-was-green"
        ]
        checkpoint = with_computed_digest(checkpoint)

        result = self.assert_outcome(
            checkpoint,
            REJECT_UNVERIFIED_COMPLETION,
        )

        self.assertEqual(result["reason_code"], "MEMORY_IS_NOT_VERIFICATION")

    def test_authority_must_remain_context_only(self):
        checkpoint = load_example()
        checkpoint["authority"] = "merge_allowed"
        checkpoint = with_computed_digest(checkpoint)

        self.assert_outcome(checkpoint, REJECT_INVALID_AUTHORITY)

    def test_merge_next_action_requires_fresh_authority(self):
        checkpoint = load_example()
        checkpoint["next_action"] = {
            "description": "Merge the pull request.",
            "action_class": "merge",
            "requires_fresh_authority": False,
        }
        checkpoint = with_computed_digest(checkpoint)

        result = self.assert_outcome(checkpoint, REJECT_INVALID_AUTHORITY)
        self.assertEqual(result["reason_code"], "FRESH_AUTHORITY_REQUIRED")

    def test_merge_next_action_may_continue_only_to_fresh_authorization(self):
        checkpoint = load_example()
        checkpoint["next_action"] = {
            "description": "Construct and evaluate a fresh Action Envelope.",
            "action_class": "merge",
            "requires_fresh_authority": True,
        }
        checkpoint = with_computed_digest(checkpoint)

        self.assert_outcome(checkpoint, CONTINUE)

    def test_digest_tampering_requires_restart(self):
        checkpoint = load_example()
        checkpoint["objective"]["goal"] = "Tampered goal"

        result = self.assert_outcome(checkpoint, RESTART_REQUIRED)
        self.assertEqual(result["reason_code"], "DIGEST_MISMATCH")

    def test_previous_completed_verification_cannot_disappear(self):
        previous = load_example()
        checkpoint = next_checkpoint(previous)
        checkpoint["verification"]["completed"] = []
        checkpoint["verification"]["pending"].append(
            {
                "verification_id": "verification:schema",
                "target": "CI operational checkpoint JSON Schema",
                "status": "pending",
            }
        )
        checkpoint = with_computed_digest(checkpoint)

        self.assert_outcome(
            checkpoint,
            REJECT_UNVERIFIED_COMPLETION,
            previous_checkpoint=previous,
        )

    def test_unknown_field_requires_restart(self):
        checkpoint = load_example()
        checkpoint["surprise"] = True
        checkpoint = with_computed_digest(checkpoint)

        result = self.assert_outcome(checkpoint, RESTART_REQUIRED)
        self.assertEqual(result["reason_code"], "SCHEMA_INVALID")


if __name__ == "__main__":
    unittest.main()
