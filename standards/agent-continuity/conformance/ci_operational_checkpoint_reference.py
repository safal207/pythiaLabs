from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCHEMA_PATH = ROOT / "schema" / "ci-operational-checkpoint-v0.1.schema.json"

CONTINUE = "CONTINUE"
REVALIDATE_WORKSPACE = "REVALIDATE_WORKSPACE"
RESTART_REQUIRED = "RESTART_REQUIRED"
IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"
REJECT_LINEAGE_MISMATCH = "REJECT_LINEAGE_MISMATCH"
REJECT_UNVERIFIED_COMPLETION = "REJECT_UNVERIFIED_COMPLETION"
REJECT_INVALID_AUTHORITY = "REJECT_INVALID_AUTHORITY"

MEMORY_ONLY_PREFIXES = ("memory://", "agent-memory://", "summary://")


def load_schema() -> dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    if not isinstance(schema, dict):
        raise ValueError("checkpoint schema root must be an object")
    Draft202012Validator.check_schema(schema)
    return schema


def _canonical_bytes(checkpoint: Mapping[str, Any]) -> bytes:
    value = copy.deepcopy(dict(checkpoint))
    value.pop("checkpoint_digest", None)
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def computed_digest(checkpoint: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(checkpoint)).hexdigest()


def with_computed_digest(checkpoint: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(checkpoint))
    result.setdefault(
        "checkpoint_digest",
        {
            "algorithm": "sha256",
            "canonicalization": "json-sort-keys-utf8-v1",
            "value": "0" * 64,
        },
    )
    result["checkpoint_digest"]["value"] = computed_digest(result)
    return result


def _schema_errors(checkpoint: Mapping[str, Any]) -> list[Any]:
    validator = Draft202012Validator(
        load_schema(),
        format_checker=FormatChecker(),
    )
    return sorted(
        validator.iter_errors(dict(checkpoint)),
        key=lambda error: [str(part) for part in error.absolute_path],
    )


def _result(outcome: str, reason_code: str, detail: str) -> dict[str, str]:
    return {
        "outcome": outcome,
        "reason_code": reason_code,
        "detail": detail,
    }


