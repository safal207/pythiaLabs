from __future__ import annotations

from typing import Any, Iterable, Mapping

import ci_operational_checkpoint_reference_core as _core
from ci_operational_checkpoint_reference_core import *  # noqa: F401,F403


def _is_memory_only_ref(value: Any) -> bool:
    return str(value).lstrip().casefold().startswith(MEMORY_ONLY_PREFIXES)


def _memory_only_verification_id(
    checkpoint: Mapping[str, Any] | None,
) -> str | None:
    if checkpoint is None:
        return None
    for row in checkpoint["verification"]["completed"]:
        if any(_is_memory_only_ref(ref) for ref in row["evidence_refs"]):
            return str(row["verification_id"])
    return None


def evaluate_resume(
    checkpoint: Mapping[str, Any],
    *,
    current_workspace: Mapping[str, Any],
    previous_checkpoint: Mapping[str, Any] | None = None,
    seen_checkpoint_ids: Iterable[str] = (),
    known_parent_ids: Iterable[str] = (),
) -> dict[str, str]:
    """Delegate first, then fail closed on normalized memory-only evidence."""

    result = _core.evaluate_resume(
        checkpoint,
        current_workspace=current_workspace,
        previous_checkpoint=previous_checkpoint,
        seen_checkpoint_ids=seen_checkpoint_ids,
        known_parent_ids=known_parent_ids,
    )
    if result["outcome"] != CONTINUE:
        return result

    parent_verification_id = _memory_only_verification_id(previous_checkpoint)
    if parent_verification_id is not None:
        return _core._result(
            REJECT_LINEAGE_MISMATCH,
            "PREVIOUS_CHECKPOINT_SEMANTIC_INVALID",
            f"{parent_verification_id} relies on memory-only evidence",
        )

    verification_id = _memory_only_verification_id(checkpoint)
    if verification_id is not None:
        return _core._result(
            REJECT_UNVERIFIED_COMPLETION,
            "MEMORY_IS_NOT_VERIFICATION",
            f"{verification_id} relies on memory-only evidence",
        )
    return result
