#!/usr/bin/env python3
"""Check PythiaLabs canonical authorization export fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

AUTH_SCHEMA = "org.pythialabs.authorization-record.v0.1"
EXPORT_PROFILE = "org.pythialabs.authorization-export.v0.1"
ACTION_PROFILE = "org.liminal.trustworthy-transition.action-identity.v0.1"
ARGS_PROFILE = "org.pythialabs.authorization-arguments.v0.1"
OBS_SCHEMA = "org.liminal.trustworthy-transition.observation.v0.1"
INTEGRITY_SCHEMA = "org.liminal.trustworthy-transition.response-integrity.v0.1"
CLAIM_BOUNDARY = (
    "PythiaLabs proves the deterministic pre-execution gate decision and the "
    "decision-time evidence bindings in this record; it does not prove "
    "downstream execution, observation-source truth, or response honesty."
)
VALID_STATES = {"ACTIVE", "BLOCKED", "EXPIRED", "REVALIDATION_REQUIRED"}


class FixtureError(ValueError):
    pass


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value).encode()).hexdigest()


def text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise FixtureError(f"{label} must be a non-empty string")
    return value


def strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(x, str) or not x for x in value):
        raise FixtureError(f"{label} must be a string array")
    if len(value) != len(set(value)):
        raise FixtureError(f"{label} must not contain duplicates")
    return value


def wrap(record: dict[str, Any]) -> dict[str, Any]:
    body = canonical(record)
    return {
        "record": record,
        "canonical_bytes_utf8": body,
        "record_ref": "sha256:" + hashlib.sha256(body.encode()).hexdigest(),
    }


def export(case: dict[str, Any]) -> dict[str, Any]:
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
    if set(identity) != {"caller_id", "tool_id", "resource_scope"}:
        raise FixtureError(f"{case_id} has invalid action identity")

    action_preimage = {"profile_id": ACTION_PROFILE, **identity}
    arguments_preimage = {
        "profile_id": ARGS_PROFILE,
        "arguments_schema": text(action.get("arguments_schema"), "arguments_schema"),
        "arguments": arguments,
    }
    record = {
        "schema": AUTH_SCHEMA,
        "profile": EXPORT_PROFILE,
        "transition_id": text(source.get("transition_id"), "transition_id"),
        "subject_id": text(source.get("subject_id"), "subject_id"),
        "source_showcase": text(source.get("source_showcase"), "source_showcase"),
        "gate_profile": text(gate.get("profile"), "gate.profile"),
        "gate_version": text(gate.get("version"), "gate.version"),
        "action_identity_profile": ACTION_PROFILE,
        "action_identity_digest": digest(action_preimage),
        "arguments_profile": ARGS_PROFILE,
        "arguments_digest": digest(arguments_preimage),
        "decision": text(gate.get("decision"), "decision"),
        "reason_codes": strings(gate.get("reason_codes"), "reason_codes"),
        "decision_time": text(gate.get("decision_time"), "decision_time"),
        "evaluation_clock": text(gate.get("evaluation_clock"), "evaluation_clock"),
        "valid_from": text(gate.get("valid_from"), "valid_from"),
        "expires_at": gate.get("expires_at"),
        "approval_state": text(gate.get("approval_state"), "approval_state"),
        "credential_state": text(gate.get("credential_state"), "credential_state"),
        "evidence_snapshot_digest": text(gate.get("evidence_snapshot_digest"), "evidence_snapshot_digest"),
        "evidence_refs": strings(gate.get("evidence_refs"), "evidence_refs"),
        "environment_digest": text(gate.get("environment_digest"), "environment_digest"),
        "target_state_digest": text(gate.get("target_state_digest"), "target_state_digest"),
        "continuation_requirement": text(gate.get("continuation_requirement"), "continuation_requirement"),
        "revalidation_requirements": strings(gate.get("revalidation_requirements"), "revalidation_requirements"),
        "artifact_digest": text(gate.get("artifact_digest"), "artifact_digest"),
        "verification": {
            "algorithm": "sha256",
            "status": text(gate.get("verification_status"), "verification_status"),
            "verifier": text(gate.get("verifier"), "verifier"),
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }
    if record["decision"] not in {"ALLOW", "BLOCK", "ESCALATE"}:
        raise FixtureError(f"{case_id} has invalid decision")
    return wrap(record)


def handoff(case: dict[str, Any], authorization: dict[str, Any]) -> dict[str, Any] | None:
    source = case.get("handoff")
    if source is None:
        return None
    if not isinstance(source, dict) or not isinstance(source.get("observation"), dict):
        raise FixtureError(f"{case['case_id']} has invalid handoff")
    record = authorization["record"]
    observation_input = source["observation"]
    observation = {
        "schema": OBS_SCHEMA,
        "transition_id": record["transition_id"],
        "subject_id": record["subject_id"],
        "authorization_ref": authorization["record_ref"],
        "action_identity_digest": record["action_identity_digest"],
        "binding_digest": record["arguments_digest"],
        "execution_status": text(observation_input.get("execution_status"), "execution_status"),
        "observed_at": text(observation_input.get("observed_at"), "observed_at"),
        "result_digest": text(observation_input.get("result_digest"), "result_digest"),
        "issuer": text(observation_input.get("issuer"), "issuer"),
    }
    result: dict[str, Any] = {
        "observation_record": {"record": observation, "record_ref": digest(observation)},
        "expected_join": text(source.get("expected_join"), "expected_join"),
    }
    integrity_input = source.get("response_integrity")
    if isinstance(integrity_input, dict):
        integrity = {
            "schema": INTEGRITY_SCHEMA,
            "transition_id": record["transition_id"],
            "subject_id": record["subject_id"],
            "authorization_ref": authorization["record_ref"],
            "observation_refs": [result["observation_record"]["record_ref"]],
            "overall_verdict": text(integrity_input.get("overall_verdict"), "overall_verdict"),
            "verifier": text(integrity_input.get("verifier"), "integrity.verifier"),
            "claim_boundary": text(integrity_input.get("claim_boundary"), "integrity.claim_boundary"),
        }
        result["response_integrity_record"] = {"record": integrity, "record_ref": digest(integrity)}
    return result


def verify(case: dict[str, Any]) -> dict[str, Any]:
    case_id = text(case.get("case_id"), "case_id")
    expected = case.get("expected")
    if not isinstance(expected, dict):
        raise FixtureError(f"{case_id}.expected must be an object")
    authorization = export(case)
    if authorization["record_ref"] != expected.get("authorization_ref"):
        raise FixtureError(f"{case_id} authorization_ref regression")
    state = expected.get("authority_state")
    if state not in VALID_STATES:
        raise FixtureError(f"{case_id} has invalid authority_state")
    allowed = authorization["record"]["decision"] == "ALLOW" and state == "ACTIVE"
    if expected.get("execution_allowed") is not allowed:
        raise FixtureError(f"{case_id} execution_allowed mismatch")
    if expected.get("expected_additional_side_effects") != (1 if allowed else 0):
        raise FixtureError(f"{case_id} side-effect expectation mismatch")

    joined = handoff(case, authorization)
    if joined:
        observation = joined["observation_record"]
        if observation["record_ref"] != expected.get("observation_ref"):
            raise FixtureError(f"{case_id} observation_ref regression")
        if observation["record"]["authorization_ref"] != authorization["record_ref"]:
            raise FixtureError(f"{case_id} authorization join mismatch")
        integrity = joined.get("response_integrity_record")
        if integrity and integrity["record_ref"] != expected.get("response_integrity_ref"):
            raise FixtureError(f"{case_id} response_integrity_ref regression")
    return {"authorization_record": authorization, "handoff": joined}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", nargs="?", type=Path,
                        default=Path("conformance/pythialabs-authorization-export-v0.1.json"))
    parser.add_argument("--emit-case")
    args = parser.parse_args()
    try:
        data = json.loads(args.fixture.read_text(encoding="utf-8"))
        if data.get("profile") != EXPORT_PROFILE:
            raise FixtureError("fixture profile mismatch")
        seen: set[str] = set()
        selected = None
        for case in data.get("cases", []):
            case_id = text(case.get("case_id"), "case_id")
            if case_id in seen:
                raise FixtureError(f"duplicate case_id: {case_id}")
            seen.add(case_id)
            derived = verify(case)
            if case_id == args.emit_case:
                selected = derived
            record = derived["authorization_record"]["record"]
            print(f"PASS {case_id} -> {record['source_showcase']} / {record['decision']} / {case['expected']['authority_state']}")
        if args.emit_case:
            if selected is None:
                raise FixtureError(f"unknown case_id: {args.emit_case}")
            print(json.dumps(selected, ensure_ascii=False, indent=2))
        print(f"\nPythiaLabs authorization export fixtures passed: {len(seen)}")
        return 0
    except (OSError, json.JSONDecodeError, FixtureError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
