from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ENVELOPE_SCHEMA_PATH = ROOT / "schema" / "responsibility-lane-envelope.schema.json"
RESTORE_RESULTS_SCHEMA_PATH = ROOT / "schema" / "responsibility-lane-restore-results.schema.json"

MATERIAL_EVENT_TYPES = {
    "tool_call",
    "tool_result",
    "artifact_modified",
    "verification_started",
    "verification_result",
}


def load_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} root must be an object")
    return value


def load_schema(path: Path) -> dict[str, Any]:
    schema = load_json_object(path)
    Draft202012Validator.check_schema(schema)
    return schema


def schema_errors(document: Mapping[str, Any], schema_path: Path) -> list[str]:
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


def _canonical_bytes(document: Mapping[str, Any], excluded_key: str) -> bytes:
    payload = {key: value for key, value in document.items() if key != excluded_key}
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256(document: Mapping[str, Any], excluded_key: str) -> str:
    return hashlib.sha256(_canonical_bytes(document, excluded_key)).hexdigest()


def compute_extension_digest(extension: Mapping[str, Any]) -> str:
    return _sha256(extension, "extension_digest")


def verify_extension_digest(extension: Mapping[str, Any]) -> bool:
    metadata = extension.get("extension_digest")
    return (
        isinstance(metadata, Mapping)
        and metadata.get("algorithm") == "sha256"
        and metadata.get("canonicalization") == "json-sort-keys-utf8-v1"
        and metadata.get("value") == compute_extension_digest(extension)
    )


def compute_lane_digest(lane: Mapping[str, Any]) -> str:
    return "sha256:" + _sha256(lane, "lane_digest")


def _lane_index(extension: Mapping[str, Any], errors: list[str]) -> dict[str, Mapping[str, Any]]:
    rows = extension.get("responsibility_lanes")
    if not isinstance(rows, list):
        errors.append("responsibility_lanes must be an array")
        return {}

    lanes: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            errors.append("responsibility_lanes entries must be objects")
            continue
        lane_id = row.get("lane_id")
        if not isinstance(lane_id, str) or not lane_id:
            errors.append("responsibility lane requires lane_id")
            continue
        if lane_id in lanes:
            errors.append(f"duplicate lane_id: {lane_id}")
            continue
        lanes[lane_id] = row
    return lanes


def _scope_errors(
    label: str,
    lane: Mapping[str, Any],
    effect_refs: Any,
) -> list[str]:
    errors: list[str] = []
    scope = lane.get("mutation_scope")
    if not isinstance(scope, Mapping):
        return [f"{label}: lane mutation_scope is invalid"]

    allowed = set(scope.get("allowed_refs", []))
    denied = set(scope.get("denied_refs", []))
    if allowed & denied:
        errors.append(
            f"{label}: lane scope cannot allow and deny the same refs: "
            + ", ".join(sorted(allowed & denied))
        )

    if not isinstance(effect_refs, list):
        return errors + [f"{label}: effect_refs must be an array"]

    effects = {ref for ref in effect_refs if isinstance(ref, str)}
    missing = effects - allowed
    forbidden = effects & denied
    if missing:
        errors.append(
            f"{label}: effect refs outside lane allowlist: "
            + ", ".join(sorted(missing))
        )
    if forbidden:
        errors.append(
            f"{label}: effect refs explicitly denied by lane: "
            + ", ".join(sorted(forbidden))
        )
    return errors


