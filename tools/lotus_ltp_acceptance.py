#!/usr/bin/env python3
"""Validate an LTP-joined transition and emit a bounded Lotus judgment.

This adapter is deterministic and fail-closed. It may emit an artifact-only
negative-memory candidate; it cannot write durable memory, submit externally,
execute, deploy, or merge.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "pythia-lotus-ltp-judgment-v0.1"
EVENT_SCHEMA = "liminaldb-pythia-negative-memory-event-v0.1"
GRANTS = ("ownership", "approval", "execution", "delivery", "external_submission", "deployment", "merge")
SHA_REF = re.compile(r"^sha256:[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha256_hex(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def sha256_ref(value: Any) -> str:
    return f"sha256:{sha256_hex(value)}"


def mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be an object")
    return value


def text(obj: dict[str, Any], key: str, context: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}.{key} must be a non-empty string")
    return value


def timestamp(value: str, context: str) -> None:
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError(f"{context} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{context} must include a timezone")


def false_authority(value: Any, context: str, mode: str) -> dict[str, Any]:
    authority = mapping(value, context)
    if authority.get("mode") != mode:
        raise ValueError(f"{context}.mode must be {mode}")
    for grant in GRANTS:
        if authority.get(grant) is not False:
            raise ValueError(f"{context}.{grant} must be false")
    if authority.get("product_verdict_override", False) is not False:
        raise ValueError(f"{context}.product_verdict_override must be false")
    return authority


def wrapper(value: Any, context: str) -> dict[str, Any]:
    value = mapping(value, context)
    record = mapping(value.get("record"), f"{context}.record")
    record_ref = text(value, "record_ref", context)
    if SHA_REF.fullmatch(record_ref) is None or record_ref != sha256_ref(record):
        raise ValueError(f"{context}.record_ref mismatch")
    return value


def validate_packet(packet: dict[str, Any], authorization: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    if packet.get("schema_version") != "airbnb-ltp-transition-v0.1":
        raise ValueError("packet.schema_version is unsupported")
    transition_id = text(packet, "transition_id", "packet")
    subject_id = text(packet, "subject_id", "packet")
    ltp_commit = text(packet, "ltp_commit", "packet")
    if HEX40.fullmatch(ltp_commit) is None:
        raise ValueError("packet.ltp_commit must be a full SHA")

    authorization = wrapper(authorization, "authorization")
    observation = wrapper(observation, "observation")
    auth = authorization["record"]
    obs = observation["record"]
    if packet.get("authorization_ref") != authorization["record_ref"]:
        raise ValueError("packet.authorization_ref mismatch")
    if packet.get("observation_ref") != observation["record_ref"]:
        raise ValueError("packet.observation_ref mismatch")
    for label, record in (("authorization", auth), ("observation", obs)):
        if record.get("transition_id") != transition_id or record.get("subject_id") != subject_id:
            raise ValueError(f"{label} identity mismatch")
    if obs.get("authorization_ref") != authorization["record_ref"]:
        raise ValueError("observation authorization_ref mismatch")
    for key in ("action_identity_digest", "binding_digest"):
        if obs.get(key) != auth.get(key):
            raise ValueError(f"authorization/observation {key} mismatch")
    if obs.get("execution_status") != "EXECUTED":
        raise ValueError("observation must be EXECUTED")
    if obs.get("result_digest") != sha256_ref(obs.get("result")):
        raise ValueError("observation result_digest mismatch")
    if auth.get("decision") != "ALLOW" or auth.get("current_state") != "ACTIVE":
        raise ValueError("authorization must be ACTIVE ALLOW")
    scope = mapping(auth.get("scope"), "authorization.scope")
    if scope.get("kind") != "public_readonly_airbnb_currency_history_probe":
        raise ValueError("authorization scope mismatch")
    if not {"login", "host_contact", "payment", "reservation", "external_submission"}.issubset(set(scope.get("prohibited") or [])):
        raise ValueError("authorization prohibited scope is incomplete")
    auth_boundary = mapping(auth.get("authority"), "authorization.authority")
    for key in ("external_submission", "deployment", "merge"):
        if auth_boundary.get(key) is not False:
            raise ValueError(f"authorization.authority.{key} must be false")

    verified = mapping(packet.get("verified_response"), "verified_response")
    if verified.get("transition_id") != transition_id or verified.get("subject_id") != subject_id:
        raise ValueError("verified_response identity mismatch")
    if verified.get("verification_level") != "FULL_LIFECYCLE_JOINED":
        raise ValueError("verified_response must be FULL_LIFECYCLE_JOINED")
    if verified.get("dimensions") != {"authority": "VALID", "execution": "OBSERVED_EXECUTED", "response_integrity": "VERIFIED"}:
        raise ValueError("verified_response dimensions mismatch")
    response = mapping(verified.get("response_integrity_record"), "verified response record")
    if response.get("overall_verdict") != "VERIFIED":
        raise ValueError("verified response overall_verdict must be VERIFIED")
    if response.get("authorization_ref") != authorization["record_ref"] or response.get("observation_refs") != [observation["record_ref"]]:
        raise ValueError("verified response record refs mismatch")
    claims = response.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ValueError("verified response claims must be non-empty")
    for index, claim in enumerate(claims):
        claim = mapping(claim, f"verified claim {index}")
        if claim.get("verdict") != "SUPPORTED" or claim.get("evidence_level") != "FULL_LIFECYCLE_JOINED":
            raise ValueError(f"verified claim {index} is not fully supported")
        refs = set(claim.get("required_record_refs") or [])
        if {authorization["record_ref"], observation["record_ref"]} - refs:
            raise ValueError(f"verified claim {index} missing required refs")

    negative = mapping(packet.get("fabricated_claim_control"), "negative control")
    negative_record = mapping(negative.get("response_integrity_record"), "negative control record")
    if negative.get("verification_level") != "FULL_LIFECYCLE_JOINED" or negative_record.get("overall_verdict") != "FAILED":
        raise ValueError("negative control must be FULL_LIFECYCLE_JOINED and FAILED")
    negative_claims = negative_record.get("claims")
    if not isinstance(negative_claims, list) or not any(isinstance(item, dict) and item.get("verdict") == "CONTRADICTED" for item in negative_claims):
        raise ValueError("negative control must contain a CONTRADICTED claim")

    result = mapping(obs.get("result"), "observation.result")
    run = mapping(result.get("run"), "observation.result.run")
    advisory = mapping(result.get("advisory"), "observation.result.advisory")
    workflow = mapping(result.get("workflow"), "observation.result.workflow")
    false_authority(run.get("authority"), "run.authority", "audit_only")
    false_authority(advisory.get("authority"), "advisory.authority", "advisory_only")
    if run.get("live_garden_probe_confirmed") is not True or run.get("safe_readonly_probe") is not True:
        raise ValueError("live safe Garden probe is not confirmed")
    probe = mapping(run.get("probe_summary"), "run.probe_summary")
    if probe.get("confirmed_defect") is not False or probe.get("payment_submitted") is not False or probe.get("reservation_created") is not False:
        raise ValueError("probe is not a safe negative observation")
    if probe.get("outcomes") != ["consistent", "consistent"]:
        raise ValueError("probe outcomes must be two consistent attempts")
    if advisory.get("classification") != "NO_DEFECT_OBSERVED" or advisory.get("product_verdict_source") != "normalized_evidence_not_liminalos":
        raise ValueError("LiminalOSAI advisory boundary mismatch")
    if workflow.get("ltp_commit") != ltp_commit:
        raise ValueError("workflow LTP commit mismatch")
    return {
        "transition_id": transition_id,
        "subject_id": subject_id,
        "authorization_ref": authorization["record_ref"],
        "observation_ref": observation["record_ref"],
        "observation_result_ref": obs["result_digest"],
        "claim_count": len(claims),
        "run": run,
    }


def build_judgment(validated: dict[str, Any], packet_sha256: str, generated_at: str) -> dict[str, Any]:
    timestamp(generated_at, "generated_at")
    probe = validated["run"]["probe_summary"]
    return {
        "schema_version": SCHEMA,
        "case_id": validated["transition_id"],
        "subject_id": validated["subject_id"],
        "generated_at": generated_at,
        "verdict": "ALLOW",
        "verdict_scope": "artifact_only_verified_negative_memory_candidate",
        "decision_status": "CONFIRMED",
        "result_class": "VERIFIED_NEGATIVE_OBSERVATION",
        "evidence_state": {
            "verification_level": "FULL_LIFECYCLE_JOINED",
            "authority": "VALID",
            "execution": "OBSERVED_EXECUTED",
            "response_integrity": "VERIFIED",
            "supported_claim_count": validated["claim_count"],
            "fabricated_claim_control": "CONTRADICTED",
            "packet_sha256": packet_sha256,
            "authorization_ref": validated["authorization_ref"],
            "observation_ref": validated["observation_ref"],
            "observation_result_ref": validated["observation_result_ref"],
        },
        "product_observation": {
            "platform": "Airbnb",
            "scope": "public unauthenticated currency and history behavior",
            "confirmed_defect": False,
            "outcomes": probe["outcomes"],
            "normalized_signatures": probe.get("normalized_signatures"),
            "evidence_grade": probe.get("evidence_grade"),
            "payment_submitted": False,
            "reservation_created": False,
        },
        "causal_state": {
            "cause_status": "UNCONFIRMED",
            "confidence": "OBSERVED_ONCE",
            "recurrence": "SINGLE_TRANSITION",
            "negative_claim": "The bounded scenario did not exhibit the hypothesized defect.",
            "falsifier": "A newer exact-scope LTP-joined observation with a confirmed inconsistent state supersedes this memory.",
        },
        "memory_candidate": {
            "memory_kind": "VERIFIED_NEGATIVE_OBSERVATION",
            "canonical_id": "airbnb.public.currency-history.no-defect-observed",
            "durable_memory": False,
            "write_mode": "artifact_only",
            "supersession_policy": "exact_scope_newer_verified_observation",
        },
        "pythia": {
            "evidence_sufficiency": "SUFFICIENT_FOR_NEGATIVE_OBSERVATION",
            "external_reporting": "BLOCK_NO_CONFIRMED_DEFECT",
            "causal_claim": "BLOCK_CONFIRMED_CAUSE",
            "next_action": "PRESERVE_NEGATIVE_CONTROL",
        },
        "authority": {
            "mode": "audit_only",
            "ownership": False,
            "approval": False,
            "execution": False,
            "delivery": False,
            "external_submission": False,
            "deployment": False,
            "merge": False,
            "durable_memory_write": False,
        },
    }


def build_event(judgment: dict[str, Any], source_repository: str, source_branch: str, source_commit: str, pythia_commit: str, packet_sha256: str, generated_at: str) -> dict[str, Any]:
    if not source_repository.strip() or not source_branch.strip():
        raise ValueError("source repository and branch must be non-empty")
    for label, value in (("source_commit", source_commit), ("pythia_commit", pythia_commit)):
        if HEX40.fullmatch(value) is None:
            raise ValueError(f"{label} must be a full SHA")
    judgment_sha = sha256_hex(judgment)
    event = {
        "id": f"pythia-neg-{sha256_hex({'transition': judgment['case_id'], 'judgment': judgment_sha, 'pythia': pythia_commit})[:32]}",
        "ts": generated_at,
        "kind": "audit",
        "actor": "pythia-lotus",
        "action": "lotus.verified_negative.observed",
        "details": {
            "schema_version": EVENT_SCHEMA,
            "source": {
                "repository": source_repository,
                "branch": source_branch,
                "commit": source_commit,
                "packet_id": judgment["case_id"],
                "packet_sha256": packet_sha256,
                "authorization_ref": judgment["evidence_state"]["authorization_ref"],
                "observation_ref": judgment["evidence_state"]["observation_ref"],
                "observation_result_ref": judgment["evidence_state"]["observation_result_ref"],
            },
            "judgment": {
                "schema_version": judgment["schema_version"],
                "sha256": judgment_sha,
                "decision_status": "CONFIRMED",
                "pythia_verdict": "ALLOW",
                "result_class": "VERIFIED_NEGATIVE_OBSERVATION",
                "canonical_id": judgment["memory_candidate"]["canonical_id"],
                "memory_kind": "VERIFIED_NEGATIVE_OBSERVATION",
                "cause_status": "UNCONFIRMED",
                "confidence": "OBSERVED_ONCE",
                "recurrence": "SINGLE_TRANSITION",
                "durable_memory": False,
            },
            "evidence": {
                "bounded": True,
                "replayable": True,
                "ltp_verification_level": "FULL_LIFECYCLE_JOINED",
                "response_integrity": "VERIFIED",
                "fabricated_claim_control": "CONTRADICTED",
            },
            "authority": copy.deepcopy(judgment["authority"]),
            "adapter": {
                "repository": "safal207/pythiaLabs",
                "commit": pythia_commit,
                "event_contract": "AuditEvent-extension",
                "write_mode": "artifact_only",
            },
        },
    }
    event["details"]["event_sha256"] = sha256_hex(event)
    return event


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--observation", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-repository", required=True)
    parser.add_argument("--source-branch", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--pythia-commit", required=True)
    parser.add_argument("--generated-at", required=True)
    args = parser.parse_args()
    packet = mapping(json.loads(args.packet.read_text()), "packet")
    authorization = mapping(json.loads(args.authorization.read_text()), "authorization")
    observation = mapping(json.loads(args.observation.read_text()), "observation")
    packet_sha = sha256_hex(packet)
    judgment = build_judgment(validate_packet(packet, authorization, observation), packet_sha, args.generated_at)
    event = build_event(judgment, args.source_repository, args.source_branch, args.source_commit, args.pythia_commit, packet_sha, args.generated_at)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "lotus-ltp-judgment.json").write_text(json.dumps(judgment, indent=2, sort_keys=True) + "\n")
    (args.output_dir / "liminaldb-negative-memory.jsonl").write_text(json.dumps(event, sort_keys=True) + "\n")
    print(json.dumps(judgment, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
