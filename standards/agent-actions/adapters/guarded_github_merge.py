from __future__ import annotations

import copy
from threading import Lock
from typing import Any, Mapping, Protocol

from github_pr_merge_gate import evaluate_github_pr_merge, input_errors

ALLOW_OK = "ALLOW_OK"
REQUIRED_EVIDENCE_MISSING = "REQUIRED_EVIDENCE_MISSING"
EVIDENCE_TARGET_MISMATCH = "EVIDENCE_TARGET_MISMATCH"
HEAD_SHA_MISMATCH = "HEAD_SHA_MISMATCH"
ACTION_ALREADY_IN_PROGRESS = "ACTION_ALREADY_IN_PROGRESS"
ACTION_ALREADY_EXECUTED = "ACTION_ALREADY_EXECUTED"
TARGET_CHANGED_BEFORE_EXECUTION = "TARGET_CHANGED_BEFORE_EXECUTION"
CURRENT_STATE_UNAVAILABLE = "CURRENT_STATE_UNAVAILABLE"
EXECUTION_FAILED = "EXECUTION_FAILED"

NEW = "NEW"
IN_PROGRESS = "IN_PROGRESS"
SUCCEEDED = "SUCCEEDED"
FAILED = "FAILED"


class CurrentPullRequestStateProvider(Protocol):
    def get_head_sha(self, repository: str, pull_request: int) -> str:
        """Return the current GitHub head SHA for one pull request."""


class MergeExecutor(Protocol):
    def merge_pull_request(
        self,
        repository: str,
        pull_request: int,
        expected_head_sha: str,
    ) -> Mapping[str, Any]:
        """Execute a merge that is conditionally bound to expected_head_sha."""


class ExecutionStateStore(Protocol):
    def get(self, idempotency_key: str) -> str:
        """Return NEW, IN_PROGRESS, SUCCEEDED, or FAILED."""

    def reserve(self, idempotency_key: str) -> bool:
        """Atomically transition NEW to IN_PROGRESS."""

    def mark_succeeded(
        self,
        idempotency_key: str,
        result: Mapping[str, Any],
    ) -> None:
        """Transition an in-progress action to SUCCEEDED."""

    def mark_failed(self, idempotency_key: str, reason: str) -> None:
        """Transition an in-progress action to FAILED."""


class InMemoryExecutionStateStore:
    """Thread-safe reference store; PR #215 adds durable coordination."""

    def __init__(self) -> None:
        self._states: dict[str, str] = {}
        self._results: dict[str, Mapping[str, Any]] = {}
        self._lock = Lock()

    def get(self, idempotency_key: str) -> str:
        with self._lock:
            return self._states.get(idempotency_key, NEW)

    def reserve(self, idempotency_key: str) -> bool:
        with self._lock:
            if self._states.get(idempotency_key, NEW) != NEW:
                return False
            self._states[idempotency_key] = IN_PROGRESS
            return True

    def mark_succeeded(
        self,
        idempotency_key: str,
        result: Mapping[str, Any],
    ) -> None:
        with self._lock:
            if self._states.get(idempotency_key, NEW) != IN_PROGRESS:
                raise RuntimeError("only an in-progress action may succeed")
            self._states[idempotency_key] = SUCCEEDED
            self._results[idempotency_key] = dict(result)

    def mark_failed(self, idempotency_key: str, reason: str) -> None:
        with self._lock:
            if self._states.get(idempotency_key, NEW) != IN_PROGRESS:
                raise RuntimeError("only an in-progress action may fail")
            self._states[idempotency_key] = FAILED
            self._results[idempotency_key] = {"reason": reason}

    def result(self, idempotency_key: str) -> Mapping[str, Any] | None:
        with self._lock:
            return self._results.get(idempotency_key)


def _outcome(
    decision: str,
    reason_code: str,
    *,
    detail: str,
    action_id: str | None = None,
    idempotency_key: str | None = None,
    executed: bool = False,
    execution_result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "decision": decision,
        "reason_code": reason_code,
        "reason_codes": [reason_code],
        "detail": detail,
        "action_id": action_id,
        "idempotency_key": idempotency_key,
        "executed": executed,
        "execution_result": (
            dict(execution_result) if execution_result is not None else None
        ),
    }


def _missing_required_evidence(snapshot: Mapping[str, Any]) -> list[str]:
    checks = {row["name"] for row in snapshot.get("checks", [])}
    reviews = {row["reviewer"] for row in snapshot.get("reviews", [])}
    missing_checks = [
        f"check:{name}"
        for name in snapshot.get("required_checks", [])
        if name not in checks
    ]
    missing_reviews = [
        f"review:{reviewer}"
        for reviewer in snapshot.get("required_reviews", [])
        if reviewer not in reviews
    ]
    return missing_checks + missing_reviews


def _evidence_target_mismatches(snapshot: Mapping[str, Any]) -> list[str]:
    repository = snapshot["repository"]
    pull_request_number = snapshot["pull_request"]["number"]
    check_prefix = f"github-actions://{repository}/runs/"
    review_prefix = (
        f"github-review://{repository}/pulls/{pull_request_number}/"
    )
    mismatches = [
        f"check:{row['name']}"
        for row in snapshot.get("checks", [])
        if not row["run_ref"].startswith(check_prefix)
    ]
    mismatches.extend(
        f"review:{row['reviewer']}"
        for row in snapshot.get("reviews", [])
        if not row["review_ref"].startswith(review_prefix)
    )
    return mismatches


