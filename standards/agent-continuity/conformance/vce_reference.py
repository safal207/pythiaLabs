from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ENVELOPE_SCHEMA_PATH = ROOT / "schema" / "continuation-envelope.schema.json"
RESTORE_RESULTS_SCHEMA_PATH = ROOT / "schema" / "restore-results.schema.json"

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

DURABLE_EVIDENCE_METHODS = {"digest", "receipt"}
DEFAULT_AUTHORITATIVE_SOURCES = {"user_message", "project_policy"}


def load_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} root must be an object")
    return value


def load_envelope(path: Path) -> dict[str, Any]:
    return load_json_object(path)


def load_schema(path: Path) -> dict[str, Any]:
    schema = load_json_object(path)
    Draft202012Validator.check_schema(schema)
    return schema


def schema_errors(
    document: Mapping[str, Any],
    schema_path: Path,
) -> list[str]:
    validator = Draft202012Validator(
        load_schema(schema_path),
        format_checker=FormatChecker(),
    )
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in sorted(
            validator.iter_errors(dict(document)),
            key=lambda item: [str(part) for part in item.absolute_path],
        )
    ]


def canonical_bytes(envelope: Mapping[str, Any]) -> bytes:
    payload = {
        key: value
        for key, value in envelope.items()
        if key != "envelope_digest"
    }
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
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


def _artifact_index(
    artifact_rows: Any,
    errors: list[str],
) -> dict[str, Mapping[str, Any]]:
    if not isinstance(artifact_rows, list):
        errors.append("artifact_refs must be an array")
        return {}

    artifacts: dict[str, Mapping[str, Any]] = {}
    for row in artifact_rows:
        if not isinstance(row, Mapping):
            errors.append("artifact_refs entries must be objects")
            continue
        artifact_id = row.get("artifact_id")
        if not isinstance(artifact_id, str) or not artifact_id:
            errors.append("artifact_refs entries require artifact_id")
            continue
        if artifact_id in artifacts:
            errors.append(f"duplicate artifact_id: {artifact_id}")
            continue
        artifacts[artifact_id] = row
    return artifacts


def _execution_artifact_ids(envelope: Mapping[str, Any]) -> set[str]:
    artifact_ids: set[str] = set()
    events = envelope.get("operational_tail")
    if not isinstance(events, list):
        return artifact_ids

    for event in events:
        if not isinstance(event, Mapping):
            continue
        if event.get("event_type") not in EXECUTION_EVENT_TYPES:
            continue
        refs = event.get("evidence_refs")
        if not isinstance(refs, list):
            continue
        artifact_ids.update(ref for ref in refs if isinstance(ref, str))
    return artifact_ids


def semantic_errors(envelope: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TOP_LEVEL - set(envelope))
    if missing:
        errors.append("missing top-level fields: " + ", ".join(missing))

    authority_model = envelope.get("authority_model")
    authoritative_sources = DEFAULT_AUTHORITATIVE_SOURCES
    if not isinstance(authority_model, Mapping):
        errors.append("authority_model must be an object")
    else:
        precedence = authority_model.get("precedence")
        if precedence != ["system", "developer", "user", "project_policy", "memory"]:
            errors.append(
                "authority precedence must be system > developer > user > "
                "project_policy > memory"
            )
        if authority_model.get("memory_default") != "non_authoritative_memory":
            errors.append("memory_default must be non_authoritative_memory")
        declared_sources = authority_model.get("authoritative_sources")
        if not isinstance(declared_sources, list):
            errors.append("authoritative_sources must be an array")
        else:
            authoritative_sources = set(declared_sources)
            if not authoritative_sources:
                errors.append("authoritative_sources cannot be empty")
            if not authoritative_sources <= DEFAULT_AUTHORITATIVE_SOURCES:
                errors.append(
                    "authoritative_sources contains a source not allowed by RFC-001"
                )

    events = envelope.get("operational_tail")
    if not isinstance(events, list) or not events:
        errors.append("operational_tail must contain at least one event")
        events = []

    artifacts = _artifact_index(envelope.get("artifact_refs"), errors)

    requirements = envelope.get("restore_requirements")
    required_checks: list[Mapping[str, Any]] = []
    if not isinstance(requirements, Mapping):
        errors.append("restore_requirements must be an object")
    else:
        if requirements.get("fail_closed") is not True:
            errors.append("restore gate must fail closed")
        checks = requirements.get("required_evidence_checks")
        if not isinstance(checks, list):
            errors.append("required_evidence_checks must be an array")
        else:
            required_checks = [
                item for item in checks if isinstance(item, Mapping)
            ]

    checks_by_artifact: dict[str, list[Mapping[str, Any]]] = {}
    seen_check_ids: set[str] = set()
    for check in required_checks:
        check_id = check.get("check_id")
        if not isinstance(check_id, str) or not check_id:
            errors.append("evidence checks require check_id")
            continue
        if check_id in seen_check_ids:
            errors.append(f"duplicate evidence check id: {check_id}")
        seen_check_ids.add(check_id)

        artifact_id = check.get("artifact_id")
        artifact = artifacts.get(artifact_id)
        if artifact is None:
            errors.append(f"{check_id}: unknown artifact {artifact_id}")
            continue
        checks_by_artifact.setdefault(str(artifact_id), []).append(check)

        method = check.get("method")
        if method == "digest" and not artifact.get("digest"):
            errors.append(f"{check_id}: digest check requires artifact digest")
        if method == "receipt" and not artifact.get("receipt_ref"):
            errors.append(f"{check_id}: receipt check requires artifact receipt_ref")

    active_constraints = 0
    for event in events:
        if not isinstance(event, Mapping):
            errors.append("operational_tail entries must be objects")
            continue

        event_id = event.get("event_id", "<unknown>")
        authority = event.get("authority_class")
        provenance = event.get("provenance")
        source_type = (
            provenance.get("source_type")
            if isinstance(provenance, Mapping)
            else None
        )

        if authority in {"instruction", "constraint"}:
            if source_type not in authoritative_sources:
                errors.append(
                    f"{event_id}: {source_type} cannot restore instruction or "
                    "constraint authority"
                )
            elif authority == "constraint":
                active_constraints += 1

        if event.get("event_type") in EXECUTION_EVENT_TYPES:
            refs = event.get("evidence_refs")
            if not isinstance(refs, list) or not refs:
                errors.append(f"{event_id}: execution event requires evidence refs")
                continue

            for ref in refs:
                artifact = artifacts.get(ref)
                if artifact is None:
                    errors.append(f"{event_id}: missing artifact ref {ref}")
                    continue
                if not artifact.get("digest") and not artifact.get("receipt_ref"):
                    errors.append(
                        f"{event_id}: artifact {ref} lacks a durable anchor"
                    )

                checks = checks_by_artifact.get(str(ref), [])
                if not checks:
                    errors.append(
                        f"{event_id}: artifact {ref} has no required evidence check"
                    )
                elif not any(
                    check.get("method") in DURABLE_EVIDENCE_METHODS
                    for check in checks
                ):
                    errors.append(
                        f"{event_id}: artifact {ref} requires digest or receipt "
                        "evidence check"
                    )

    if active_constraints == 0:
        errors.append(
            "at least one authoritative active constraint must survive restoration"
        )

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

    return errors


