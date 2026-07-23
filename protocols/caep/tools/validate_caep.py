#!/usr/bin/env python3
"""Validate Causal Action Episode Packet (CAEP) v0.1 bundles.

Stdlib-only. Checks structure plus cross-record invariants. It does not verify
production cryptographic signatures.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.1.0"
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
LEVELS = {"F0", "F1", "F2", "F3", "F4", "F5"}
DECISIONS = {"ALLOW", "DENY", "REQUIRE_APPROVAL", "REVISE"}
REVERSIBILITY = {"READ_ONLY", "REVERSIBLE", "EXTERNAL_REVERSIBLE", "IRREVERSIBLE"}
TYPES = {"intent", "authorization", "dispatch", "outcome", "recovery", "supersession"}
COMMON = {"record_type", "record_id", "episode_ref", "sequence", "observed_at", "issuer"}
REQUIRED = {
    "intent": {"actor_id", "agent_runtime_id", "action_type", "target_resource", "params_hash", "boundary_id", "requested_capabilities", "valid_time", "transaction_time", "pre_state_digest"},
    "authorization": {"decision", "policy_version", "authorized_target_resource", "authorized_params_hash", "authorized_boundary_id", "authorized_network_destinations", "credential_class", "expiry", "single_use_nonce", "reversibility_class"},
    "dispatch": {"tool_identity", "actual_target_resource", "network_destination", "actual_params_hash", "actual_boundary_id", "credential_class", "execution_environment_id", "dispatch_time"},
    "outcome": {"status", "policy_conformance", "response_hash", "changed_resources", "contacted_resources", "post_state_digest", "execution_duration_ms", "containment_required", "causal_parent_record_ids"},
    "recovery": {"containment_actions", "recovery_objective", "recovery_status", "objective_met", "recovered_state_digest", "residual_effects", "unresolved_dependencies", "causal_parent_record_ids"},
    "supersession": {"supersedes_record_id", "correction_reason", "new_evidence_refs", "transaction_time"},
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_ref(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()


def intent_binding(intent: dict[str, Any]) -> dict[str, Any]:
    keys = ("actor_id", "agent_runtime_id", "action_type", "target_resource", "params_hash", "boundary_id", "requested_capabilities", "valid_time", "transaction_time")
    return {key: intent.get(key) for key in keys}


def expected_episode_ref(intent: dict[str, Any]) -> str:
    return sha256_ref(intent_binding(intent))


def parse_time(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str):
        errors.append(f"{label} must be an RFC3339 string")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} is not valid RFC3339")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{label} must include a timezone")
        return None
    return parsed.astimezone(timezone.utc)


def check_hash(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not HASH_RE.fullmatch(value):
        errors.append(f"{label} must match sha256:<64 lowercase hex characters>")


def one(records: list[dict[str, Any]], kind: str, errors: list[str], required: bool = True):
    found = [record for record in records if record.get("record_type") == kind]
    if required and len(found) != 1:
        errors.append(f"packet must contain exactly one {kind} record; found {len(found)}")
    elif not required and len(found) > 1:
        errors.append(f"packet supports at most one {kind} record; found {len(found)}")
    return found[0] if len(found) == 1 else None


def validate_packet(packet: Any) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(packet, dict):
        return ["packet must be a JSON object"], warnings

    for field in ("caep_version", "episode_ref", "evidence_level", "records"):
        if field not in packet:
            errors.append(f"missing top-level field: {field}")
    if packet.get("caep_version") != VERSION:
        errors.append(f"caep_version must be {VERSION}")
    check_hash(packet.get("episode_ref"), "episode_ref", errors)
    if packet.get("evidence_level") not in LEVELS:
        errors.append(f"evidence_level must be one of {sorted(LEVELS)}")

    raw_records = packet.get("records")
    if not isinstance(raw_records, list) or not raw_records:
        return errors + ["records must be a non-empty array"], warnings

    records: list[dict[str, Any]] = []
    ids: dict[str, dict[str, Any]] = {}
    sequences: list[int] = []
    episode_ref = packet.get("episode_ref")

    for index, record in enumerate(raw_records):
        label = f"records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        records.append(record)
        kind = record.get("record_type")
        if kind not in TYPES:
            errors.append(f"{label}.record_type must be one of {sorted(TYPES)}")
            continue
        missing = sorted((COMMON | REQUIRED[kind]) - record.keys())
        if missing:
            errors.append(f"{label} missing fields: {', '.join(missing)}")

        record_id = record.get("record_id")
        if not isinstance(record_id, str) or not record_id:
            errors.append(f"{label}.record_id must be a non-empty string")
        elif record_id in ids:
            errors.append(f"duplicate record_id: {record_id}")
        else:
            ids[record_id] = record

        seq = record.get("sequence")
        if not isinstance(seq, int) or isinstance(seq, bool) or seq < 1:
            errors.append(f"{label}.sequence must be an integer >= 1")
        else:
            sequences.append(seq)
        if record.get("episode_ref") != episode_ref:
            errors.append(f"{label}.episode_ref does not match packet episode_ref")
        parse_time(record.get("observed_at"), f"{label}.observed_at", errors)

        for field in {
            "intent": ("params_hash", "pre_state_digest"),
            "authorization": ("authorized_params_hash",),
            "dispatch": ("actual_params_hash",),
            "outcome": ("response_hash", "post_state_digest"),
            "recovery": ("recovered_state_digest",),
        }.get(kind, ()):
            check_hash(record.get(field), f"{label}.{field}", errors)

        if kind == "authorization":
            if record.get("decision") not in DECISIONS:
                errors.append(f"{label}.decision must be one of {sorted(DECISIONS)}")
            if record.get("reversibility_class") not in REVERSIBILITY:
                errors.append(f"{label}.reversibility_class must be one of {sorted(REVERSIBILITY)}")
            destinations = record.get("authorized_network_destinations")
            if not isinstance(destinations, list) or not all(isinstance(v, str) and v for v in destinations):
                errors.append(f"{label}.authorized_network_destinations must be non-empty strings")
            parse_time(record.get("expiry"), f"{label}.expiry", errors)
        if kind == "dispatch":
            parse_time(record.get("dispatch_time"), f"{label}.dispatch_time", errors)

    if sequences:
        if sequences != sorted(sequences):
            errors.append("records must be ordered by ascending sequence")
        if len(sequences) != len(set(sequences)):
            errors.append("record sequences must be unique")
        if sorted(sequences) != list(range(1, len(sequences) + 1)):
            errors.append("record sequences must be contiguous starting at 1")

    intent = one(records, "intent", errors)
    auth = one(records, "authorization", errors)
    dispatch = one(records, "dispatch", errors, required=False)
    outcome = one(records, "outcome", errors, required=False)
    recovery = one(records, "recovery", errors, required=False)
    supersessions = [r for r in records if r.get("record_type") == "supersession"]

    if intent:
        computed = expected_episode_ref(intent)
        if computed != episode_ref:
            errors.append(f"episode_ref does not match canonical intent binding: expected {computed}")

    if intent and auth:
        for left, right in (("target_resource", "authorized_target_resource"), ("params_hash", "authorized_params_hash"), ("boundary_id", "authorized_boundary_id")):
            if intent.get(left) != auth.get(right):
                errors.append(f"authorization {right} does not match intent {left}")
        decision = auth.get("decision")
        if decision in {"DENY", "REVISE"} and dispatch:
            errors.append(f"decision {decision} must not have a dispatch record")
        if decision == "ALLOW" and not dispatch:
            errors.append("ALLOW must have exactly one dispatch record; found 0")
        if decision == "REQUIRE_APPROVAL":
            if not auth.get("human_approval_ref"):
                errors.append("REQUIRE_APPROVAL must bind human_approval_ref")
            if not dispatch:
                errors.append("REQUIRE_APPROVAL with approval evidence requires dispatch")

    if dispatch and not outcome:
        errors.append("every dispatch must have exactly one terminal outcome; found 0")
    if outcome and not dispatch:
        errors.append("outcome record exists without a dispatch record")

    if auth and dispatch:
        for left, right in (("actual_target_resource", "authorized_target_resource"), ("actual_params_hash", "authorized_params_hash"), ("actual_boundary_id", "authorized_boundary_id"), ("credential_class", "credential_class")):
            if dispatch.get(left) != auth.get(right):
                errors.append(f"dispatch {left} does not match authorization {right}")
        if dispatch.get("network_destination") not in auth.get("authorized_network_destinations", []):
            errors.append("dispatch network_destination is outside authorized_network_destinations")
        dispatch_time = parse_time(dispatch.get("dispatch_time"), "dispatch.dispatch_time", errors)
        expiry = parse_time(auth.get("expiry"), "authorization.expiry", errors)
        if dispatch_time and expiry and dispatch_time > expiry:
            errors.append("dispatch occurred after authorization expiry")

    if dispatch and outcome:
        if dispatch.get("record_id") not in outcome.get("causal_parent_record_ids", []):
            errors.append("outcome must causally reference the dispatch record")
        containment_needed = bool(outcome.get("containment_required")) or outcome.get("policy_conformance") == "DRIFT_DETECTED"
        if containment_needed and not recovery:
            errors.append("drift/containment-required outcome must have exactly one recovery record; found 0")

    if recovery:
        if not outcome:
            errors.append("recovery record exists without an outcome record")
        elif outcome.get("record_id") not in recovery.get("causal_parent_record_ids", []):
            errors.append("recovery must causally reference the outcome record")
        status = recovery.get("recovery_status")
        objective_met = recovery.get("objective_met")
        residuals = recovery.get("residual_effects")
        unresolved = recovery.get("unresolved_dependencies")
        if status == "RECOVERED":
            if objective_met is not True:
                errors.append("RECOVERED requires objective_met=true")
            if residuals or unresolved:
                errors.append("RECOVERED requires empty residual_effects and unresolved_dependencies")
        elif status == "RECOVERED_WITH_RESIDUALS":
            if objective_met is not True:
                errors.append("RECOVERED_WITH_RESIDUALS requires objective_met=true")
            if not isinstance(residuals, list) or not residuals:
                errors.append("RECOVERED_WITH_RESIDUALS requires non-empty residual_effects")
        elif status == "FAILED":
            if objective_met is not False:
                errors.append("FAILED recovery requires objective_met=false")
        else:
            errors.append("recovery_status must be RECOVERED, RECOVERED_WITH_RESIDUALS, or FAILED")

    sequence_by_id = {r.get("record_id"): r.get("sequence") for r in records}
    for record in records:
        parents = record.get("causal_parent_record_ids", [])
        if not isinstance(parents, list):
            errors.append(f"record {record.get('record_id')!r} causal_parent_record_ids must be an array")
            continue
        for parent in parents:
            if parent not in ids:
                errors.append(f"record {record.get('record_id')!r} references unknown causal parent {parent!r}")
            elif sequence_by_id[parent] >= record.get("sequence", -1):
                errors.append(f"causal parent {parent!r} must precede child {record.get('record_id')!r}")

    for record in supersessions:
        target = record.get("supersedes_record_id")
        if target not in ids:
            errors.append(f"supersession references unknown record {target!r}")
        elif sequence_by_id[target] >= record.get("sequence", -1):
            errors.append("supersession must occur after the superseded record")

    level = packet.get("evidence_level")
    action_records = [r for r in records if r.get("record_type") in {"authorization", "dispatch", "outcome", "recovery"}]
    if level in {"F3", "F4", "F5"}:
        missing = [r.get("record_id") for r in action_records if not isinstance(r.get("integrity_proof"), dict)]
        if missing:
            errors.append(f"{level} requires integrity_proof on action records: {missing}")
    elif action_records and not all(isinstance(r.get("integrity_proof"), dict) for r in action_records):
        warnings.append("packet is below F3: not all authorization/dispatch/outcome/recovery records carry independent integrity proofs")
    if level in {"F4", "F5"} and not packet.get("replay_evidence"):
        errors.append(f"{level} requires replay_evidence")
    if level == "F5" and not packet.get("external_verification"):
        errors.append("F5 requires external_verification")

    return errors, warnings


def load_packet(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args(argv)
    try:
        packet = load_packet(args.packet)
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)], "warnings": []}, indent=2) if args.json_output else f"INVALID: {exc}")
        return 2
    errors, warnings = validate_packet(packet)
    result = {"valid": not errors, "episode_ref": packet.get("episode_ref"), "errors": errors, "warnings": warnings}
    if args.json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("VALID" if not errors else "INVALID")
        for warning in warnings:
            print(f"warning: {warning}")
        for error in errors:
            print(f"error: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
