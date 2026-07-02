from __future__ import annotations

from functools import lru_cache
from typing import Any, Iterable, Mapping

import ci_operational_checkpoint_reference_impl as _impl
from ci_operational_checkpoint_reference_impl import *  # noqa: F401,F403

_result = _impl._result
_schema_errors = _impl._schema_errors
_ORIGINAL_LOAD_SCHEMA = _impl.load_schema


@lru_cache(maxsize=1)
def load_schema() -> dict[str, Any]:
    return _ORIGINAL_LOAD_SCHEMA()


_impl.load_schema = load_schema


def _previous_checkpoint_integrity_error(
    previous_checkpoint: Mapping[str, Any],
) -> tuple[str, str] | None:
    verification = previous_checkpoint.get("verification")
    if isinstance(verification, Mapping):
        completed = verification.get("completed")
        if isinstance(completed, list):
            for row in completed:
                if not isinstance(row, Mapping):
                    continue
                refs = row.get("evidence_refs")
                if isinstance(refs, list) and not refs:
                    return (
                        "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
                        f"{row.get('verification_id', '<unknown>')} has no evidence references",
                    )

    error = _impl._previous_checkpoint_integrity_error(previous_checkpoint)
    if error is not None:
        return error

    sequence = previous_checkpoint["sequence"]
    parent_id = previous_checkpoint["parent_checkpoint_id"]
    checkpoint_id = previous_checkpoint["checkpoint_id"]
    if sequence == 0 and parent_id is not None:
        return (
            "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
            "root previous checkpoint must not declare a parent",
        )
    if sequence > 0 and parent_id is None:
        return (
            "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
            "non-root previous checkpoint must declare a parent",
        )
    if parent_id is not None and checkpoint_id == parent_id:
        return (
            "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
            "previous checkpoint cannot be its own parent",
        )

    next_action = previous_checkpoint["next_action"]
    if (
        next_action["action_class"] in {"merge", "deploy"}
        and not next_action["requires_fresh_authority"]
    ):
        return (
            "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
            "parent merge or deploy intent requires fresh authority",
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
        authority_error = next(
            (
                error
                for error in errors
                if list(error.absolute_path) == ["authority"]
            ),
            None,
        )
        if authority_error is not None:
            return _result(
                REJECT_INVALID_AUTHORITY,
                "AUTHORITY_NOT_CONTEXT_ONLY",
                authority_error.message,
            )

    if previous_checkpoint is not None:
        error = _previous_checkpoint_integrity_error(previous_checkpoint)
        if error is not None:
            reason_code, detail = error
            return _result(
                REJECT_LINEAGE_MISMATCH,
                reason_code,
                detail,
            )

    return _impl.evaluate_resume(
        checkpoint,
        current_workspace=current_workspace,
        previous_checkpoint=previous_checkpoint,
        seen_checkpoint_ids=seen_checkpoint_ids,
        known_parent_ids=known_parent_ids,
    )
