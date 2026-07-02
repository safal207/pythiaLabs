from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ADAPTERS = ROOT / "adapters"
if str(ADAPTERS) not in sys.path:
    sys.path.insert(0, str(ADAPTERS))

from guarded_github_merge import (  # noqa: E402
    ACTION_ALREADY_EXECUTED,
    ACTION_ALREADY_IN_PROGRESS,
    BASE_CHANGED_BEFORE_EXECUTION,
    BASE_REF_MISMATCH,
    CURRENT_STATE_UNAVAILABLE,
    EVIDENCE_TARGET_MISMATCH,
    EXECUTION_FAILED,
    FAILED,
    GITHUB_ENVELOPE_INVALID,
    HEAD_SHA_MISMATCH,
    IN_PROGRESS,
    InMemoryExecutionStateStore,
    NEW,
    NOT_ATTEMPTED,
    PullRequestState,
    REQUIRED_EVIDENCE_MISSING,
    SUCCEEDED,
    TARGET_CHANGED_BEFORE_EXECUTION,
    TRUSTED_TIME_UNAVAILABLE,
    execute_guarded_merge,
)

EXAMPLE_PATH = ROOT / "examples" / "github-pr-merge-gate-input.example.json"
TRUSTED_DECISION_TIME = "2026-07-01T21:05:00Z"


def load_example():
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


class FakeClock:
    def __init__(
        self,
        value: str = TRUSTED_DECISION_TIME,
        *,
        fail: bool = False,
    ) -> None:
        self.value = value
        self.fail = fail

    def now(self) -> str:
        if self.fail:
            raise RuntimeError("trusted clock unavailable")
        return self.value


class FakeStateProvider:
    def __init__(self, *states: object) -> None:
        self._states = list(states)
        self.calls = 0

    def get_state(self, repository: str, pull_request: int) -> PullRequestState:
        self.calls += 1
        if not self._states:
            raise RuntimeError("no configured state")
        value = self._states.pop(0)
        if value == "ERROR":
            raise RuntimeError("GitHub unavailable")
        if isinstance(value, tuple):
            head_sha, base_ref = value
            return PullRequestState(str(head_sha), str(base_ref))
        return PullRequestState(str(value), "main")


class FakeMergeExecutor:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
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
        if self.fail:
            raise RuntimeError("merge rejected")
        return {
            "merged": True,
            "sha": expected_head_sha,
            "base_ref": expected_base_ref,
        }


