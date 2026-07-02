from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ADAPTERS = ROOT / "adapters"
if str(ADAPTERS) not in sys.path:
    sys.path.insert(0, str(ADAPTERS))

from guarded_github_merge import (  # noqa: E402
    ACTION_ALREADY_IN_PROGRESS,
    CURRENT_STATE_UNAVAILABLE,
    IN_PROGRESS,
    NEW,
    NOT_ATTEMPTED,
    PullRequestState,
    ReservationObservation,
    execute_guarded_merge,
)

EXAMPLE_PATH = ROOT / "examples" / "github-pr-merge-gate-input.example.json"


def load_example() -> dict[str, Any]:
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


class FixedClock:
    def now(self) -> str:
        return "2026-07-01T21:05:00Z"


class FixedStateProvider:
    def __init__(self, head_sha: str) -> None:
        self.head_sha = head_sha
        self.calls = 0

    def get_state(self, repository: str, pull_request: int) -> PullRequestState:
        self.calls += 1
        return PullRequestState(self.head_sha, "main")


class RecordingExecutor:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int, str, str]] = []

    def merge_pull_request(
        self,
        repository: str,
        pull_request: int,
        expected_head_sha: str,
        expected_base_ref: str,
    ) -> Mapping[str, Any]:
        self.calls.append(
            (repository, pull_request, expected_head_sha, expected_base_ref)
        )
        return {"merged": True}


class ReleaseAfterAtomicObservationStore:
    """Simulate release immediately after one locked failed observation."""

    def __init__(self) -> None:
        self.state = IN_PROGRESS
        self.get_calls = 0

    def get(self, idempotency_key: str) -> str:
        self.get_calls += 1
        return self.state

    def try_reserve(self, idempotency_key: str) -> ReservationObservation:
        observed = self.state
        self.state = NEW
        return ReservationObservation(False, observed)

    def release(self, idempotency_key: str) -> None:
        raise AssertionError("release must not be called after failed reservation")

    def mark_succeeded(
        self,
        idempotency_key: str,
        result: Mapping[str, Any],
    ) -> None:
        raise AssertionError("success must be unreachable")

    def mark_failed(self, idempotency_key: str, reason: str) -> None:
        raise AssertionError("failure transition must be unreachable")


class ImpossibleNewObservationStore(ReleaseAfterAtomicObservationStore):
    def try_reserve(self, idempotency_key: str) -> ReservationObservation:
        return ReservationObservation(False, NEW)


class GuardedMergeAtomicReservationTest(unittest.TestCase):
    def execute(self, store):
        snapshot = load_example()
        expected = snapshot["pull_request"]["expected_head_sha"]
        executor = RecordingExecutor()
        result = execute_guarded_merge(
            snapshot,
            clock=FixedClock(),
            state_provider=FixedStateProvider(expected),
            executor=executor,
            execution_store=store,
        )
        return result, executor

    def test_release_after_failed_reservation_cannot_change_classification(self):
        store = ReleaseAfterAtomicObservationStore()

        result, executor = self.execute(store)

        self.assertEqual(store.state, NEW)
        self.assertEqual(store.get_calls, 0)
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            ("BLOCK", ACTION_ALREADY_IN_PROGRESS),
        )
        self.assertFalse(result["executor_called"])
        self.assertEqual(result["execution_status"], NOT_ATTEMPTED)
        self.assertEqual(executor.calls, [])

    def test_failed_reservation_observing_new_is_not_terminal(self):
        store = ImpossibleNewObservationStore()

        result, executor = self.execute(store)

        self.assertEqual(store.get_calls, 0)
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            ("ESCALATE", CURRENT_STATE_UNAVAILABLE),
        )
        self.assertNotEqual(result["reason_code"], "ACTION_ALREADY_EXECUTED")
        self.assertFalse(result["executor_called"])
        self.assertEqual(executor.calls, [])


if __name__ == "__main__":
    unittest.main()
