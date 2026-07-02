from __future__ import annotations

import copy
from dataclasses import dataclass
from threading import Lock
from typing import Any, Mapping, Protocol

from github_pr_merge_gate import evaluate_github_pr_merge, input_errors

ALLOW_OK = "ALLOW_OK"
GITHUB_ENVELOPE_INVALID = "GITHUB_ENVELOPE_INVALID"
REQUIRED_EVIDENCE_MISSING = "REQUIRED_EVIDENCE_MISSING"
EVIDENCE_TARGET_MISMATCH = "EVIDENCE_TARGET_MISMATCH"
HEAD_SHA_MISMATCH = "HEAD_SHA_MISMATCH"
BASE_REF_MISMATCH = "BASE_REF_MISMATCH"
ACTION_ALREADY_IN_PROGRESS = "ACTION_ALREADY_IN_PROGRESS"
ACTION_ALREADY_EXECUTED = "ACTION_ALREADY_EXECUTED"
TARGET_CHANGED_BEFORE_EXECUTION = "TARGET_CHANGED_BEFORE_EXECUTION"
BASE_CHANGED_BEFORE_EXECUTION = "BASE_CHANGED_BEFORE_EXECUTION"
CURRENT_STATE_UNAVAILABLE = "CURRENT_STATE_UNAVAILABLE"
TRUSTED_TIME_UNAVAILABLE = "TRUSTED_TIME_UNAVAILABLE"
EXECUTION_FAILED = "EXECUTION_FAILED"

NEW = "NEW"
IN_PROGRESS = "IN_PROGRESS"
SUCCEEDED = "SUCCEEDED"
FAILED = "FAILED"
NOT_ATTEMPTED = "NOT_ATTEMPTED"
TERMINAL_STATES = frozenset({SUCCEEDED, FAILED})


@dataclass(frozen=True)
class PullRequestState:
    head_sha: str
    base_ref: str


@dataclass(frozen=True)
class ReservationObservation:
    """One atomic reservation result and the state observed under the same lock."""

    reserved: bool
    observed_state: str


class DecisionClock(Protocol):
    def now(self) -> str:
        """Return trusted RFC 3339 decision time."""


class CurrentPullRequestStateProvider(Protocol):
    def get_state(self, repository: str, pull_request: int) -> PullRequestState:
        """Return the current GitHub head SHA and base ref for one pull request."""


class MergeExecutor(Protocol):
    def merge_pull_request(
        self,
        repository: str,
        pull_request: int,
        expected_head_sha: str,
        expected_base_ref: str,
    ) -> Mapping[str, Any]:
        """Execute a merge bound to the expected head SHA and base ref."""


class ExecutionStateStore(Protocol):
    def get(self, idempotency_key: str) -> str:
        """Return NEW, IN_PROGRESS, SUCCEEDED, or FAILED for diagnostics."""

    def try_reserve(self, idempotency_key: str) -> ReservationObservation:
        """Atomically observe state and transition NEW to IN_PROGRESS."""

    def release(self, idempotency_key: str) -> None:
        """Transition an unattempted IN_PROGRESS action back to NEW."""

    def mark_succeeded(
        self,
        idempotency_key: str,
        result: Mapping[str, Any],
    ) -> None:
        """Transition an in-progress action to SUCCEEDED."""

    def mark_failed(self, idempotency_key: str, reason: str) -> None:
        """Transition an in-progress action to FAILED."""


class InMemoryExecutionStateStore:
    """Thread-safe reference store; durable coordination is separate work."""

    def __init__(self) -> None:
        self._states: dict[str, str] = {}
        self._results: dict[str, Mapping[str, Any]] = {}
        self._lock = Lock()

    def get(self, idempotency_key: str) -> str:
        with self._lock:
            return self._states.get(idempotency_key, NEW)

    def try_reserve(self, idempotency_key: str) -> ReservationObservation:
        with self._lock:
            observed_state = self._states.get(idempotency_key, NEW)
            if observed_state != NEW:
                return ReservationObservation(False, observed_state)
            self._states[idempotency_key] = IN_PROGRESS
            return ReservationObservation(True, NEW)

    def reserve(self, idempotency_key: str) -> bool:
        """Compatibility helper; guarded execution uses try_reserve()."""

        return self.try_reserve(idempotency_key).reserved

    def release(self, idempotency_key: str) -> None:
        with self._lock:
            if self._states.get(idempotency_key, NEW) != IN_PROGRESS:
                raise RuntimeError("only an unattempted in-progress action may be released")
            self._states.pop(idempotency_key, None)
            self._results.pop(idempotency_key, None)

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
    executor_called: bool = False,
    execution_status: str = NOT_ATTEMPTED,
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
        "executor_called": executor_called,
        "execution_status": execution_status,
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
    check_prefix = f"github-actions://{repository}/pulls/{pull_request_number}/runs/"
    review_prefix = f"github-review://{repository}/pulls/{pull_request_number}/"
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


def _extract_idempotency_key(envelope: Any) -> str | None:
    if not isinstance(envelope, Mapping):
        return None
    idempotency = envelope.get("idempotency")
    if not isinstance(idempotency, Mapping):
        return None
    key = idempotency.get("key")
    return key if isinstance(key, str) and key else None