def execute_guarded_merge(
    snapshot: Mapping[str, Any],
    *,
    state_provider: CurrentPullRequestStateProvider,
    executor: MergeExecutor,
    execution_store: ExecutionStateStore,
) -> dict[str, Any]:
    """Evaluate and execute one exact-head GitHub merge at most once.

    The executor is unreachable until the Action Envelope evaluator returns
    ALLOW, the semantic idempotency key is reserved, and the current GitHub head
    is checked a second time immediately before execution.
    """

    errors = input_errors(snapshot)
    if errors:
        return _outcome(
            "BLOCK",
            "GITHUB_INPUT_INVALID",
            detail=errors[0],
        )

    missing = _missing_required_evidence(snapshot)
    if missing:
        return _outcome(
            "BLOCK",
            REQUIRED_EVIDENCE_MISSING,
            detail="missing required evidence: " + ", ".join(missing),
        )

    target_mismatches = _evidence_target_mismatches(snapshot)
    if target_mismatches:
        return _outcome(
            "BLOCK",
            EVIDENCE_TARGET_MISMATCH,
            detail=(
                "evidence locator is not bound to the proposed target: "
                + ", ".join(target_mismatches)
            ),
        )

    repository = snapshot["repository"]
    pull_request = snapshot["pull_request"]
    pull_request_number = pull_request["number"]
    expected_head_sha = pull_request["expected_head_sha"]

    try:
        first_head_sha = state_provider.get_head_sha(
            repository,
            pull_request_number,
        )
    except Exception as exc:  # external availability boundary
        return _outcome(
            "ESCALATE",
            CURRENT_STATE_UNAVAILABLE,
            detail=f"cannot load current pull-request head: {exc}",
        )

    if first_head_sha != expected_head_sha:
        return _outcome(
            "BLOCK",
            HEAD_SHA_MISMATCH,
            detail=(
                f"expected head {expected_head_sha}, "
                f"current head is {first_head_sha}"
            ),
        )

    evaluated_snapshot = copy.deepcopy(dict(snapshot))
    evaluated_snapshot["pull_request"]["observed_head_sha"] = first_head_sha
    gate = evaluate_github_pr_merge(evaluated_snapshot)
    action_id = gate.get("action_id")
    envelope = gate.get("envelope")
    idempotency_key = (
        envelope["idempotency"]["key"] if envelope is not None else None
    )

    if gate["decision"] != "ALLOW":
        return _outcome(
            gate["decision"],
            gate["reason_code"],
            detail=gate["detail"],
            action_id=action_id,
            idempotency_key=idempotency_key,
        )

    if idempotency_key is None:
        return _outcome(
            "BLOCK",
            "GITHUB_INPUT_INVALID",
            detail="allowed gate result did not contain an idempotency key",
            action_id=action_id,
        )

    if not execution_store.reserve(idempotency_key):
        existing_state = execution_store.get(idempotency_key)
        if existing_state == IN_PROGRESS:
            reason_code = ACTION_ALREADY_IN_PROGRESS
            detail = "the semantic merge action is already in progress"
        else:
            reason_code = ACTION_ALREADY_EXECUTED
            detail = f"the semantic merge action is terminal: {existing_state}"
        return _outcome(
            "BLOCK",
            reason_code,
            detail=detail,
            action_id=action_id,
            idempotency_key=idempotency_key,
        )

    try:
        second_head_sha = state_provider.get_head_sha(
            repository,
            pull_request_number,
        )
    except Exception as exc:  # external availability boundary
        execution_store.mark_failed(idempotency_key, CURRENT_STATE_UNAVAILABLE)
        return _outcome(
            "ESCALATE",
            CURRENT_STATE_UNAVAILABLE,
            detail=f"cannot re-check pull-request head before execution: {exc}",
            action_id=action_id,
            idempotency_key=idempotency_key,
        )

    if second_head_sha != expected_head_sha:
        execution_store.mark_failed(
            idempotency_key,
            TARGET_CHANGED_BEFORE_EXECUTION,
        )
        return _outcome(
            "BLOCK",
            TARGET_CHANGED_BEFORE_EXECUTION,
            detail=(
                f"head changed after evaluation: expected {expected_head_sha}, "
                f"current head is {second_head_sha}"
            ),
            action_id=action_id,
            idempotency_key=idempotency_key,
        )

    try:
        execution_result = executor.merge_pull_request(
            repository,
            pull_request_number,
            expected_head_sha,
        )
    except Exception as exc:  # execution boundary
        execution_store.mark_failed(idempotency_key, EXECUTION_FAILED)
        return _outcome(
            "BLOCK",
            EXECUTION_FAILED,
            detail=f"merge executor failed: {exc}",
            action_id=action_id,
            idempotency_key=idempotency_key,
        )

    execution_store.mark_succeeded(idempotency_key, execution_result)
    return _outcome(
        "ALLOW",
        ALLOW_OK,
        detail="gate allowed and exact-head merge executed once",
        action_id=action_id,
        idempotency_key=idempotency_key,
        executed=True,
        execution_result=execution_result,
    )
