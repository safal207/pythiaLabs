from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "envelope_id",
    "created_at",
    "transition_reason",
    "project",
    "active_objective",
    "authority_model",
    "operational_tail",
    "artifact_refs",
    "rejected_approaches",
    "pending_verification",
    "next_action",
    "restore_requirements",
    "envelope_digest",
}

EXECUTION_EVENT_TYPES = {
    "tool_call",
    "tool_result",
    "artifact_modified",
    "verification_result",
}


def load_envelope(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Envelope root must be an object")
    return value


def canonical_bytes(envelope: Mapping[str, Any]) -> bytes:
    payload = copy.deepcopy(dict(envelope))
    payload.pop("envelope_digest", None)
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def compute_digest(envelope: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(envelope)).hexdigest()


def verify_digest(envelope: Mapping[str, Any]) -> bool:
    metadata = envelope.get("envelope_digest")
    if not isinstance(metadata, Mapping):
        return False
    return (
        metadata.get("algorithm") == "sha256"
        and metadata.get("canonicalization") == "json-sort-keys-utf8-v1"
        and metadata.get("value") == compute_digest(envelope)
    )


def semantic_errors(envelope: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TOP_LEVEL - set(envelope))
    if missing:
        errors.append("missing top-level fields: " + ", ".join(missing))

    authority_model = envelope.get("authority_model")
    if not isinstance(authority_model, Mapping):
        errors.append("authority_model must be an object")
    else:
        precedence = authority_model.get("precedence")
        if not isinstance(precedence, list) or not precedence or precedence[-1] != "memory":
            errors.append("memory must be the lowest-precedence authority source")
        if authority_model.get("memory_default") != "non_authoritative_memory":
            errors.append("memory_default must be non_authoritative_memory")

    events = envelope.get("operational_tail")
    if not isinstance(events, list) or not events:
        errors.append("operational_tail must contain at least one event")
        events = []

    artifact_rows = envelope.get("artifact_refs")
    if not isinstance(artifact_rows, list):
        errors.append("artifact_refs must be an array")
        artifact_rows = []
    artifacts = {
        row.get("artifact_id"): row
        for row in artifact_rows
        if isinstance(row, Mapping) and row.get("artifact_id")
    }

    active_constraints = 0
    for event in events:
        if not isinstance(event, Mapping):
            errors.append("operational_tail entries must be objects")
            continue
        authority = event.get("authority_class")
        source_type = (event.get("provenance") or {}).get("source_type")
        if authority == "constraint":
            active_constraints += 1
        if source_type == "memory" and authority in {"instruction", "constraint"}:
            errors.append(
                f"{event.get('event_id', '<unknown>')}: memory cannot restore instruction or constraint authority"
            )
        if event.get("event_type") in EXECUTION_EVENT_TYPES:
            refs = event.get("evidence_refs")
            if not isinstance(refs, list) or not refs:
                errors.append(
                    f"{event.get('event_id', '<unknown>')}: execution event requires evidence refs"
                )
                continue
            for ref in refs:
                artifact = artifacts.get(ref)
                if artifact is None:
                    errors.append(
                        f"{event.get('event_id', '<unknown>')}: missing artifact ref {ref}"
                    )
                elif artifact.get("verification_status") != "verified":
                    errors.append(
                        f"{event.get('event_id', '<unknown>')}: artifact {ref} is not verified"
                    )

    if active_constraints == 0:
        errors.append("at least one active constraint must survive restoration")

    rejected = envelope.get("rejected_approaches")
    if not isinstance(rejected, list):
        errors.append("rejected_approaches must be an array")
    else:
        for item in rejected:
            if not isinstance(item, Mapping) or item.get("status") != "rejected":
                errors.append("rejected approaches must remain explicitly rejected")

    pending = envelope.get("pending_verification")
    if not isinstance(pending, list):
        errors.append("pending_verification must be an array")
    else:
        for item in pending:
            if isinstance(item, Mapping) and item.get("status") == "passed":
                errors.append("pending verification cannot be silently promoted to passed")

    requirements = envelope.get("restore_requirements")
    if not isinstance(requirements, Mapping) or requirements.get("fail_closed") is not True:
        errors.append("restore gate must fail closed")

    return errors


def restore_decision(envelope: Mapping[str, Any]) -> str:
    if not verify_digest(envelope):
        return "BLOCKED"
    if semantic_errors(envelope):
        return "BLOCKED"
    pending = envelope.get("pending_verification", [])
    if any(
        isinstance(item, Mapping)
        and item.get("status") in {"pending", "running", "blocked", "failed"}
        for item in pending
    ):
        return "REVIEW_REQUIRED"
    return "RESUMABLE"
