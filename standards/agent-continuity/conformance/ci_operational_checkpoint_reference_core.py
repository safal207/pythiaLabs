from __future__ import annotations

from typing import Any, Iterable, Mapping

import ci_operational_checkpoint_reference_impl as _impl
from ci_operational_checkpoint_reference_impl import *  # noqa: F401,F403

_result = _impl._result
_schema_errors = _impl._schema_errors
_ORIGINAL_PREVIOUS_CHECKPOINT_INTEGRITY_ERROR = (
    _impl._previous_checkpoint_integrity_error
)


def _previous_checkpoint_integrity_error(
    previous_checkpoint: Mapping[str, Any],
) -> tuple[str, str] | None:
    """Extend parent integrity after canonical schema and digest validation."""

    error = _ORIGINAL_PREVIOUS_CHECKPOINT_INTEGRITY_ERROR(previous_checkpoint)
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

    for row in previous_checkpoint["verification"]["completed"]:
        if not row["evidence_refs"]:
            return (
                "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
                f"{row['verification_id']} has no evidence references",
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


# Install the enhanced parent hook into the canonical ordered implementation.
_impl._previous_checkpoint_integrity_error = _previous_checkpoint_integrity_error


def evaluate_resume(
    checkpoint: Mapping[str, Any],
    *,
    current_workspace: Mapping[str, Any],
    previous_checkpoint: Mapping[str, Any] | None = None,
    seen_checkpoint_ids: Iterable[str] = (),
    known_parent_ids: Iterable[str] = (),
) -> dict[str, str]:
    """Preserve canonical validation order and stable authority diagnostics."""

    errors = _schema_errors(checkpoint)
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

    result = _impl.evaluate_resume(
        checkpoint,
        current_workspace=current_workspace,
        previous_checkpoint=previous_checkpoint,
        seen_checkpoint_ids=seen_checkpoint_ids,
        known_parent_ids=known_parent_ids,
    )

    if result["outcome"] == CONTINUE:
        sequence = checkpoint["sequence"]
        if (
            sequence > 0
            and checkpoint["checkpoint_id"] == checkpoint["parent_checkpoint_id"]
        ):
            return _result(
                REJECT_LINEAGE_MISMATCH,
                "CHECKPOINT_ID_REUSED",
                "a checkpoint cannot reuse its parent checkpoint ID",
            )
    return result
