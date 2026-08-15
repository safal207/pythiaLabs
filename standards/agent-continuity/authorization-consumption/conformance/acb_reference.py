from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
AUTH_SCHEMA = ROOT / "schema" / "authorization-occurrence.schema.json"
EXEC_SCHEMA = ROOT / "schema" / "proposed-execution.schema.json"
RECEIPT_SCHEMA = ROOT / "schema" / "consumption-receipt.schema.json"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("document root must be object")
    return value


def schema_errors(document: Mapping[str, Any], schema_path: Path) -> list[str]:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    return [error.message for error in validator.iter_errors(dict(document))]


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256_ref(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def execution_scope_preimage(execution: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "logical_operation_id": execution["logical_operation_id"],
        "tool_name": execution["tool_name"],
        "normalized_args": execution["normalized_args"],
        "actor_ref": execution["actor_ref"],
        "policy_version": execution["policy_version"],
        "authority_ref": execution["authority_ref"],
        "authority_epoch": execution["authority_epoch"],
        "relevant_state_refs": sorted(execution["relevant_state_refs"]),
    }


def compute_execution_scope_digest(execution: Mapping[str, Any]) -> str:
    return _sha256_ref(execution_scope_preimage(execution))


def resolve_occurrence(
    decision_ref: str,
    decision_event_id: str | None,
    occurrences: Sequence[Mapping[str, Any]],
) -> tuple[str, Mapping[str, Any] | None]:
    candidates = [
        item for item in occurrences
        if item.get("decision_ref") == decision_ref
    ]

    if decision_event_id is None:
        if not candidates:
            return "OCCURRENCE_NOT_FOUND", None
        if len(candidates) > 1:
            return "OCCURRENCE_AMBIGUOUS", None
        return "RESOLVED", candidates[0]

    exact = [
        item for item in occurrences
        if item.get("decision_event_id") == decision_event_id
    ]
    if not exact:
        return "OCCURRENCE_NOT_FOUND", None
    if len(exact) > 1:
        return "OCCURRENCE_AMBIGUOUS", None

    occurrence = exact[0]
    if occurrence.get("decision_ref") != decision_ref:
        return "OCCURRENCE_REF_MISMATCH", None
    return "RESOLVED", occurrence


def _receipt(
    result: str,
    reason: str,
    execution: Mapping[str, Any],
    authorization: Mapping[str, Any] | None,
) -> dict[str, Any]:
    decision_ref = authorization.get("decision_ref") if authorization else None
    decision_event_id = authorization.get("decision_event_id") if authorization else None
    scope_digest = compute_execution_scope_digest(execution)
    base = {
        "schema_version": "acb-receipt/0.1",
        "result": result,
        "reason": reason,
        "decision_ref": decision_ref,
        "decision_event_id": decision_event_id,
        "logical_operation_id": execution["logical_operation_id"],
        "execution_id": execution["execution_id"],
        "execution_scope_digest": scope_digest,
    }
    base["consumption_ref"] = _sha256_ref(base)
    return base


def attempt_consume(
    authorization: Mapping[str, Any],
    execution: Mapping[str, Any],
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    updated = copy.deepcopy(dict(authorization))

    if schema_errors(authorization, AUTH_SCHEMA):
        receipt = _receipt("BLOCKED", "authorization_schema_invalid", execution, authorization)
        return "BLOCKED", updated, receipt
    if schema_errors(execution, EXEC_SCHEMA):
        receipt = _receipt("BLOCKED", "execution_schema_invalid", execution, authorization)
        return "BLOCKED", updated, receipt

    if authorization["status"] != "resolved_allow":
        receipt = _receipt("BLOCKED", f"authorization_status_{authorization['status']}", execution, authorization)
        return "BLOCKED", updated, receipt

    if execution["cancelled"]:
        receipt = _receipt("BLOCKED", "execution_cancelled", execution, authorization)
        return "BLOCKED", updated, receipt
    if execution["superseded"]:
        receipt = _receipt("BLOCKED", "execution_superseded", execution, authorization)
        return "BLOCKED", updated, receipt

    if authorization["logical_operation_id"] != execution["logical_operation_id"]:
        receipt = _receipt("BLOCKED", "logical_operation_mismatch", execution, authorization)
        return "BLOCKED", updated, receipt

    if authorization["policy_version"] != execution["policy_version"]:
        receipt = _receipt("BLOCKED", "policy_version_mismatch", execution, authorization)
        return "BLOCKED", updated, receipt

    actual_scope = compute_execution_scope_digest(execution)
    if authorization["execution_scope_digest"] != actual_scope:
        receipt = _receipt("BLOCKED", "execution_scope_mismatch", execution, authorization)
        return "BLOCKED", updated, receipt

    bound_conditions = authorization["bound_conditions"]
    current_conditions = execution["current_conditions"]
    for condition in authorization["revalidate_if"]:
        if condition not in bound_conditions:
            receipt = _receipt("BLOCKED", f"bound_condition_missing:{condition}", execution, authorization)
            return "BLOCKED", updated, receipt
        if condition not in current_conditions:
            receipt = _receipt("BLOCKED", f"current_condition_missing:{condition}", execution, authorization)
            return "BLOCKED", updated, receipt
        if current_conditions[condition] != bound_conditions[condition]:
            receipt = _receipt("BLOCKED", f"freshness_changed:{condition}", execution, authorization)
            return "BLOCKED", updated, receipt

    usage = authorization["usage_policy"]
    mode = usage["mode"]
    max_uses = usage["max_uses"]
    use_count = authorization["use_count"]

    if execution["execution_id"] in authorization["consumed_by_execution_ids"]:
        receipt = _receipt("BLOCKED", "execution_already_consumed", execution, authorization)
        return "BLOCKED", updated, receipt

    if mode == "one_shot":
        if max_uses != 1 or use_count != 0 or authorization["consumed_by_execution_ids"]:
            receipt = _receipt("BLOCKED", "one_shot_already_consumed", execution, authorization)
            return "BLOCKED", updated, receipt
    elif mode == "reusable":
        if max_uses is not None and use_count >= max_uses:
            receipt = _receipt("BLOCKED", "reusable_limit_exhausted", execution, authorization)
            return "BLOCKED", updated, receipt
    else:
        receipt = _receipt("BLOCKED", "usage_mode_invalid", execution, authorization)
        return "BLOCKED", updated, receipt

    updated["use_count"] += 1
    updated["consumed_by_execution_ids"].append(execution["execution_id"])

    if mode == "one_shot" or (
        max_uses is not None and updated["use_count"] >= max_uses
    ):
        updated["status"] = "consumed"

    receipt = _receipt("CONSUMED", "authorization_consumed", execution, updated)
    if schema_errors(receipt, RECEIPT_SCHEMA):
        raise AssertionError("reference implementation produced invalid receipt")
    return "CONSUMED", updated, receipt