def semantic_errors(
    extension: Mapping[str, Any],
    vce_envelope: Mapping[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    lanes = _lane_index(extension, errors)
    if not lanes:
        return errors

    for lane_id, lane in lanes.items():
        if lane.get("lane_digest") != compute_lane_digest(lane):
            errors.append(f"{lane_id}: lane digest mismatch")

        scope = lane.get("mutation_scope")
        if isinstance(scope, Mapping):
            allowed = set(scope.get("allowed_refs", []))
            denied = set(scope.get("denied_refs", []))
            overlap = allowed & denied
            if overlap:
                errors.append(
                    f"{lane_id}: mutation scope overlaps allow/deny: "
                    + ", ".join(sorted(overlap))
                )

        depends_on = lane.get("depends_on", [])
        if isinstance(depends_on, list):
            for dependency in depends_on:
                if dependency == lane_id:
                    errors.append(f"{lane_id}: lane cannot depend on itself")
                elif dependency not in lanes:
                    errors.append(f"{lane_id}: unknown dependency lane {dependency}")

    active_lane_id = extension.get("active_lane_id")
    if active_lane_id not in lanes:
        errors.append(f"active_lane_id references unknown lane {active_lane_id}")

    next_action = extension.get("next_action")
    if isinstance(next_action, Mapping):
        next_lane_id = next_action.get("lane_id")
        next_lane = lanes.get(next_lane_id)
        if next_lane is None:
            errors.append(f"next_action references unknown lane {next_lane_id}")
        else:
            errors.extend(
                _scope_errors(
                    "next_action",
                    next_lane,
                    next_action.get("effect_refs"),
                )
            )
            if next_lane.get("status") in {"complete", "superseded"}:
                errors.append(
                    f"next_action cannot execute in {next_lane.get('status')} lane {next_lane_id}"
                )

    bindings = extension.get("event_bindings")
    seen_events: set[str] = set()
    bound_events: set[str] = set()
    if not isinstance(bindings, list):
        errors.append("event_bindings must be an array")
        bindings = []

    for binding in bindings:
        if not isinstance(binding, Mapping):
            errors.append("event_bindings entries must be objects")
            continue
        event_id = binding.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            errors.append("event binding requires event_id")
            continue
        if event_id in seen_events:
            errors.append(f"duplicate event binding: {event_id}")
            continue
        seen_events.add(event_id)
        bound_events.add(event_id)

        lane_id = binding.get("lane_id")
        lane = lanes.get(lane_id)
        if lane is None:
            errors.append(f"{event_id}: binding references unknown lane {lane_id}")
            continue
        errors.extend(_scope_errors(event_id, lane, binding.get("effect_refs")))

    if vce_envelope is not None:
        if extension.get("vce_envelope_id") != vce_envelope.get("envelope_id"):
            errors.append("vce_envelope_id does not match the supplied VCE envelope")

        event_rows = vce_envelope.get("operational_tail")
        known_events: dict[str, Mapping[str, Any]] = {}
        if isinstance(event_rows, list):
            for event in event_rows:
                if isinstance(event, Mapping) and isinstance(event.get("event_id"), str):
                    known_events[event["event_id"]] = event

        for event_id in bound_events:
            if event_id not in known_events:
                errors.append(f"event binding references unknown VCE event {event_id}")

        material_ids = {
            event_id
            for event_id, event in known_events.items()
            if event.get("event_type") in MATERIAL_EVENT_TYPES
        }
        missing_bindings = sorted(material_ids - bound_events)
        if missing_bindings:
            errors.append(
                "material VCE events missing responsibility-lane binding: "
                + ", ".join(missing_bindings)
            )

    requirements = extension.get("restore_requirements")
    required_lane_ids: set[str] = set()
    seen_check_ids: set[str] = set()
    if not isinstance(requirements, Mapping):
        errors.append("restore_requirements must be an object")
    else:
        if requirements.get("fail_closed") is not True:
            errors.append("responsibility-lane restore gate must fail closed")
        checks = requirements.get("required_lane_checks")
        if not isinstance(checks, list):
            errors.append("required_lane_checks must be an array")
        else:
            for check in checks:
                if not isinstance(check, Mapping):
                    errors.append("required_lane_checks entries must be objects")
                    continue
                check_id = check.get("check_id")
                lane_id = check.get("lane_id")
                if not isinstance(check_id, str) or not check_id:
                    errors.append("lane check requires check_id")
                    continue
                if check_id in seen_check_ids:
                    errors.append(f"duplicate lane check id: {check_id}")
                seen_check_ids.add(check_id)
                if lane_id not in lanes:
                    errors.append(f"{check_id}: unknown lane {lane_id}")
                elif isinstance(lane_id, str):
                    required_lane_ids.add(lane_id)

    must_revalidate = {
        lane_id
        for lane_id, lane in lanes.items()
        if lane.get("status") != "superseded"
    }
    missing_lane_checks = sorted(must_revalidate - required_lane_ids)
    if missing_lane_checks:
        errors.append(
            "non-superseded lanes missing source revalidation: "
            + ", ".join(missing_lane_checks)
        )

    return errors


def restore_state(
    extension: Mapping[str, Any],
    restore_results: Mapping[str, Any] | None,
) -> str:
    if restore_results is None:
        return "BLOCKED"
    if schema_errors(restore_results, RESTORE_RESULTS_SCHEMA_PATH):
        return "BLOCKED"
    if restore_results.get("extension_id") != extension.get("extension_id"):
        return "BLOCKED"

    lanes_errors: list[str] = []
    lanes = _lane_index(extension, lanes_errors)
    if lanes_errors:
        return "BLOCKED"

    requirements = extension.get("restore_requirements")
    if not isinstance(requirements, Mapping):
        return "BLOCKED"
    required_checks = requirements.get("required_lane_checks")
    if not isinstance(required_checks, list):
        return "BLOCKED"

    rows = restore_results.get("lane_checks")
    if not isinstance(rows, list):
        return "BLOCKED"

    results: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            return "BLOCKED"
        check_id = row.get("check_id")
        if not isinstance(check_id, str) or check_id in results:
            return "BLOCKED"
        results[check_id] = row

    has_pending = False
    for requirement in required_checks:
        if not isinstance(requirement, Mapping):
            return "BLOCKED"
        check_id = requirement.get("check_id")
        lane_id = requirement.get("lane_id")
        result = results.get(check_id)
        lane = lanes.get(lane_id)
        if result is None or lane is None:
            return "BLOCKED"
        if result.get("lane_id") != lane_id:
            return "BLOCKED"

        status = result.get("status")
        if status == "pending":
            has_pending = True
            continue
        if status in {"failed", "conflict"}:
            return "BLOCKED"
        if status != "passed":
            return "BLOCKED"

        if result.get("conflict_refs"):
            return "BLOCKED"
        if result.get("observed_lane_digest") != lane.get("lane_digest"):
            return "BLOCKED"

        checked_refs = result.get("source_refs_checked")
        source_refs = lane.get("source_refs")
        if not isinstance(checked_refs, list) or not isinstance(source_refs, list):
            return "BLOCKED"
        if not set(source_refs) <= set(checked_refs):
            return "BLOCKED"

    return "REVIEW_REQUIRED" if has_pending else "PASSED"


def rlc_decision(
    extension: Mapping[str, Any],
    restore_results: Mapping[str, Any] | None = None,
    vce_envelope: Mapping[str, Any] | None = None,
) -> str:
    if schema_errors(extension, ENVELOPE_SCHEMA_PATH):
        return "BLOCKED"
    if not verify_extension_digest(extension):
        return "BLOCKED"
    if semantic_errors(extension, vce_envelope):
        return "BLOCKED"
    return restore_state(extension, restore_results)
