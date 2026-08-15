from __future__ import annotations

from typing import Any, Mapping


def evaluate_transition(
    state: Mapping[str, Any],
    proposal: Mapping[str, Any],
) -> tuple[str, dict[str, Any]]:
    if proposal.get("lane_id") != state.get("lane_id"):
        return "BLOCKED_LANE_MISMATCH", {}
    if proposal.get("writer_ref") != state.get("owner_ref"):
        return "BLOCKED_WRITER_NOT_OWNER", {}
    if proposal.get("writer_ownership_epoch") != state.get("ownership_epoch"):
        return "BLOCKED_OWNERSHIP_EPOCH_MISMATCH", {}

    observed = proposal.get("observed_through_event_id")
    expected = proposal.get("expected_predecessor_id")
    current = state.get("head_event_id")

    if observed != expected:
        return "BLOCKED_UNREAD_PREDECESSOR", {
            "observed_through_event_id": observed,
            "expected_predecessor_id": expected,
        }
    if expected != current:
        return "BLOCKED_CAS_CONFLICT", {
            "expected_predecessor_id": expected,
            "current_head_event_id": current,
        }

    kind = proposal.get("transition_kind")
    if kind == "STATUS":
        return "STATUS_TRANSITION_ALLOWED", {
            "next_event_id": proposal.get("next_event_id"),
        }
    if kind == "HANDOFF":
        return "HANDOFF_REQUIRES_REACHABILITY", {}
    return "BLOCKED_UNKNOWN_TRANSITION_KIND", {}


def evaluate_handoff(
    state: Mapping[str, Any],
    proposal: Mapping[str, Any],
    reachability: Mapping[str, Any] | None,
    now_tick: int,
) -> tuple[str, dict[str, Any]]:
    base, detail = evaluate_transition(state, proposal)
    if base != "HANDOFF_REQUIRES_REACHABILITY":
        return base, detail

    target = proposal.get("target_owner_ref")
    target_epoch = proposal.get("target_ownership_epoch")
    if not target or target_epoch != state.get("ownership_epoch", -1) + 1:
        return "BLOCKED_INVALID_HANDOFF_EPOCH", {}

    if reachability is None:
        return "PENDING_REACHABILITY_UNCHECKED", {
            "target_owner_ref": target,
        }
    if reachability.get("participant_ref") != target:
        return "BLOCKED_REACHABILITY_PARTICIPANT_MISMATCH", {}
    if reachability.get("surface_ref") != proposal.get("reachability_surface_ref"):
        return "BLOCKED_REACHABILITY_NOT_SURFACED", {}

    observed_at = reachability.get("observed_at_tick")
    valid_until = reachability.get("valid_until_tick")
    if not isinstance(observed_at, int) or not isinstance(valid_until, int):
        return "BLOCKED_INVALID_REACHABILITY_SIGNAL", {}
    if observed_at > now_tick:
        return "BLOCKED_FUTURE_REACHABILITY_SIGNAL", {}
    if now_tick > valid_until:
        return "PENDING_UNREACHABLE", {
            "reason": "reachability_signal_expired",
        }
    if reachability.get("status") != "READY":
        return "PENDING_UNREACHABLE", {
            "reason": str(reachability.get("status", "unknown")).lower(),
        }

    return "HANDOFF_DELIVERABLE", {
        "target_owner_ref": target,
        "target_ownership_epoch": target_epoch,
        "reachability_signal_id": reachability.get("signal_id"),
    }


def evaluate_handoff_commit(
    state: Mapping[str, Any],
    proposal: Mapping[str, Any],
    reachability: Mapping[str, Any] | None,
    ack: Mapping[str, Any] | None,
    now_tick: int,
) -> tuple[str, dict[str, Any]]:
    status, detail = evaluate_handoff(state, proposal, reachability, now_tick)
    if status != "HANDOFF_DELIVERABLE":
        return status, detail

    if ack is None:
        return "PENDING_RECIPIENT_ACK", {}
    if ack.get("lane_id") != state.get("lane_id"):
        return "BLOCKED_ACK_LANE_MISMATCH", {}
    if ack.get("recipient_ref") != proposal.get("target_owner_ref"):
        return "BLOCKED_ACK_RECIPIENT_MISMATCH", {}
    if ack.get("accepted_handoff_event_id") != proposal.get("next_event_id"):
        return "BLOCKED_ACK_EVENT_MISMATCH", {}
    if ack.get("accepted_ownership_epoch") != proposal.get("target_ownership_epoch"):
        return "BLOCKED_ACK_EPOCH_MISMATCH", {}
    if ack.get("observed_predecessor_id") != state.get("head_event_id"):
        return "BLOCKED_ACK_STALE_PREDECESSOR", {}

    return "HANDOFF_COMMIT_ALLOWED", {
        "new_owner_ref": proposal.get("target_owner_ref"),
        "new_ownership_epoch": proposal.get("target_ownership_epoch"),
        "new_head_event_id": proposal.get("next_event_id"),
    }
