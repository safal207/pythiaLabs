from __future__ import annotations

from typing import Any, Iterable, Mapping


def _same_authority(a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
    return (
        a.get("authority_lane_id") == b.get("authority_lane_id")
        and a.get("authority_owner_ref") == b.get("authority_owner_ref")
        and a.get("authority_epoch") == b.get("authority_epoch")
        and a.get("root_execution_id") == b.get("root_execution_id")
    )


def evaluate_side_effect(
    state: Mapping[str, Any],
    execution: Mapping[str, Any],
    parent: Mapping[str, Any] | None = None,
) -> tuple[str, dict[str, Any]]:
    """Evaluate whether an execution still has authority for a side effect.

    The current lane state is assumed to come from the HRC ownership state.
    ORC intentionally treats process liveness as independent from admission.
    """

    if execution.get("authority_lane_id") != state.get("lane_id"):
        return "BLOCKED_LANE_MISMATCH", {}

    if parent is not None:
        if execution.get("parent_execution_id") != parent.get("execution_id"):
            return "BLOCKED_PARENT_EXECUTION_MISMATCH", {}
        if not _same_authority(execution, parent):
            return "BLOCKED_AUTHORITY_LINEAGE_ESCAPE", {
                "parent_execution_id": parent.get("execution_id"),
                "execution_id": execution.get("execution_id"),
            }

    bound_epoch = execution.get("authority_epoch")
    current_epoch = state.get("ownership_epoch")
    if bound_epoch != current_epoch:
        return "BLOCKED_REVOKED_AUTHORITY_EPOCH", {
            "bound_authority_epoch": bound_epoch,
            "current_ownership_epoch": current_epoch,
        }

    bound_owner = execution.get("authority_owner_ref")
    current_owner = state.get("owner_ref")
    if bound_owner != current_owner:
        return "BLOCKED_REVOKED_AUTHORITY_OWNER", {
            "bound_authority_owner_ref": bound_owner,
            "current_owner_ref": current_owner,
        }

    return "SIDE_EFFECT_ALLOWED", {
        "execution_id": execution.get("execution_id"),
        "authority_owner_ref": bound_owner,
        "authority_epoch": bound_epoch,
    }


def evaluate_revocation_quiescence(
    state: Mapping[str, Any],
    executions: Iterable[Mapping[str, Any]],
) -> tuple[str, dict[str, Any]]:
    """Report whether executions from superseded authority are observed stopped.

    KILL_REQUESTED and UNKNOWN remain non-quiescent. This function does not
    decide side-effect authority; evaluate_side_effect does that independently.
    """

    revoked: list[str] = []
    live: list[str] = []

    for execution in executions:
        if execution.get("authority_lane_id") != state.get("lane_id"):
            continue

        stale = (
            execution.get("authority_epoch") != state.get("ownership_epoch")
            or execution.get("authority_owner_ref") != state.get("owner_ref")
        )
        if not stale:
            continue

        execution_id = str(execution.get("execution_id"))
        revoked.append(execution_id)
        if execution.get("process_state") != "EXITED":
            live.append(execution_id)

    if live:
        return "REVOCATION_PENDING_LIVE_EXECUTIONS", {
            "revoked_execution_ids": revoked,
            "live_execution_ids": live,
        }

    return "REVOCATION_QUIESCENT", {
        "revoked_execution_ids": revoked,
        "live_execution_ids": [],
    }