class GuardedGitHubMergeTest(unittest.TestCase):
    def execute(self, snapshot, provider, executor, store=None, clock=None):
        execution_store = (
            store if store is not None else InMemoryExecutionStateStore()
        )
        decision_clock = clock if clock is not None else FakeClock()
        return execute_guarded_merge(
            snapshot,
            clock=decision_clock,
            state_provider=provider,
            executor=executor,
            execution_store=execution_store,
        )

    def assert_not_attempted(self, result, executor):
        self.assertFalse(result["executed"])
        self.assertFalse(result["executor_called"])
        self.assertEqual(result["execution_status"], NOT_ATTEMPTED)
        self.assertEqual(executor.calls, [])

    def test_allow_executes_once_after_two_exact_target_reads(self):
        snapshot = load_example()
        expected = snapshot["pull_request"]["expected_head_sha"]
        provider = FakeStateProvider(expected, expected)
        executor = FakeMergeExecutor()
        store = InMemoryExecutionStateStore()

        result = self.execute(snapshot, provider, executor, store)

        self.assertEqual(
            (result["decision"], result["reason_code"]),
            ("ALLOW", "ALLOW_OK"),
        )
        self.assertTrue(result["executed"])
        self.assertTrue(result["executor_called"])
        self.assertEqual(result["execution_status"], SUCCEEDED)
        self.assertEqual(provider.calls, 2)
        self.assertEqual(len(executor.calls), 1)
        self.assertEqual(executor.calls[0][3], "main")
        self.assertEqual(store.get(result["idempotency_key"]), SUCCEEDED)

    def test_initial_head_mismatch_blocks_without_executor(self):
        snapshot = load_example()
        provider = FakeStateProvider("b" * 40)
        executor = FakeMergeExecutor()

        result = self.execute(snapshot, provider, executor)

        self.assertEqual(result["reason_code"], HEAD_SHA_MISMATCH)
        self.assert_not_attempted(result, executor)

    def test_initial_base_mismatch_blocks_without_executor(self):
        snapshot = load_example()
        expected = snapshot["pull_request"]["expected_head_sha"]
        provider = FakeStateProvider((expected, "release"))
        executor = FakeMergeExecutor()

        result = self.execute(snapshot, provider, executor)

        self.assertEqual(result["reason_code"], BASE_REF_MISMATCH)
        self.assert_not_attempted(result, executor)

    def test_missing_required_check_blocks_not_escalates(self):
        snapshot = load_example()
        snapshot["checks"] = [
            row for row in snapshot["checks"] if row["name"] != "Security"
        ]
        expected = snapshot["pull_request"]["expected_head_sha"]
        provider = FakeStateProvider(expected)
        executor = FakeMergeExecutor()

        result = self.execute(snapshot, provider, executor)

        self.assertEqual(
            (result["decision"], result["reason_code"]),
            ("BLOCK", REQUIRED_EVIDENCE_MISSING),
        )
        self.assertEqual(provider.calls, 0)
        self.assert_not_attempted(result, executor)

    def test_missing_required_review_blocks_not_escalates(self):
        snapshot = load_example()
        snapshot["reviews"] = [
            row
            for row in snapshot["reviews"]
            if row["reviewer"] != "coderabbitai"
        ]
        provider = FakeStateProvider()
        executor = FakeMergeExecutor()

        result = self.execute(snapshot, provider, executor)

        self.assertEqual(result["reason_code"], REQUIRED_EVIDENCE_MISSING)
        self.assertEqual(provider.calls, 0)
        self.assert_not_attempted(result, executor)

    def test_foreign_approval_does_not_satisfy_required_reviewer(self):
        snapshot = load_example()
        snapshot["reviews"][0]["reviewer"] = "mallory"
        provider = FakeStateProvider()
        executor = FakeMergeExecutor()

        result = self.execute(snapshot, provider, executor)

        self.assertEqual(result["reason_code"], REQUIRED_EVIDENCE_MISSING)
        self.assertEqual(provider.calls, 0)
        self.assert_not_attempted(result, executor)

    def test_review_for_another_pull_request_blocks(self):
        snapshot = load_example()
        snapshot["reviews"][0]["review_ref"] = (
            "github-review://safal207/pythiaLabs/pulls/999/coderabbitai"
        )
        provider = FakeStateProvider()
        executor = FakeMergeExecutor()

        result = self.execute(snapshot, provider, executor)

        self.assertEqual(result["reason_code"], EVIDENCE_TARGET_MISMATCH)
        self.assertEqual(provider.calls, 0)
        self.assert_not_attempted(result, executor)

    def test_check_from_another_repository_blocks(self):
        snapshot = load_example()
        snapshot["checks"][0]["run_ref"] = (
            "github-actions://attacker/fork/pulls/214/runs/1"
        )
        provider = FakeStateProvider()
        executor = FakeMergeExecutor()

        result = self.execute(snapshot, provider, executor)

        self.assertEqual(result["reason_code"], EVIDENCE_TARGET_MISMATCH)
        self.assertEqual(provider.calls, 0)
        self.assert_not_attempted(result, executor)

    def test_backdated_snapshot_cannot_extend_evidence_freshness(self):
        snapshot = load_example()
        snapshot["decision_time"] = "2026-07-01T21:01:00Z"
        snapshot["checks"][0]["expires_at"] = "2026-07-01T21:04:59Z"
        expected = snapshot["pull_request"]["expected_head_sha"]
        provider = FakeStateProvider(expected)
        executor = FakeMergeExecutor()

        result = self.execute(snapshot, provider, executor)

        self.assertEqual(
            (result["decision"], result["reason_code"]),
            ("BLOCK", "EVIDENCE_STALE"),
        )
        self.assert_not_attempted(result, executor)

    def test_trusted_clock_failure_escalates_without_executor(self):
        snapshot = load_example()
        provider = FakeStateProvider()
        executor = FakeMergeExecutor()

        result = self.execute(
            snapshot,
            provider,
            executor,
            clock=FakeClock(fail=True),
        )

        self.assertEqual(
            (result["decision"], result["reason_code"]),
            ("ESCALATE", TRUSTED_TIME_UNAVAILABLE),
        )
        self.assertEqual(provider.calls, 0)
        self.assert_not_attempted(result, executor)

    def test_old_head_check_blocks_without_executor(self):
        snapshot = load_example()
        snapshot["checks"][0]["head_sha"] = "b" * 40
        expected = snapshot["pull_request"]["expected_head_sha"]
        provider = FakeStateProvider(expected)
        executor = FakeMergeExecutor()

        result = self.execute(snapshot, provider, executor)

        self.assertEqual(
            (result["decision"], result["reason_code"]),
            ("BLOCK", "PRECONDITION_FAILED"),
        )
        self.assert_not_attempted(result, executor)

    def test_head_change_between_gate_and_executor_blocks(self):
        snapshot = load_example()
        expected = snapshot["pull_request"]["expected_head_sha"]
        provider = FakeStateProvider(expected, "b" * 40)
        executor = FakeMergeExecutor()
        store = InMemoryExecutionStateStore()

        result = self.execute(snapshot, provider, executor, store)

        self.assertEqual(result["reason_code"], TARGET_CHANGED_BEFORE_EXECUTION)
        self.assert_not_attempted(result, executor)
        self.assertEqual(store.get(result["idempotency_key"]), FAILED)

    def test_base_change_between_gate_and_executor_blocks(self):
        snapshot = load_example()
        expected = snapshot["pull_request"]["expected_head_sha"]
        provider = FakeStateProvider((expected, "main"), (expected, "release"))
        executor = FakeMergeExecutor()
        store = InMemoryExecutionStateStore()

        result = self.execute(snapshot, provider, executor, store)

        self.assertEqual(result["reason_code"], BASE_CHANGED_BEFORE_EXECUTION)
        self.assert_not_attempted(result, executor)
        self.assertEqual(store.get(result["idempotency_key"]), FAILED)

    def test_transient_second_state_read_failure_releases_for_retry(self):
        snapshot = load_example()
        expected = snapshot["pull_request"]["expected_head_sha"]
        executor = FakeMergeExecutor()
        store = InMemoryExecutionStateStore()

        first = self.execute(
            snapshot,
            FakeStateProvider(expected, "ERROR"),
            executor,
            store,
        )

        self.assertEqual(
            (first["decision"], first["reason_code"]),
            ("ESCALATE", CURRENT_STATE_UNAVAILABLE),
        )
        self.assert_not_attempted(first, executor)
        self.assertEqual(store.get(first["idempotency_key"]), NEW)

        second = self.execute(
            snapshot,
            FakeStateProvider(expected, expected),
            executor,
            store,
        )

        self.assertEqual(second["reason_code"], "ALLOW_OK")
        self.assertEqual(len(executor.calls), 1)
        self.assertEqual(store.get(second["idempotency_key"]), SUCCEEDED)

    def test_allowed_gate_without_idempotency_key_is_envelope_invalid(self):
        snapshot = load_example()
        expected = snapshot["pull_request"]["expected_head_sha"]
        provider = FakeStateProvider(expected)
        executor = FakeMergeExecutor()
        fake_gate = {
            "decision": "ALLOW",
            "reason_code": "ALLOW_OK",
            "detail": "synthetic invariant probe",
            "action_id": "action-test",
            "envelope": {},
        }

        with patch(
            "guarded_github_merge.evaluate_github_pr_merge",
            return_value=fake_gate,
        ):
            result = self.execute(snapshot, provider, executor)

        self.assertEqual(
            (result["decision"], result["reason_code"]),
            ("BLOCK", GITHUB_ENVELOPE_INVALID),
        )
        self.assertEqual(provider.calls, 1)
        self.assert_not_attempted(result, executor)

    def test_successful_action_cannot_execute_twice(self):
        snapshot = load_example()
        expected = snapshot["pull_request"]["expected_head_sha"]
        provider = FakeStateProvider(expected, expected, expected)
        executor = FakeMergeExecutor()
        store = InMemoryExecutionStateStore()

        first = self.execute(snapshot, provider, executor, store)
        second = self.execute(snapshot, provider, executor, store)

        self.assertEqual(first["reason_code"], "ALLOW_OK")
        self.assertEqual(second["reason_code"], ACTION_ALREADY_EXECUTED)
        self.assertFalse(second["executor_called"])
        self.assertEqual(len(executor.calls), 1)

    def test_in_progress_action_is_blocked(self):
        snapshot = load_example()
        expected = snapshot["pull_request"]["expected_head_sha"]
        probe = self.execute(
            snapshot,
            FakeStateProvider(expected, expected),
            FakeMergeExecutor(),
        )
        key = probe["idempotency_key"]
        store = InMemoryExecutionStateStore()
        self.assertTrue(store.reserve(key))
        self.assertEqual(store.get(key), IN_PROGRESS)
        provider = FakeStateProvider(expected)
        executor = FakeMergeExecutor()

        result = self.execute(snapshot, provider, executor, store)

        self.assertEqual(result["reason_code"], ACTION_ALREADY_IN_PROGRESS)
        self.assert_not_attempted(result, executor)

    def test_current_state_unavailable_escalates(self):
        snapshot = load_example()
        provider = FakeStateProvider("ERROR")
        executor = FakeMergeExecutor()

        result = self.execute(snapshot, provider, executor)

        self.assertEqual(
            (result["decision"], result["reason_code"]),
            ("ESCALATE", CURRENT_STATE_UNAVAILABLE),
        )
        self.assert_not_attempted(result, executor)

    def test_executor_failure_is_terminal_and_reported_as_attempted(self):
        snapshot = load_example()
        expected = snapshot["pull_request"]["expected_head_sha"]
        provider = FakeStateProvider(expected, expected)
        executor = FakeMergeExecutor(fail=True)
        store = InMemoryExecutionStateStore()

        result = self.execute(snapshot, provider, executor, store)

        self.assertEqual(
            (result["decision"], result["reason_code"]),
            ("BLOCK", EXECUTION_FAILED),
        )
        self.assertFalse(result["executed"])
        self.assertTrue(result["executor_called"])
        self.assertEqual(result["execution_status"], FAILED)
        self.assertEqual(len(executor.calls), 1)
        self.assertEqual(store.get(result["idempotency_key"]), FAILED)


if __name__ == "__main__":
    unittest.main()