def _verification_index(rows: Iterable[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    return {str(row["verification_id"]): row for row in rows}


def _rejected_index(rows: Iterable[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    return {str(row["approach_id"]): row for row in rows}


def _duplicate_ids(rows: Iterable[Mapping[str, Any]], field: str) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        value = str(row[field])
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def _previous_checkpoint_integrity_error(
    previous_checkpoint: Mapping[str, Any],
) -> tuple[str, str] | None:
    errors = _schema_errors(previous_checkpoint)
    if errors:
        first = errors[0]
        path = "/".join(str(part) for part in first.absolute_path) or "<root>"
        return (
            "PREVIOUS_CHECKPOINT_SCHEMA_INVALID",
            f"{path}: {first.message}",
        )

    expected_digest = previous_checkpoint["checkpoint_digest"]["value"]
    actual_digest = computed_digest(previous_checkpoint)
    if expected_digest != actual_digest:
        return (
            "PREVIOUS_CHECKPOINT_DIGEST_MISMATCH",
            f"expected {expected_digest}, computed {actual_digest}",
        )

    duplicate_approaches = _duplicate_ids(
        previous_checkpoint["rejected_approaches"],
        "approach_id",
    )
    if duplicate_approaches:
        return (
            "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
            "duplicate rejected approach IDs: " + ", ".join(duplicate_approaches),
        )

    previous_verification = previous_checkpoint["verification"]
    previous_completed = previous_verification["completed"]
    previous_pending = previous_verification["pending"]
    verification_ids = [
        row["verification_id"] for row in previous_completed + previous_pending
    ]
    if len(verification_ids) != len(set(verification_ids)):
        return (
            "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
            "verification IDs are duplicated across completed and pending lists",
        )
    if set(verification_ids) != set(previous_verification["required"]):
        return (
            "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
            "required verification IDs do not match completed and pending rows",
        )
    for row in previous_completed:
        if any(
            str(ref).casefold().startswith(MEMORY_ONLY_PREFIXES)
            for ref in row["evidence_refs"]
        ):
            return (
                "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
                f"{row['verification_id']} relies on memory-only evidence",
            )
    return None


def evaluate_resume(
    checkpoint: Mapping[str, Any],
    *,
    current_workspace: Mapping[str, Any],
    previous_checkpoint: Mapping[str, Any] | None = None,
    seen_checkpoint_ids: Iterable[str] = (),
    known_parent_ids: Iterable[str] = (),
) -> dict[str, str]:
    errors = _schema_errors(checkpoint)
    if errors:
        first = errors[0]
        path = "/".join(str(part) for part in first.absolute_path) or "<root>"
        if path == "authority":
            return _result(
                REJECT_INVALID_AUTHORITY,
                "AUTHORITY_NOT_CONTEXT_ONLY",
                first.message,
            )
        return _result(
            RESTART_REQUIRED,
            "SCHEMA_INVALID",
            f"{path}: {first.message}",
        )

    expected_digest = checkpoint["checkpoint_digest"]["value"]
    actual_digest = computed_digest(checkpoint)
    if expected_digest != actual_digest:
        return _result(
            RESTART_REQUIRED,
            "DIGEST_MISMATCH",
            f"expected {expected_digest}, computed {actual_digest}",
        )

    checkpoint_id = checkpoint["checkpoint_id"]
    if checkpoint_id in set(seen_checkpoint_ids):
        return _result(
            IDEMPOTENT_REPLAY,
            "CHECKPOINT_ALREADY_CONSUMED",
            f"checkpoint {checkpoint_id} was already consumed",
        )

    duplicate_approaches = _duplicate_ids(
        checkpoint["rejected_approaches"],
        "approach_id",
    )
    if duplicate_approaches:
        return _result(
            REJECT_LINEAGE_MISMATCH,
            "REJECTED_APPROACH_ID_DUPLICATED",
            "duplicate rejected approach IDs: " + ", ".join(duplicate_approaches),
        )

    sequence = checkpoint["sequence"]
    parent_checkpoint_id = checkpoint["parent_checkpoint_id"]
    if sequence == 0 and parent_checkpoint_id is not None:
        return _result(
            REJECT_LINEAGE_MISMATCH,
            "ROOT_HAS_PARENT",
            "sequence 0 checkpoint must not declare a parent",
        )
    if sequence > 0 and parent_checkpoint_id is None:
        return _result(
            REJECT_LINEAGE_MISMATCH,
            "PARENT_REQUIRED",
            "non-root checkpoint must declare parent_checkpoint_id",
        )

    if previous_checkpoint is None:
        if sequence > 0:
            if parent_checkpoint_id not in set(known_parent_ids):
                return _result(
                    REJECT_LINEAGE_MISMATCH,
                    "PARENT_NOT_FOUND",
                    f"parent checkpoint {parent_checkpoint_id} is not known",
                )
            return _result(
                REJECT_LINEAGE_MISMATCH,
                "PREVIOUS_CHECKPOINT_REQUIRED",
                "non-root resume requires the full previous checkpoint",
            )
    else:
        integrity_error = _previous_checkpoint_integrity_error(previous_checkpoint)
        if integrity_error is not None:
            reason_code, detail = integrity_error
            return _result(
                REJECT_LINEAGE_MISMATCH,
                reason_code,
                detail,
            )
        if checkpoint["trajectory_id"] != previous_checkpoint["trajectory_id"]:
            return _result(
                REJECT_LINEAGE_MISMATCH,
                "TRAJECTORY_CHANGED",
                "checkpoint trajectory differs from previous checkpoint",
            )
        if parent_checkpoint_id != previous_checkpoint["checkpoint_id"]:
            return _result(
                REJECT_LINEAGE_MISMATCH,
                "PARENT_MISMATCH",
                "parent_checkpoint_id does not reference the previous checkpoint",
            )
        if sequence != previous_checkpoint["sequence"] + 1:
            return _result(
                REJECT_LINEAGE_MISMATCH,
                "SEQUENCE_MISMATCH",
                "checkpoint sequence is not previous sequence + 1",
            )

        previous_rejected = _rejected_index(
            previous_checkpoint["rejected_approaches"]
        )
        current_rejected = _rejected_index(checkpoint["rejected_approaches"])
        missing_rejections = sorted(set(previous_rejected) - set(current_rejected))
        if missing_rejections:
            return _result(
                REJECT_LINEAGE_MISMATCH,
                "REJECTED_APPROACH_LOST",
                "rejected approaches disappeared: " + ", ".join(missing_rejections),
            )
        changed_rejections = sorted(
            approach_id
            for approach_id, previous_row in previous_rejected.items()
            if current_rejected[approach_id] != previous_row
        )
        if changed_rejections:
            return _result(
                REJECT_LINEAGE_MISMATCH,
                "REJECTED_APPROACH_CHANGED",
                "rejected approaches changed: " + ", ".join(changed_rejections),
            )

        previous_completed = _verification_index(
            previous_checkpoint["verification"]["completed"]
        )
        current_completed = _verification_index(
            checkpoint["verification"]["completed"]
        )
        lost_completed = sorted(set(previous_completed) - set(current_completed))
        if lost_completed:
            return _result(
                REJECT_UNVERIFIED_COMPLETION,
                "COMPLETED_VERIFICATION_LOST",
                "completed verification disappeared: " + ", ".join(lost_completed),
            )
        for verification_id, previous_row in previous_completed.items():
            current_row = current_completed[verification_id]
            previous_refs = set(previous_row["evidence_refs"])
            current_refs = set(current_row["evidence_refs"])
            if (
                current_row["target"] != previous_row["target"]
                or not previous_refs.issubset(current_refs)
            ):
                return _result(
                    REJECT_UNVERIFIED_COMPLETION,
                    "COMPLETED_VERIFICATION_CHANGED",
                    (
                        "completed verification target changed or prior evidence "
                        f"was removed: {verification_id}"
                    ),
                )

    required_ids = set(checkpoint["verification"]["required"])
    completed_rows = checkpoint["verification"]["completed"]
    pending_rows = checkpoint["verification"]["pending"]
    completed_ids = [row["verification_id"] for row in completed_rows]
    pending_ids = [row["verification_id"] for row in pending_rows]

    all_ids = completed_ids + pending_ids
    if len(all_ids) != len(set(all_ids)):
        return _result(
            REJECT_UNVERIFIED_COMPLETION,
            "VERIFICATION_ID_DUPLICATED",
            "verification IDs must be unique across completed and pending lists",
        )

    represented_ids = set(all_ids)
    if represented_ids != required_ids:
        missing = sorted(required_ids - represented_ids)
        unexpected = sorted(represented_ids - required_ids)
        return _result(
            REJECT_UNVERIFIED_COMPLETION,
            "VERIFICATION_SET_MISMATCH",
            f"missing={missing}; unexpected={unexpected}",
        )

    for row in completed_rows:
        refs = row["evidence_refs"]
        if not refs:
            return _result(
                REJECT_UNVERIFIED_COMPLETION,
                "COMPLETION_EVIDENCE_MISSING",
                f"{row['verification_id']} has no evidence references",
            )
        if any(str(ref).casefold().startswith(MEMORY_ONLY_PREFIXES) for ref in refs):
            return _result(
                REJECT_UNVERIFIED_COMPLETION,
                "MEMORY_IS_NOT_VERIFICATION",
                f"{row['verification_id']} relies on memory-only evidence",
            )

    next_action = checkpoint["next_action"]
    if (
        next_action["action_class"] in {"merge", "deploy"}
        and not next_action["requires_fresh_authority"]
    ):
        return _result(
            REJECT_INVALID_AUTHORITY,
            "FRESH_AUTHORITY_REQUIRED",
            "merge and deploy actions require a fresh action authorization",
        )

    expected_workspace = checkpoint["workspace_state"]
    identity_fields = ("repository", "working_directory")
    for field in identity_fields:
        if field not in current_workspace:
            return _result(
                RESTART_REQUIRED,
                "CURRENT_WORKSPACE_FIELD_MISSING",
                f"current workspace did not report {field}",
            )
        if current_workspace[field] != expected_workspace[field]:
            return _result(
                RESTART_REQUIRED,
                "WORKSPACE_IDENTITY_MISMATCH",
                f"{field} differs from the checkpoint",
            )

    state_fields = ["base_ref", "head_sha"]
    if "dirty_state_digest" in expected_workspace:
        state_fields.append("dirty_state_digest")

    missing_state_fields = [
        field for field in state_fields if field not in current_workspace
    ]
    if missing_state_fields:
        return _result(
            REVALIDATE_WORKSPACE,
            "CURRENT_WORKSPACE_FIELD_MISSING",
            "current workspace did not report: " + ", ".join(missing_state_fields),
        )

    changed_fields = [
        field
        for field in state_fields
        if current_workspace[field] != expected_workspace[field]
    ]
    if changed_fields:
        return _result(
            REVALIDATE_WORKSPACE,
            "WORKSPACE_STATE_CHANGED",
            "changed workspace fields: " + ", ".join(changed_fields),
        )

    return _result(
        CONTINUE,
        "CONTINUE_OK",
        "checkpoint is valid, workspace matches, and authority remains context-only",
    )
