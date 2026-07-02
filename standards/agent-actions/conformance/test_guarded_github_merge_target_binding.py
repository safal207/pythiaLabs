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

from guarded_github_merge import (  # noqa: E402
    EVIDENCE_TARGET_MISMATCH,
    InMemoryExecutionStateStore,
    NOT_ATTEMPTED,
    PullRequestState,
    execute_guarded_merge,
)

EXAMPLE_PATH = ROOT / "examples" / "github-pr-merge-gate-input.example.json"


class FixedClock:
    def now(self) -> str:
        return "2026-07-01T21:05:00Z"


class RecordingStateProvider:
    def __init__(self) -> None:
        self.calls = 0

    def get_state(self, repository: str, pull_request: int) -> PullRequestState:
        self.calls += 1
        return PullRequestState("a" * 40, "main")


class RecordingExecutor:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int, str, str]] = []

    def merge_pull_request(
        self,
        repository: str,
        pull_request: int,
        expected_head_sha: str,
        expected_base_ref: str,
    ):
        self.calls.append(
            (repository, pull_request, expected_head_sha, expected_base_ref)
        )
        return {"merged": True}


class GuardedGitHubMergeTargetBindingTest(unittest.TestCase):
    def test_workflow_locator_for_another_pull_request_blocks_before_state_lookup(self):
        snapshot = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
        snapshot["checks"][0]["run_ref"] = (
            "github-actions://safal207/pythiaLabs/pulls/999/runs/495"
        )
        provider = RecordingStateProvider()
        executor = RecordingExecutor()

        result = execute_guarded_merge(
            snapshot,
            clock=FixedClock(),
            state_provider=provider,
            executor=executor,
            execution_store=InMemoryExecutionStateStore(),
        )

        self.assertEqual(
            (result["decision"], result["reason_code"]),
            ("BLOCK", EVIDENCE_TARGET_MISMATCH),
        )
        self.assertEqual(provider.calls, 0)
        self.assertEqual(executor.calls, [])
        self.assertFalse(result["executor_called"])
        self.assertEqual(result["execution_status"], NOT_ATTEMPTED)


if __name__ == "__main__":
    unittest.main()
