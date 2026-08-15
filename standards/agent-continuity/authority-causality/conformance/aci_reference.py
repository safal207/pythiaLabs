from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STATE_SCHEMA = ROOT / "schema" / "authority-state.schema.json"
TRANSITION_SCHEMA = ROOT / "schema" / "authority-transition.schema.json"
MUTATION_SCHEMA = ROOT / "schema" / "mutation-request.schema.json"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("document root must be object")
    return value


def schema_errors(document: Mapping[str, Any], schema_path: Path) -> list[str]:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    return [error.message for error in validator.iter_errors(dict(document))]


def _canonical_bytes(document: Mapping[str, Any], excluded: str) -> bytes:
    return json.dumps(
        {key: value for key, value in document.items() if key != excluded},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def compute_authority_digest(state: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(state, "authority_digest")).hexdigest()


def authority_digest_ref(state: Mapping[str, Any]) -> str:
    return "sha256:" + compute_authority_digest(state)


def sign_state(state: dict[str, Any]) -> None:
    state["authority_digest"]["value"] = compute_authority_digest(state)


def verify_state(state: Mapping[str, Any]) -> bool:
    digest = state.get("authority_digest")
    return (
        isinstance(digest, Mapping)
        and digest.get("algorithm") == "sha256"
        and digest.get("canonicalization") == "json-sort-keys-utf8-v1"
        and digest.get("value") == compute_authority_digest(state)
    )


def apply_transition(
    current: Mapping[str, Any] | None,
    transition: Mapping[str, Any],
) -> tuple[str, dict[str, Any] | None]:
    if schema_errors(transition, TRANSITION_SCHEMA):
        return "BLOCKED", None

    kind = transition["kind"]

    if current is None:
        if kind != "assign":
            return "BLOCKED", None
        if transition["expected_previous_authority_digest"] is not None:
            return "BLOCKED", None
        if transition["expected_previous_epoch"] != -1:
            return "BLOCKED", None
        if transition["from_owner_ref"] is not None:
            return "BLOCKED", None
        if transition["to_owner_ref"] is None or transition["new_epoch"] != 0:
            return "BLOCKED", None
        predecessor = None
    else:
        if schema_errors(current, STATE_SCHEMA) or not verify_state(current):
            return "BLOCKED", None
        if current["resource_ref"] != transition["resource_ref"]:
            return "BLOCKED", None
        if transition["expected_previous_authority_digest"] != authority_digest_ref(current):
            return "BLOCKED", None
        if transition["expected_previous_epoch"] != current["authority_epoch"]:
            return "BLOCKED", None
        if transition["from_owner_ref"] != current["owner_ref"]:
            return "BLOCKED", None
        if transition["new_epoch"] != current["authority_epoch"] + 1:
            return "BLOCKED", None
        predecessor = authority_digest_ref(current)

    if kind in {"assign", "transfer", "delegate"}:
        owner = transition["to_owner_ref"]
        if not owner:
            return "BLOCKED", None
        status = "active"
    elif kind == "revoke":
        if current is None or transition["to_owner_ref"] is not None:
            return "BLOCKED", None
        owner = current["owner_ref"]
        status = "revoked"
    elif kind == "expire":
        if current is None or transition["to_owner_ref"] is not None:
            return "BLOCKED", None
        owner = current["owner_ref"]
        status = "expired"
    else:
        return "BLOCKED", None

    new_state = {
        "schema_version": "aci-state/0.1",
        "resource_ref": transition["resource_ref"],
        "owner_ref": owner,
        "authority_epoch": transition["new_epoch"],
        "status": status,
        "scope": transition["new_scope"],
        "predecessor_digest": predecessor,
        "authority_digest": {
            "algorithm": "sha256",
            "canonicalization": "json-sort-keys-utf8-v1",
            "value": "0" * 64,
        },
    }
    sign_state(new_state)
    return "ACCEPTED", new_state


def mutation_decision(
    current_authority: Mapping[str, Any],
    mutation: Mapping[str, Any],
    current_state_digest: str | None = None,
) -> str:
    if schema_errors(current_authority, STATE_SCHEMA):
        return "BLOCKED"
    if schema_errors(mutation, MUTATION_SCHEMA):
        return "BLOCKED"
    if not verify_state(current_authority):
        return "BLOCKED"
    if current_authority["status"] != "active":
        return "BLOCKED"
    if mutation["resource_ref"] != current_authority["resource_ref"]:
        return "BLOCKED"
    if mutation["actor_ref"] != current_authority["owner_ref"]:
        return "BLOCKED"
    if mutation["presented_authority_epoch"] != current_authority["authority_epoch"]:
        return "BLOCKED"
    if mutation["presented_authority_digest"] != authority_digest_ref(current_authority):
        return "BLOCKED"
    if mutation["effect_ref"] not in current_authority["scope"]:
        return "BLOCKED"

    expected_state = mutation["expected_previous_state_digest"]
    new_state = mutation["new_state_digest"]
    if (expected_state is None) != (new_state is None):
        return "BLOCKED"
    if expected_state is not None:
        if current_state_digest is None or expected_state != current_state_digest:
            return "BLOCKED"

    return "ADMISSIBLE"


def detect_split_authority(states: list[Mapping[str, Any]]) -> bool:
    seen: set[tuple[str, int]] = set()
    for state in states:
        if schema_errors(state, STATE_SCHEMA) or not verify_state(state):
            return True
        if state["status"] != "active":
            continue
        key = (state["resource_ref"], state["authority_epoch"])
        if key in seen:
            return True
        seen.add(key)
    return False
