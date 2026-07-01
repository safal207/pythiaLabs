from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCHEMA_PATH = ROOT / "schema" / "action-envelope-v1.schema.json"

ALLOW = "ALLOW"
BLOCK = "BLOCK"
ESCALATE = "ESCALATE"

UNSUPPORTED_SCHEMA_VERSION = "UNSUPPORTED_SCHEMA_VERSION"
SCHEMA_INVALID = "SCHEMA_INVALID"
DIGEST_MISMATCH = "DIGEST_MISMATCH"
AUTHORIZATION_MISMATCH = "AUTHORIZATION_MISMATCH"
AUTHORIZATION_NOT_YET_VALID = "AUTHORIZATION_NOT_YET_VALID"
AUTHORIZATION_EXPIRED = "AUTHORIZATION_EXPIRED"
EVIDENCE_ACTION_MISMATCH = "EVIDENCE_ACTION_MISMATCH"
EVIDENCE_NOT_YET_VALID = "EVIDENCE_NOT_YET_VALID"
EVIDENCE_STALE = "EVIDENCE_STALE"
UNKNOWN_EVIDENCE_REF = "UNKNOWN_EVIDENCE_REF"
PRECONDITION_FAILED = "PRECONDITION_FAILED"
PRECONDITION_UNRESOLVED = "PRECONDITION_UNRESOLVED"
REPLAY_DETECTED = "REPLAY_DETECTED"
RECOVERY_NOT_READY = "RECOVERY_NOT_READY"
ALLOW_OK = "ALLOW_OK"

SUPPORTED_SCHEMA_VERSION = "1.0"


def load_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} root must be an object")
    return value


def load_schema() -> dict[str, Any]:
    schema = load_json_object(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    return schema


def schema_errors(document: Mapping[str, Any]) -> list[str]:
    validator = Draft202012Validator(
        load_schema(),
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


def with_computed_digest(envelope: Mapping[str, Any]) -> dict[str, Any]:
    value = dict(envelope)
    value["envelope_digest"] = {
        "algorithm": "sha256",
        "canonicalization": "json-sort-keys-utf8-v1",
        "value": compute_digest(value),
    }
    return value


def verify_digest(envelope: Mapping[str, Any]) -> bool:
    digest = envelope.get("envelope_digest")
    return (
        isinstance(digest, Mapping)
        and digest.get("algorithm") == "sha256"
        and digest.get("canonicalization") == "json-sort-keys-utf8-v1"
        and digest.get("value") == compute_digest(envelope)
    )


def parse_time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed


def decision(decision_value: str, reason_code: str, detail: str) -> dict[str, str]:
    return {
        "decision": decision_value,
        "reason_code": reason_code,
        "detail": detail,
    }


def evaluate_action(
    envelope: Mapping[str, Any],
    *,
    seen_idempotency_keys: Iterable[str] = (),
) -> dict[str, str]:
    schema_version = envelope.get("schema_version")
    if isinstance(schema_version, str) and schema_version != SUPPORTED_SCHEMA_VERSION:
        return decision(
            BLOCK,
            UNSUPPORTED_SCHEMA_VERSION,
            f"supported schema_version is {SUPPORTED_SCHEMA_VERSION}",
        )

    errors = schema_errors(envelope)
    if errors:
        return decision(BLOCK, SCHEMA_INVALID, errors[0])

    if not verify_digest(envelope):
        return decision(BLOCK, DIGEST_MISMATCH, "envelope digest verification failed")

    action_id = envelope["action_id"]
    request = envelope["request"]
    actor = envelope["actor"]
    authorization = envelope["authorization"]
    decision_time = parse_time(envelope["decision_time"])

    authorization_bindings = {
        "actor_id": actor["actor_id"],
        "granted_to": actor["agent_id"],
        "capability": request["capability"],
        "operation": request["operation"],
        "target": request["target"],
        "environment": request["environment"],
    }
    for field, expected in authorization_bindings.items():
        if authorization[field] != expected:
            return decision(
                BLOCK,
                AUTHORIZATION_MISMATCH,
                f"authorization {field} does not match the proposed action",
            )

    if decision_time < parse_time(authorization["valid_from"]):
        return decision(
            BLOCK,
            AUTHORIZATION_NOT_YET_VALID,
            "authorization is not valid at decision_time",
        )
    if decision_time > parse_time(authorization["valid_until"]):
        return decision(
            BLOCK,
            AUTHORIZATION_EXPIRED,
            "authorization expired before decision_time",
        )

    evidence_by_id: dict[str, Mapping[str, Any]] = {}
    for row in envelope["evidence"]:
        evidence_id = row["evidence_id"]
        if evidence_id in evidence_by_id:
            return decision(
                BLOCK,
                SCHEMA_INVALID,
                f"duplicate evidence_id: {evidence_id}",
            )
        evidence_by_id[evidence_id] = row

        if row["action_id"] != action_id:
            return decision(
                BLOCK,
                EVIDENCE_ACTION_MISMATCH,
                f"evidence {evidence_id} is bound to another action",
            )
        if decision_time < parse_time(row["observed_at"]):
            return decision(
                BLOCK,
                EVIDENCE_NOT_YET_VALID,
                f"evidence {evidence_id} was observed after decision_time",
            )
        if decision_time > parse_time(row["expires_at"]):
            return decision(
                BLOCK,
                EVIDENCE_STALE,
                f"evidence {evidence_id} expired before decision_time",
            )

    unresolved = []
    for row in envelope["preconditions"]:
        precondition_id = row["precondition_id"]
        for evidence_ref in row["evidence_refs"]:
            if evidence_ref not in evidence_by_id:
                return decision(
                    BLOCK,
                    UNKNOWN_EVIDENCE_REF,
                    f"precondition {precondition_id} references unknown evidence {evidence_ref}",
                )
        if row["status"] == "failed":
            return decision(
                BLOCK,
                PRECONDITION_FAILED,
                f"precondition {precondition_id} failed",
            )
        if row["status"] == "unknown":
            unresolved.append(precondition_id)

    if unresolved:
        return decision(
            ESCALATE,
            PRECONDITION_UNRESOLVED,
            "unresolved preconditions: " + ", ".join(unresolved),
        )

    idempotency_key = envelope["idempotency"]["key"]
    if idempotency_key in set(seen_idempotency_keys):
        return decision(
            BLOCK,
            REPLAY_DETECTED,
            f"idempotency key already observed: {idempotency_key}",
        )

    recovery = envelope["recovery"]
    if recovery["rollback_required"] and not recovery["rollback_available"]:
        return decision(
            ESCALATE,
            RECOVERY_NOT_READY,
            "rollback is required but not available",
        )

    return decision(ALLOW, ALLOW_OK, "all declared checks passed")
