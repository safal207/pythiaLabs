#!/usr/bin/env python3
"""Check PythiaLabs canonical authorization export fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import rfc8785
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import SchemaError
except ImportError as error:  # pragma: no cover - exercised by local misuse
    print(
        "ERROR: install scripts/requirements-pythialabs-authorization-export.txt",
        file=sys.stderr,
    )
    raise SystemExit(2) from error

AUTH_SCHEMA = "org.pythialabs.authorization-record.v0.1"
EXPORT_PROFILE = "org.pythialabs.authorization-export.v0.1"
ACTION_PROFILE = "org.liminal.trustworthy-transition.action-identity.v0.1"
ARGS_PROFILE = "org.pythialabs.authorization-arguments.v0.1"
OBS_SCHEMA = "org.liminal.trustworthy-transition.observation.v0.1"
INTEGRITY_SCHEMA = "org.liminal.trustworthy-transition.response-integrity.v0.1"
SCHEMA_PATH = Path(
    "schemas/interop/pythialabs-authorization-record-v0.1.schema.json"
)
CLAIM_BOUNDARY = (
    "PythiaLabs proves the deterministic pre-execution gate decision and the "
    "decision-time evidence bindings in this record; it does not prove "
    "downstream execution, observation-source truth, or response honesty."
)
VALID_STATES = {"ACTIVE", "BLOCKED", "EXPIRED", "REVALIDATION_REQUIRED"}
VALID_JOINS = {"MATCH", "MATCH_WITH_INTEGRITY_FAILURE"}
SHA256_PREFIX = "sha256:"


class FixtureError(ValueError):
    """Raised when a conformance fixture violates the export contract."""


def canonical(value: Any) -> bytes:
    """Return RFC 8785/JCS canonical UTF-8 bytes for a JSON value."""
    try:
        return rfc8785.dumps(value)
    except rfc8785.CanonicalizationError as error:
        raise FixtureError(
            f"value cannot be canonicalized with RFC 8785: {error}"
        ) from error


def digest(value: Any) -> str:
    """Return a lowercase SHA-256 reference over canonical JCS bytes."""
    return SHA256_PREFIX + hashlib.sha256(canonical(value)).hexdigest()


def text(value: Any, label: str) -> str:
    """Require a non-empty string."""
    if not isinstance(value, str) or not value:
        raise FixtureError(f"{label} must be a non-empty string")
    return value


def strings(
    value: Any,
    label: str,
    *,
    allow_empty: bool = False,
) -> list[str]:
    """Require a unique array of non-empty strings."""
    if not isinstance(value, list):
        raise FixtureError(f"{label} must be a string array")
    if not allow_empty and not value:
        raise FixtureError(f"{label} must not be empty")
    if any(not isinstance(item, str) or not item for item in value):
        raise FixtureError(f"{label} must be a string array")
    if len(value) != len(set(value)):
        raise FixtureError(f"{label} must not contain duplicates")
    return list(value)


def sha256_ref(value: Any, label: str) -> str:
    """Require a portable sha256:<64 lowercase hex> reference."""
    value = text(value, label)
    if len(value) != 71 or not value.startswith(SHA256_PREFIX):
        raise FixtureError(f"{label} must be sha256:<64 lowercase hex>")
    suffix = value[len(SHA256_PREFIX):]
    if any(character not in "0123456789abcdef" for character in suffix):
        raise FixtureError(f"{label} must be sha256:<64 lowercase hex>")
    return value


def timestamp(value: Any, label: str) -> datetime:
    """Parse a timezone-aware ISO-8601 timestamp."""
    value = text(value, label)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise FixtureError(f"{label} must be ISO-8601") from error
    if parsed.tzinfo is None:
        raise FixtureError(f"{label} must include a timezone")
    return parsed


def exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    """Reject missing and unknown object fields."""
    if set(value) != expected:
        raise FixtureError(f"{label} must contain exactly {sorted(expected)}")


def wrap(record: dict[str, Any]) -> dict[str, Any]:
    """Wrap a record with canonical text and its content-addressed reference."""
    body = canonical(record)
    return {
        "record": record,
        "canonical_bytes_utf8": body.decode("utf-8"),
        "record_ref": SHA256_PREFIX + hashlib.sha256(body).hexdigest(),
    }


def load_schema_validator() -> Draft202012Validator:
    """Load and compile the published authorization-record schema."""
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except (OSError, json.JSONDecodeError, SchemaError) as error:
        raise FixtureError(f"cannot load authorization schema: {error}") from error
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate_record(
    case_id: str,
    record: dict[str, Any],
    validator: Draft202012Validator,
) -> None:
    """Validate a derived record against the published Draft 2020-12 schema."""
    errors = sorted(
        validator.iter_errors(record),
        key=lambda error: [str(part) for part in error.absolute_path],
    )
    if not errors:
        return
    error = errors[0]
    path = ".".join(str(part) for part in error.absolute_path) or "<record>"
    raise FixtureError(f"{case_id} schema violation at {path}: {error.message}")


def export(case: dict[str, Any]) -> dict[str, Any]:
    """Derive one canonical provider-neutral authorization record."""
    case_id = text(case.get("case_id"), "case_id")
    source = case.get("input")
    if not isinstance(source, dict):
        raise FixtureError(f"{case_id}.input must be an object")
    action = source.get("action")
    gate = source.get("gate")
    if not isinstance(action, dict) or not isinstance(gate, dict):
        raise FixtureError(f"{case_id} requires action and gate objects")
    identity = action.get("identity")
    arguments = action.get("arguments")
    if not isinstance(identity, dict) or not isinstance(arguments, dict):
        raise FixtureError(f"{case_id} requires identity and arguments objects")
    exact_keys(
        identity,
        {"caller_id", "tool_id", "resource_scope"},
        f"{case_id}.action.identity",
    )
    for key in ("caller_id", "tool_id", "resource_scope"):
        text(identity.get(key), f"{case_id}.action.identity.{key}")

    action_preimage = {"profile_id": ACTION_PROFILE, **identity}
    arguments_preimage = {
        "profile_id": ARGS_PROFILE,
        "arguments_schema": text(
            action.get("arguments_schema"),
            f"{case_id}.arguments_schema",
        ),
        "arguments": arguments,
    }
    expires_at = gate.get("expires_at")
    if expires_at is not None:
        text(expires_at, f"{case_id}.expires_at")

    record = {
        "schema": AUTH_SCHEMA,
        "profile": EXPORT_PROFILE,
        "transition_id": text(
            source.get("transition_id"), f"{case_id}.transition_id"
        ),
        "subject_id": text(source.get("subject_id"), f"{case_id}.subject_id"),
        "source_showcase": text(
            source.get("source_showcase"), f"{case_id}.source_showcase"
        ),
        "gate_profile": text(gate.get("profile"), f"{case_id}.gate.profile"),
        "gate_version": text(gate.get("version"), f"{case_id}.gate.version"),
        "action_identity_profile": ACTION_PROFILE,
        "action_identity_digest": digest(action_preimage),
        "arguments_profile": ARGS_PROFILE,
        "arguments_digest": digest(arguments_preimage),
        "decision": text(gate.get("decision"), f"{case_id}.decision"),
        "reason_codes": strings(
            gate.get("reason_codes"), f"{case_id}.reason_codes"
        ),
        "decision_time": text(
            gate.get("decision_time"), f"{case_id}.decision_time"
        ),
        "evaluation_clock": text(
            gate.get("evaluation_clock"), f"{case_id}.evaluation_clock"
        ),
        "valid_from": text(gate.get("valid_from"), f"{case_id}.valid_from"),
        "expires_at": expires_at,
        "approval_state": text(
            gate.get("approval_state"), f"{case_id}.approval_state"
        ),
        "credential_state": text(
            gate.get("credential_state"), f"{case_id}.credential_state"
        ),
        "evidence_snapshot_digest": sha256_ref(
            gate.get("evidence_snapshot_digest"),
            f"{case_id}.evidence_snapshot_digest",
        ),
        "evidence_refs": strings(
            gate.get("evidence_refs"), f"{case_id}.evidence_refs"
        ),
        "environment_digest": sha256_ref(
            gate.get("environment_digest"), f"{case_id}.environment_digest"
        ),
        "target_state_digest": sha256_ref(
            gate.get("target_state_digest"), f"{case_id}.target_state_digest"
        ),
        "continuation_requirement": text(
            gate.get("continuation_requirement"),
            f"{case_id}.continuation_requirement",
        ),
        "revalidation_requirements": strings(
            gate.get("revalidation_requirements"),
            f"{case_id}.revalidation_requirements",
            allow_empty=True,
        ),
        "artifact_digest": sha256_ref(
            gate.get("artifact_digest"), f"{case_id}.artifact_digest"
        ),
        "verification": {
            "algorithm": "sha256",
            "status": text(
                gate.get("verification_status"),
                f"{case_id}.verification_status",
            ),
            "verifier": text(gate.get("verifier"), f"{case_id}.verifier"),
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }
    if record["decision"] not in {"ALLOW", "BLOCK", "ESCALATE"}:
        raise FixtureError(f"{case_id} has invalid decision")
    return wrap(record)


def derive_authority_state(record: dict[str, Any]) -> str:
    """Derive effective authority from decision-time temporal and drift fields."""
    decision_time = timestamp(record["decision_time"], "decision_time")
    evaluation_clock = timestamp(record["evaluation_clock"], "evaluation_clock")
    valid_from = timestamp(record["valid_from"], "valid_from")
    expires_at = (
        None
        if record["expires_at"] is None
        else timestamp(record["expires_at"], "expires_at")
    )
    if decision_time > evaluation_clock:
        raise FixtureError("decision_time must not follow evaluation_clock")
    if expires_at is not None and expires_at < valid_from:
        raise FixtureError("expires_at must not precede valid_from")
    if expires_at is not None and evaluation_clock > expires_at:
        return "EXPIRED"
    if evaluation_clock < valid_from:
        return "REVALIDATION_REQUIRED"

    requirements = record["revalidation_requirements"]
    continuation = record["continuation_requirement"]
    if (
        requirements
        or continuation.startswith("REVALIDATE")
        or continuation == "REAUTHORIZE"
    ):
        return "REVALIDATION_REQUIRED"
    if record["decision"] != "ALLOW":
        return "BLOCKED"
    if record["credential_state"] != "VALID":
        return "BLOCKED"
    if record["approval_state"] == "MISSING":
        return "BLOCKED"
    if record["verification"]["status"] != "VERIFIED":
        return "BLOCKED"
    return "ACTIVE"


def handoff(
    case: dict[str, Any],
    authorization: dict[str, Any],
) -> dict[str, Any] | None:
    """Build downstream observation and optional external integrity records."""
    source = case.get("handoff")
    if source is None:
        return None
    case_id = case["case_id"]
    if not isinstance(source, dict) or not isinstance(
        source.get("observation"), dict
    ):
        raise FixtureError(f"{case_id} has invalid handoff")
    if not {"observation", "expected_join"}.issubset(source):
        raise FixtureError(f"{case_id} handoff is incomplete")
    if not set(source).issubset(
        {"observation", "expected_join", "response_integrity"}
    ):
        raise FixtureError(f"{case_id} handoff has unknown fields")
    expected_join = text(source.get("expected_join"), f"{case_id}.expected_join")
    if expected_join not in VALID_JOINS:
        raise FixtureError(f"{case_id} has invalid expected_join")

    record = authorization["record"]
    observation_input = source["observation"]
    exact_keys(
        observation_input,
        {"execution_status", "observed_at", "result_digest", "issuer"},
        f"{case_id}.observation",
    )
    observation = {
        "schema": OBS_SCHEMA,
        "transition_id": record["transition_id"],
        "subject_id": record["subject_id"],
        "authorization_ref": authorization["record_ref"],
        "action_identity_digest": record["action_identity_digest"],
        "binding_digest": record["arguments_digest"],
        "execution_status": text(
            observation_input.get("execution_status"),
            f"{case_id}.execution_status",
        ),
        "observed_at": text(
            observation_input.get("observed_at"), f"{case_id}.observed_at"
        ),
        "result_digest": sha256_ref(
            observation_input.get("result_digest"), f"{case_id}.result_digest"
        ),
        "issuer": text(observation_input.get("issuer"), f"{case_id}.issuer"),
    }
    if observation["execution_status"] not in {
        "EXECUTED",
        "BLOCKED",
        "ERRORED",
        "REFUSED",
    }:
        raise FixtureError(f"{case_id} has invalid execution_status")
    result: dict[str, Any] = {
        "observation_record": {
            "record": observation,
            "record_ref": digest(observation),
        },
        "expected_join": expected_join,
    }

    integrity_input = source.get("response_integrity")
    if integrity_input is not None:
        if not isinstance(integrity_input, dict):
            raise FixtureError(f"{case_id}.response_integrity must be an object")
        exact_keys(
            integrity_input,
            {"overall_verdict", "verifier", "claim_boundary"},
            f"{case_id}.response_integrity",
        )
        integrity = {
            "schema": INTEGRITY_SCHEMA,
            "transition_id": record["transition_id"],
            "subject_id": record["subject_id"],
            "authorization_ref": authorization["record_ref"],
            "observation_refs": [result["observation_record"]["record_ref"]],
            "overall_verdict": text(
                integrity_input.get("overall_verdict"),
                f"{case_id}.overall_verdict",
            ),
            "verifier": text(
                integrity_input.get("verifier"),
                f"{case_id}.integrity.verifier",
            ),
            "claim_boundary": text(
                integrity_input.get("claim_boundary"),
                f"{case_id}.integrity.claim_boundary",
            ),
        }
        result["response_integrity_record"] = {
            "record": integrity,
            "record_ref": digest(integrity),
        }
    return result


def derive_join(joined: dict[str, Any]) -> str:
    """Derive the handoff join outcome from independently attributed records."""
    integrity = joined.get("response_integrity_record")
    if integrity is None:
        return "MATCH"
    verdict = integrity["record"]["overall_verdict"]
    return (
        "MATCH"
        if verdict == "VERIFIED"
        else "MATCH_WITH_INTEGRITY_FAILURE"
    )


def verify(
    case: dict[str, Any],
    validator: Draft202012Validator,
    showcase_adapters: dict[str, Any],
) -> dict[str, Any]:
    """Verify one fixture without trusting expected authority or join verdicts."""
    case_id = text(case.get("case_id"), "case_id")
    expected = case.get("expected")
    if not isinstance(expected, dict):
        raise FixtureError(f"{case_id}.expected must be an object")

    authorization = export(case)
    record = authorization["record"]
    validate_record(case_id, record, validator)
    expected_profile = showcase_adapters.get(record["source_showcase"])
    if expected_profile != record["gate_profile"]:
        raise FixtureError(f"{case_id} showcase adapter/profile mismatch")
    if authorization["record_ref"] != expected.get("authorization_ref"):
        raise FixtureError(f"{case_id} authorization_ref regression")

    state = derive_authority_state(record)
    if state not in VALID_STATES:
        raise FixtureError(f"{case_id} has invalid derived authority_state")
    if expected.get("authority_state") != state:
        raise FixtureError(
            f"{case_id} authority_state mismatch: "
            f"{expected.get('authority_state')} != {state}"
        )
    allowed = record["decision"] == "ALLOW" and state == "ACTIVE"
    if expected.get("execution_allowed") is not allowed:
        raise FixtureError(f"{case_id} execution_allowed mismatch")
    if expected.get("expected_additional_side_effects") != (1 if allowed else 0):
        raise FixtureError(f"{case_id} side-effect expectation mismatch")

    joined = handoff(case, authorization)
    derived_join = None
    if joined is not None:
        observation = joined["observation_record"]
        if observation["record_ref"] != expected.get("observation_ref"):
            raise FixtureError(f"{case_id} observation_ref regression")
        observation_record = observation["record"]
        if observation_record["authorization_ref"] != authorization["record_ref"]:
            raise FixtureError(f"{case_id} authorization join mismatch")
        if (
            observation_record["action_identity_digest"]
            != record["action_identity_digest"]
        ):
            raise FixtureError(f"{case_id} action identity join mismatch")
        if observation_record["binding_digest"] != record["arguments_digest"]:
            raise FixtureError(f"{case_id} arguments binding join mismatch")
        observed_at = timestamp(observation_record["observed_at"], "observed_at")
        if observed_at < timestamp(record["decision_time"], "decision_time"):
            raise FixtureError(f"{case_id} observation predates decision")
        if observation_record["execution_status"] == "EXECUTED" and not allowed:
            raise FixtureError(f"{case_id} executed without active authority")

        integrity = joined.get("response_integrity_record")
        if integrity is not None:
            if integrity["record_ref"] != expected.get("response_integrity_ref"):
                raise FixtureError(
                    f"{case_id} response_integrity_ref regression"
                )
            integrity_record = integrity["record"]
            if integrity_record["authorization_ref"] != authorization["record_ref"]:
                raise FixtureError(
                    f"{case_id} integrity authorization join mismatch"
                )
            if integrity_record["observation_refs"] != [observation["record_ref"]]:
                raise FixtureError(
                    f"{case_id} integrity observation join mismatch"
                )

        derived_join = derive_join(joined)
        if joined["expected_join"] != derived_join:
            raise FixtureError(
                f"{case_id} expected_join mismatch: "
                f"{joined['expected_join']} != {derived_join}"
            )
    elif any(
        key in expected
        for key in ("observation_ref", "response_integrity_ref")
    ):
        raise FixtureError(f"{case_id} expected handoff references without handoff")

    return {
        "authorization_record": authorization,
        "authority_state": state,
        "derived_join": derived_join,
        "handoff": joined,
    }


def main() -> int:
    """Load fixtures, validate every case, and optionally emit one derivation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "fixture",
        nargs="?",
        type=Path,
        default=Path(
            "conformance/pythialabs-authorization-export-v0.1.json"
        ),
    )
    parser.add_argument("--emit-case")
    args = parser.parse_args()
    try:
        data = json.loads(args.fixture.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise FixtureError("fixture must contain an object")
        if data.get("profile") != EXPORT_PROFILE:
            raise FixtureError("fixture profile mismatch")
        if data.get("canonicalization") != "RFC8785-JCS":
            raise FixtureError("fixture canonicalization mismatch")
        if data.get("hash_algorithm") != "sha256":
            raise FixtureError("fixture hash algorithm mismatch")
        if data.get("schema_path") != str(SCHEMA_PATH):
            raise FixtureError("fixture schema path mismatch")
        cases = data.get("cases")
        showcase_adapters = data.get("showcase_adapters")
        if not isinstance(cases, list) or not cases:
            raise FixtureError("fixture cases must be a non-empty array")
        if not isinstance(showcase_adapters, dict):
            raise FixtureError("showcase_adapters must be an object")

        validator = load_schema_validator()
        seen: set[str] = set()
        selected = None
        for case in cases:
            if not isinstance(case, dict):
                raise FixtureError("case entry must be an object")
            case_id = text(case.get("case_id"), "case_id")
            if case_id in seen:
                raise FixtureError(f"duplicate case_id: {case_id}")
            seen.add(case_id)
            derived = verify(case, validator, showcase_adapters)
            if case_id == args.emit_case:
                selected = derived
            record = derived["authorization_record"]["record"]
            print(
                f"PASS {case_id} -> {record['source_showcase']} / "
                f"{record['decision']} / {derived['authority_state']}"
            )
        if args.emit_case:
            if selected is None:
                raise FixtureError(f"unknown case_id: {args.emit_case}")
            print(json.dumps(selected, ensure_ascii=False, indent=2))
        print(
            f"\nPythiaLabs authorization export fixtures passed: {len(seen)}"
        )
        return 0
    except (OSError, json.JSONDecodeError, FixtureError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
