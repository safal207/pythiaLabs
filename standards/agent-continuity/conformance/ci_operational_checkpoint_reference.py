from __future__ import annotations

from typing import Any, Iterable, Mapping

import ci_operational_checkpoint_reference_core as _core
from ci_operational_checkpoint_reference_core import *  # noqa: F401,F403


def evaluate_resume(
    checkpoint: Mapping[str, Any],
    *,
    current_workspace: Mapping[str, Any],
    previous_checkpoint: Mapping[str, Any] | None = None,
    seen_checkpoint_ids: Iterable[str] = (),
    known_parent_ids: Iterable[str] = (),
) -> dict[str, str]:
    """Apply link-level lineage guards before the core resume evaluator."""

    current_errors = _core._schema_errors(checkpoint)
    current_digest_valid = (
        not current_errors
        and checkpoint["checkpoint_digest"]["value"]
        == _core.computed_digest(checkpoint)
    )
    if current_digest_valid:
        sequence = checkpoint["sequence"]
        checkpoint_id = checkpoint["checkpoint_id"]
        parent_checkpoint_id = checkpoint["parent_checkpoint_id"]
        if sequence > 0 and checkpoint_id == parent_checkpoint_id:
            return _core._result(
                _core.REJECT_LINEAGE_MISMATCH,
                "CHECKPOINT_ID_REUSED",
                "a checkpoint cannot reuse its parent checkpoint ID",
            )

    if previous_checkpoint is not None:
        integrity_error = _core._previous_checkpoint_integrity_error(
            previous_checkpoint
        )
        if integrity_error is None:
            previous_sequence = previous_checkpoint["sequence"]
            previous_parent_id = previous_checkpoint["parent_checkpoint_id"]
            if previous_sequence == 0 and previous_parent_id is not None:
                return _core._result(
                    _core.REJECT_LINEAGE_MISMATCH,
                    "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
                    "root previous checkpoint must not declare a parent",
                )
            if previous_sequence > 0 and previous_parent_id is None:
                return _core._result(
                    _core.REJECT_LINEAGE_MISMATCH,
                    "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
                    "non-root previous checkpoint must declare a parent",
                )
            if (
                previous_parent_id is not None
                and previous_checkpoint["checkpoint_id"] == previous_parent_id
            ):
                return _core._result(
                    _core.REJECT_LINEAGE_MISMATCH,
                    "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
                    "previous checkpoint cannot be its own parent",
                )
            previous_action = previous_checkpoint["next_action"]
            if (
                previous_action["action_class"] in {"merge", "deploy"}
                and not previous_action["requires_fresh_authority"]
            ):
                return _core._result(
                    _core.REJECT_LINEAGE_MISMATCH,
                    "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
                    "parent merge or deploy intent requires fresh authority",
                )

    return _core.evaluate_resume(
        checkpoint,
        current_workspace=current_workspace,
        previous_checkpoint=previous_checkpoint,
        seen_checkpoint_ids=seen_checkpoint_ids,
        known_parent_ids=known_parent_ids,
    )