def _reservation_failure(
    observation: ReservationObservation,
    *,
    action_id: str | None,
    idempotency_key: str,
) -> dict[str, Any]:
    observed_state = observation.observed_state
    if observed_state == IN_PROGRESS:
        return _outcome(
            "BLOCK",
            ACTION_ALREADY_IN_PROGRESS,
            detail="the semantic merge action is already in progress",
            action_id=action_id,
            idempotency_key=idempotency_key,
        )
    if observed_state in TERMINAL_STATES:
        return _outcome(
            "BLOCK",
            ACTION_ALREADY_EXECUTED,
            detail=f"the semantic merge action is terminal: {observed_state}",
            action_id=action_id,
            idempotency_key=idempotency_key,
        )
    return _outcome(
        "ESCALATE",
        CURRENT_STATE_UNAVAILABLE,
        detail=(
            "atomic reservation failed with a non-terminal coordination state: "
            f"{observed_state}"
        ),
        action_id=action_id,
        idempotency_key=idempotency_key,
    )


def execute_guarded_merge(
    snapshot: Mapping[str, Any],
    *,
    clock: DecisionClock,
    state_provider: CurrentPullRequestStateProvider,
    executor: MergeExecutor,
    execution_store: ExecutionStateStore,
) -> dict[str, Any]:
    """Evaluate and execute one exact-target GitHub merge at most once.

    The caller-supplied snapshot cannot choose the effective decision time. The
    service overwrites it with a trusted clock value before freshness checks.
    The executor is unreachable until the Action Envelope evaluator returns
    ALLOW, reservation succeeds atomically, and the current GitHub head and base
    are checked a second time immediately before execution.
    """

    errors = input_errors(snapshot)
    if errors:
        return _outcome("BLOCK", "GITHUB_INPUT_INVALID", detail=errors[0])

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

    try:
        trusted_decision_time = clock.now()
    except Exception as exc:
        return _outcome(
            "ESCALATE",
            TRUSTED_TIME_UNAVAILABLE,
            detail=f"cannot obtain trusted decision time: {exc}",
        )

    repository = snapshot["repository"]
    pull_request = snapshot["pull_request"]
    pull_request_number = pull_request["number"]
    expected_head_sha = pull_request["expected_head_sha"]
    expected_base_ref = pull_request["base_ref"]

    try:
        first_state = state_provider.get_state(repository, pull_request_number)
    except Exception as exc:
        return _outcome(
            "ESCALATE",
            CURRENT_STATE_UNAVAILABLE,
            detail=f"cannot load current pull-request state: {exc}",
        )

    if first_state.head_sha != expected_head_sha:
        return _outcome(
            "BLOCK",
            HEAD_SHA_MISMATCH,
            detail=f"expected head {expected_head_sha}, current head is {first_state.head_sha}",
        )
    if first_state.base_ref != expected_base_ref:
        return _outcome(
            "BLOCK",
            BASE_REF_MISMATCH,
            detail=f"expected base {expected_base_ref}, current base is {first_state.base_ref}",
        )

    evaluated_snapshot = copy.deepcopy(dict(snapshot))
    evaluated_snapshot["decision_time"] = trusted_decision_time
    evaluated_snapshot["pull_request"]["observed_head_sha"] = first_state.head_sha
    gate = evaluate_github_pr_merge(evaluated_snapshot)
    action_id = gate.get("action_id")
    idempotency_key = _extract_idempotency_key(gate.get("envelope"))

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
            GITHUB_ENVELOPE_INVALID,
            detail="allowed gate result did not contain an idempotency key",
            action_id=action_id,
        )

    reservation = execution_store.try_reserve(idempotency_key)
    if not reservation.reserved:
        return _reservation_failure(
            reservation,
            action_id=action_id,
            idempotency_key=idempotency_key,
        )

    try:
        second_state = state_provider.get_state(repository, pull_request_number)
    except Exception as exc:
        execution_store.release(idempotency_key)
        return _outcome(
            "ESCALATE",
            CURRENT_STATE_UNAVAILABLE,
            detail=f"cannot re-check pull-request state before execution: {exc}",
            action_id=action_id,
            idempotency_key=idempotency_key,
        )

    if second_state.head_sha != expected_head_sha:
        execution_store.mark_failed(idempotency_key, TARGET_CHANGED_BEFORE_EXECUTION)
        return _outcome(
            "BLOCK",
            TARGET_CHANGED_BEFORE_EXECUTION,
            detail=(
                f"head changed after evaluation: expected {expected_head_sha}, "
                f"current head is {second_state.head_sha}"
            ),
            action_id=action_id,
            idempotency_key=idempotency_key,
        )
    if second_state.base_ref != expected_base_ref:
        execution_store.mark_failed(idempotency_key, BASE_CHANGED_BEFORE_EXECUTION)
        return _outcome(
            "BLOCK",
            BASE_CHANGED_BEFORE_EXECUTION,
            detail=(
                f"base changed after evaluation: expected {expected_base_ref}, "
                f"current base is {second_state.base_ref}"
            ),
            action_id=action_id,
            idempotency_key=idempotency_key,
        )

    try:
        execution_result = executor.merge_pull_request(
            repository,
            pull_request_number,
            expected_head_sha,
            expected_base_ref,
        )
    except Exception as exc:
        execution_store.mark_failed(idempotency_key, EXECUTION_FAILED)
        return _outcome(
            "BLOCK",
            EXECUTION_FAILED,
            detail=f"merge executor failed: {exc}",
            action_id=action_id,
            idempotency_key=idempotency_key,
            executor_called=True,
            execution_status=FAILED,
        )

    execution_store.mark_succeeded(idempotency_key, execution_result)
    return _outcome(
        "ALLOW",
        ALLOW_OK,
        detail="gate allowed and exact-target merge executed once",
        action_id=action_id,
        idempotency_key=idempotency_key,
        executed=True,
        executor_called=True,
        execution_status=SUCCEEDED,
        execution_result=execution_result,
    )
