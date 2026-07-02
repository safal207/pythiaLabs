from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ADAPTERS = ROOT / "adapters"
if str(ADAPTERS) not in sys.path:
    sys.path.insert(0, str(ADAPTERS))

from github_pr_merge_gate import (  # noqa: E402
    GITHUB_INPUT_INVALID,
    canonical_action_id,
    evaluate_github_pr_merge,
    input_errors,
    target_ref,
)

EXAMPLE_PATH = ROOT / "examples" / "github-pr-merge-gate-input.example.json"


def load_example():
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


class GitHubPrMergeGateTest(unittest.TestCase):
    def assert_decision(self, snapshot, expected_decision, expected_reason, **kwargs):
        result = evaluate_github_pr_merge(snapshot, **kwargs)
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            (expected_decision, expected_reason),
        )
        return result

    def test_example_matches_strict_input_schema(self):
        self.assertEqual(input_errors(load_example()), [])

    def test_valid_snapshot_allows_and_binds_every_evidence_row(self):
        snapshot = load_example()
        result = self.assert_decision(snapshot, "ALLOW", "ALLOW_OK")
        envelope = result["envelope"]
        self.assertEqual(result["action_id"], canonical_action_id(snapshot))
        self.assertEqual(envelope["request"]["target"], target_ref(snapshot))
        self.assertIn(":main:", envelope["idempotency"]["key"])
        self.assertTrue(
            all(row["action_id"] == result["action_id"] for row in envelope["evidence"])
        )

    def test_action_id_is_stable_for_same_target(self):
        first = canonical_action_id(load_example())
        second = canonical_action_id(load_example())
        self.assertEqual(first, second)

    def test_action_id_changes_when_expected_head_changes(self):
        first = load_example()
        second = load_example()
        second["pull_request"]["expected_head_sha"] = "b" * 40
        second["pull_request"]["observed_head_sha"] = "b" * 40
        second["authorization"]["target"] = target_ref(second)
        self.assertNotEqual(canonical_action_id(first), canonical_action_id(second))

    def test_action_id_changes_when_base_ref_changes(self):
        first = load_example()
        second = load_example()
        second["pull_request"]["base_ref"] = "release"
        second["authorization"]["target"] = target_ref(second)
        self.assertNotEqual(canonical_action_id(first), canonical_action_id(second))

    def test_current_head_drift_blocks(self):
        snapshot = load_example()
        snapshot["pull_request"]["observed_head_sha"] = "b" * 40
        result = self.assert_decision(snapshot, "BLOCK", "PRECONDITION_FAILED")
        self.assertIn("github-head-matches", result["detail"])

    def test_successful_check_from_old_head_blocks(self):
        snapshot = load_example()
        snapshot["checks"][0]["head_sha"] = "b" * 40
        result = self.assert_decision(snapshot, "BLOCK", "PRECONDITION_FAILED")
        self.assertIn("github-check-", result["detail"])

    def test_missing_required_check_escalates(self):
        snapshot = load_example()
        snapshot["checks"] = [row for row in snapshot["checks"] if row["name"] != "Security"]
        result = self.assert_decision(snapshot, "ESCALATE", "PRECONDITION_UNRESOLVED")
        self.assertIn("github-check-", result["detail"])

    def test_missing_required_review_escalates(self):
        snapshot = load_example()
        snapshot["reviews"] = [
            row for row in snapshot["reviews"] if row["reviewer"] != "chatgpt-codex-connector"
        ]
        result = self.assert_decision(snapshot, "ESCALATE", "PRECONDITION_UNRESOLVED")
        self.assertIn("github-review-", result["detail"])

    def test_review_from_old_head_blocks(self):
        snapshot = load_example()
        snapshot["reviews"][0]["head_sha"] = "b" * 40
        result = self.assert_decision(snapshot, "BLOCK", "PRECONDITION_FAILED")
        self.assertIn("github-review-", result["detail"])

    def test_stale_review_evidence_blocks(self):
        snapshot = load_example()
        snapshot["reviews"][0]["expires_at"] = "2026-07-01T21:04:59Z"
        self.assert_decision(snapshot, "BLOCK", "EVIDENCE_STALE")

    def test_replayed_merge_action_blocks(self):
        snapshot = load_example()
        first = self.assert_decision(snapshot, "ALLOW", "ALLOW_OK")
        replay_key = first["envelope"]["idempotency"]["key"]
        self.assert_decision(
            snapshot,
            "BLOCK",
            "REPLAY_DETECTED",
            seen_idempotency_keys={replay_key},
        )

    def test_authorization_target_mismatch_blocks(self):
        snapshot = load_example()
        snapshot["authorization"]["target"] = "github://safal207/pythiaLabs/pulls/999@" + "a" * 40
        self.assert_decision(snapshot, "BLOCK", "AUTHORIZATION_MISMATCH")

    def test_unknown_input_field_fails_closed(self):
        snapshot = load_example()
        snapshot["unexpected"] = True
        result = self.assert_decision(snapshot, "BLOCK", GITHUB_INPUT_INVALID)
        self.assertIsNone(result["envelope"])

    def test_duplicate_check_name_fails_closed(self):
        snapshot = load_example()
        snapshot["checks"].append(dict(snapshot["checks"][0]))
        self.assert_decision(snapshot, "BLOCK", GITHUB_INPUT_INVALID)

    def test_mergeable_unknown_escalates(self):
        snapshot = load_example()
        snapshot["pull_request"]["mergeable"] = None
        result = self.assert_decision(snapshot, "ESCALATE", "PRECONDITION_UNRESOLVED")
        self.assertIn("github-pr-mergeable", result["detail"])

    def test_required_rollback_missing_escalates(self):
        snapshot = load_example()
        snapshot["recovery"]["rollback_available"] = False
        snapshot["recovery"]["rollback_ref"] = None
        self.assert_decision(snapshot, "ESCALATE", "RECOVERY_NOT_READY")


if __name__ == "__main__":
    unittest.main()