def _restore_gate_state(
    envelope: Mapping[str, Any],
    restore_results: Mapping[str, Any] | None,
) -> str:
    if restore_results is None:
        return "BLOCKED"
    if schema_errors(restore_results, RESTORE_RESULTS_SCHEMA_PATH):
        return "BLOCKED"
    if restore_results.get("envelope_id") != envelope.get("envelope_id"):
        return "BLOCKED"

    requirements = envelope.get("restore_requirements")
    if not isinstance(requirements, Mapping):
        return "BLOCKED"

    completed_reads = restore_results.get("completed_reads")
    required_reads = requirements.get("required_reads")
    if not isinstance(completed_reads, list) or not isinstance(required_reads, list):
        return "BLOCKED"
    if not set(required_reads) <= set(completed_reads):
        return "BLOCKED"

    artifact_errors: list[str] = []
    artifacts = _artifact_index(envelope.get("artifact_refs"), artifact_errors)
    if artifact_errors:
        return "BLOCKED"

    result_rows = restore_results.get("evidence_checks")
    if not isinstance(result_rows, list):
        return "BLOCKED"

    result_by_id: dict[str, Mapping[str, Any]] = {}
    for result in result_rows:
        if not isinstance(result, Mapping):
            return "BLOCKED"
        check_id = result.get("check_id")
        if not isinstance(check_id, str) or check_id in result_by_id:
            return "BLOCKED"
        result_by_id[check_id] = result

    requirements_rows = requirements.get("required_evidence_checks")
    if not isinstance(requirements_rows, list):
        return "BLOCKED"

    execution_artifact_ids = _execution_artifact_ids(envelope)
    has_pending = False

    for requirement in requirements_rows:
        if not isinstance(requirement, Mapping):
            return "BLOCKED"

        check_id = requirement.get("check_id")
        result = result_by_id.get(check_id)
        if result is None:
            return "BLOCKED"
        if (
            result.get("artifact_id") != requirement.get("artifact_id")
            or result.get("method") != requirement.get("method")
        ):
            return "BLOCKED"

        status = result.get("status")
        if status == "pending":
            has_pending = True
            continue
        if status != "passed":
            return "BLOCKED"

        artifact_id = requirement.get("artifact_id")
        artifact = artifacts.get(artifact_id)
        if artifact is None:
            return "BLOCKED"

        method = requirement.get("method")
        if method == "digest":
            expected = artifact.get("digest")
            observed = result.get("observed_digest")
            if not expected or observed != expected:
                return "BLOCKED"
        elif method == "receipt":
            expected = artifact.get("receipt_ref")
            observed = result.get("receipt_ref")
            if not expected or observed != expected:
                return "BLOCKED"
        elif method == "existence":
            if artifact_id in execution_artifact_ids:
                return "BLOCKED"
        else:
            return "BLOCKED"

    return "REVIEW_REQUIRED" if has_pending else "PASSED"


def restore_decision(
    envelope: Mapping[str, Any],
    restore_results: Mapping[str, Any] | None = None,
) -> str:
    if schema_errors(envelope, ENVELOPE_SCHEMA_PATH):
        return "BLOCKED"
    if not verify_digest(envelope):
        return "BLOCKED"
    if semantic_errors(envelope):
        return "BLOCKED"

    gate_state = _restore_gate_state(envelope, restore_results)
    if gate_state != "PASSED":
        return gate_state

    pending = envelope.get("pending_verification", [])
    if any(
        isinstance(item, Mapping)
        and item.get("status") in {"pending", "running", "blocked", "failed"}
        for item in pending
    ):
        return "REVIEW_REQUIRED"

    next_action = envelope.get("next_action")
    if not isinstance(next_action, Mapping):
        return "BLOCKED"
    blocked_by = next_action.get("blocked_by", [])
    if not isinstance(blocked_by, list):
        return "BLOCKED"
    if blocked_by:
        return "REVIEW_REQUIRED"

    return "RESUMABLE"
