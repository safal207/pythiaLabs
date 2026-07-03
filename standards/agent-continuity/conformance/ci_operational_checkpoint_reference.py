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
    """Delegate to the canonical core evaluator without pre-validation."""

    return _core.evaluate_resume(
        checkpoint,
        current_workspace=current_workspace,
        previous_checkpoint=previous_checkpoint,
        seen_checkpoint_ids=seen_checkpoint_ids,
        known_parent_ids=known_parent_ids,
    )
