from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INPUT_SCHEMA_PATH = ROOT / "schema" / "github-pr-merge-gate-input.schema.json"
REFERENCE_PATH = ROOT / "conformance" / "action_envelope_reference.py"

INPUT_SCHEMA_VERSION = "pythia.github_pr_merge_gate.v0.1"
GITHUB_INPUT_INVALID = "GITHUB_INPUT_INVALID"


def _load_action_reference():
    spec = importlib.util.spec_from_file_location(
        "pythia_action_envelope_reference",
        REFERENCE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Action Envelope reference: {REFERENCE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ACTION_REFERENCE = _load_action_reference()


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        dict(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256_hex(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _stable_suffix(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def load_input_schema() -> dict[str, Any]:
    value = json.loads(INPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("GitHub gate schema root must be an object")
    Draft202012Validator.check_schema(value)
    return value


def input_errors(snapshot: Mapping[str, Any]) -> list[str]:
    validator = Draft202012Validator(
        load_input_schema(),
        format_checker=FormatChecker(),
    )
    errors = [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in sorted(
            validator.iter_errors(dict(snapshot)),
            key=lambda item: [str(part) for part in item.absolute_path],
        )
    ]
    if errors:
        return errors

    checks = [row["name"] for row in snapshot["checks"]]
    reviews = [row["reviewer"] for row in snapshot["reviews"]]
    if len(checks) != len(set(checks)):
        errors.append("checks: duplicate check name")
    if len(reviews) != len(set(reviews)):
        errors.append("reviews: duplicate reviewer")
    return errors


def target_ref(snapshot: Mapping[str, Any]) -> str:
    pull_request = snapshot["pull_request"]
    return (
        f"github://{snapshot['repository']}/pulls/{pull_request['number']}"
        f"@{pull_request['expected_head_sha']}?base={pull_request['base_ref']}"
    )


def canonical_action_id(snapshot: Mapping[str, Any]) -> str:
    pull_request = snapshot["pull_request"]
    identity = {
        "operation": "merge_pull_request",
        "repository": snapshot["repository"],
        "pull_request_number": pull_request["number"],
        "base_ref": pull_request["base_ref"],
        "expected_head_sha": pull_request["expected_head_sha"],
    }
    return f"github-pr-merge:sha256:{_sha256_hex(identity)}"


def _evidence(
    *,
    action_id: str,
    evidence_id: str,
    evidence_type: str,
    locator: str,
    observed_at: str,
    expires_at: str,
    source_type: str,
    source_ref: str,
    record: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "evidence_id": evidence_id,
        "action_id": action_id,
        "evidence_type": evidence_type,
        "locator": locator,
        "digest": f"sha256:{_sha256_hex(record)}",
        "observed_at": observed_at,
        "expires_at": expires_at,
        "provenance": {
            "source_type": source_type,
            "source_ref": source_ref,
        },
    }


def _status_for_check(row: Mapping[str, Any], expected_head_sha: str) -> str:
    if row["head_sha"] != expected_head_sha:
        return "failed"
    if row["conclusion"] == "success":
        return "passed"
    if row["conclusion"] == "pending":
        return "unknown"
    return "failed"


def _status_for_review(row: Mapping[str, Any], expected_head_sha: str) -> str:
    if row["head_sha"] != expected_head_sha:
        return "failed"
    if row["verdict"] == "approved":
        return "passed"
    if row["verdict"] == "pending":
        return "unknown"
    return "failed"


def build_github_pr_merge_envelope(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    errors = input_errors(snapshot)
    if errors:
        raise ValueError(errors[0])

    pull_request = snapshot["pull_request"]
    expected_head_sha = pull_request["expected_head_sha"]
    base_ref = pull_request["base_ref"]
    action_id = canonical_action_id(snapshot)
    target = target_ref(snapshot)
    evidence: list[dict[str, Any]] = []
    preconditions: list[dict[str, Any]] = []

    head_evidence_id = "ev-github-pr-head"
    evidence.append(
        _evidence(
            action_id=action_id,
            evidence_id=head_evidence_id,
            evidence_type="runtime_receipt",
            locator=f"github://{snapshot['repository']}/pulls/{pull_request['number']}",
            observed_at=pull_request["observed_at"],
            expires_at=pull_request["expires_at"],
            source_type="runtime",
            source_ref=f"github-pr/{pull_request['number']}/head-and-base",
            record=pull_request,
        )
    )
    preconditions.append(
        {
            "precondition_id": "github-head-matches",
            "status": (
                "passed"
                if pull_request["observed_head_sha"] == expected_head_sha
                else "failed"
            ),
            "evidence_refs": [head_evidence_id],
        }
    )
    mergeable = pull_request["mergeable"]
    preconditions.append(
        {
            "precondition_id": "github-pr-mergeable",
            "status": "unknown" if mergeable is None else ("passed" if mergeable else "failed"),
            "evidence_refs": [head_evidence_id],
        }
    )

    checks_by_name = {row["name"]: row for row in snapshot["checks"]}
    for name in snapshot["required_checks"]:
        suffix = _stable_suffix(name)
        evidence_id = f"ev-check-{suffix}"
        row = checks_by_name.get(name)
        if row is None:
            requirement = {"required_check": name, "present": False}
            evidence.append(
                _evidence(
                    action_id=action_id,
                    evidence_id=evidence_id,
                    evidence_type="policy_snapshot",
                    locator=f"policy://github/required-check/{suffix}",
                    observed_at=snapshot["decision_time"],
                    expires_at=snapshot["authorization"]["valid_until"],
                    source_type="policy",
                    source_ref=f"required-check/{name}",
                    record=requirement,
                )
            )
            status = "unknown"
        else:
            evidence.append(
                _evidence(
                    action_id=action_id,
                    evidence_id=evidence_id,
                    evidence_type="test_result",
                    locator=row["run_ref"],
                    observed_at=row["observed_at"],
                    expires_at=row["expires_at"],
                    source_type="workflow",
                    source_ref=row["run_ref"],
                    record=row,
                )
            )
            status = _status_for_check(row, expected_head_sha)
        preconditions.append(
            {
                "precondition_id": f"github-check-{suffix}",
                "status": status,
                "evidence_refs": [evidence_id],
            }
        )

    reviews_by_name = {row["reviewer"]: row for row in snapshot["reviews"]}
    for reviewer in snapshot["required_reviews"]:
        suffix = _stable_suffix(reviewer)
        evidence_id = f"ev-review-{suffix}"
        row = reviews_by_name.get(reviewer)
        if row is None:
            requirement = {"required_reviewer": reviewer, "present": False}
            evidence.append(
                _evidence(
                    action_id=action_id,
                    evidence_id=evidence_id,
                    evidence_type="policy_snapshot",
                    locator=f"policy://github/required-review/{suffix}",
                    observed_at=snapshot["decision_time"],
                    expires_at=snapshot["authorization"]["valid_until"],
                    source_type="policy",
                    source_ref=f"required-review/{reviewer}",
                    record=requirement,
                )
            )
            status = "unknown"
        else:
            source_type = "user" if row["reviewer_type"] == "human" else "tool"
            evidence.append(
                _evidence(
                    action_id=action_id,
                    evidence_id=evidence_id,
                    evidence_type="approval",
                    locator=row["review_ref"],
                    observed_at=row["submitted_at"],
                    expires_at=row["expires_at"],
                    source_type=source_type,
                    source_ref=row["review_ref"],
                    record=row,
                )
            )
            status = _status_for_review(row, expected_head_sha)
        preconditions.append(
            {
                "precondition_id": f"github-review-{suffix}",
                "status": status,
                "evidence_refs": [evidence_id],
            }
        )

    envelope = {
        "schema_version": "1.0",
        "envelope_id": f"env:{action_id}",
        "action_id": action_id,
        "created_at": snapshot["created_at"],
        "decision_time": snapshot["decision_time"],
        "actor": dict(snapshot["actor"]),
        "request": {
            "capability": "repository.merge",
            "operation": "merge_pull_request",
            "target": target,
            "environment": "github",
        },
        "authorization": dict(snapshot["authorization"]),
        "preconditions": preconditions,
        "evidence": evidence,
        "idempotency": {
            "key": (
                f"github:merge:{snapshot['repository']}:{pull_request['number']}"
                f":{base_ref}:{expected_head_sha}"
            ),
            "replay_policy": "reject_duplicate",
        },
        "recovery": dict(snapshot["recovery"]),
        "expected_state_transition": {
            "from": f"open:{base_ref}@{expected_head_sha}",
            "to": f"merged:{base_ref}@{expected_head_sha}",
        },
    }
    return _ACTION_REFERENCE.with_computed_digest(envelope)


def evaluate_github_pr_merge(
    snapshot: Mapping[str, Any],
    *,
    seen_idempotency_keys: Iterable[str] = (),
) -> dict[str, Any]:
    errors = input_errors(snapshot)
    if errors:
        return {
            "decision": "BLOCK",
            "reason_code": GITHUB_INPUT_INVALID,
            "detail": errors[0],
            "action_id": None,
            "expected_head_sha": None,
            "expected_base_ref": None,
            "envelope": None,
        }

    envelope = build_github_pr_merge_envelope(snapshot)
    result = _ACTION_REFERENCE.evaluate_action(
        envelope,
        seen_idempotency_keys=seen_idempotency_keys,
    )
    return {
        **result,
        "action_id": envelope["action_id"],
        "expected_head_sha": snapshot["pull_request"]["expected_head_sha"],
        "expected_base_ref": snapshot["pull_request"]["base_ref"],
        "envelope": envelope,
    }
