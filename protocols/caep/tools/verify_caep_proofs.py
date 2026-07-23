#!/usr/bin/env python3
"""Cryptographically verify CAEP F3+ action-record proofs.

The semantic engine stays standard-library-only. This verifier adds Ed25519
verification using the optional ``cryptography`` package and a separately
supplied public keyset.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
from pathlib import Path
from typing import Any

from caep_canonical import (
    CANONICALIZATION,
    CanonicalizationError,
    canonical_bytes,
    record_payload,
    strict_json_load,
)
from validate_caep_strict import validate_packet

try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
except ImportError:  # pragma: no cover
    InvalidSignature = Exception
    Ed25519PublicKey = None

ACTION_ROLES = {
    "authorization": "policy_decision_point",
    "dispatch": "enforcement_point",
    "outcome": "independent_observer",
    "recovery": "incident_controller",
}
ALLOWED_AUTHORITY_ROLES = set(ACTION_ROLES.values())
REQUIRED_PROOF_FIELDS = {"scheme", "key_id", "value"}
PROOF_SCHEME = f"Ed25519+{CANONICALIZATION}"
HIGH_EVIDENCE_LEVELS = {"F3", "F4", "F5"}
B64URL_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def _non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _b64url_decode(value: str) -> bytes:
    if not isinstance(value, str) or not value:
        raise ValueError("base64url value must be a non-empty string")
    if not B64URL_RE.fullmatch(value):
        raise ValueError("base64url value contains unsupported characters")
    padding = "=" * (-len(value) % 4)
    try:
        return base64.urlsafe_b64decode(value + padding)
    except Exception as exc:
        raise ValueError("invalid base64url value") from exc


def load_keyset(path: Path) -> dict[str, dict[str, Any]]:
    raw = strict_json_load(path)
    if not isinstance(raw, dict) or raw.get("caep_keyset_version") != "0.1.0":
        raise ValueError("keyset must declare caep_keyset_version 0.1.0")
    keys = raw.get("keys")
    if not isinstance(keys, list) or not keys:
        raise ValueError("keyset.keys must be a non-empty array")

    indexed: dict[str, dict[str, Any]] = {}
    public_key_owners: dict[bytes, tuple[str, str]] = {}
    for index, entry in enumerate(keys):
        if not isinstance(entry, dict):
            raise ValueError(f"keys[{index}] must be an object")
        required = {"key_id", "scheme", "issuer", "authority_role", "public_key"}
        missing = sorted(required - entry.keys())
        if missing:
            raise ValueError(f"keys[{index}] missing fields: {', '.join(missing)}")
        if set(entry) != required:
            extras = sorted(set(entry) - required)
            raise ValueError(f"keys[{index}] contains unsupported fields: {extras}")
        if entry.get("scheme") != "Ed25519":
            raise ValueError(f"keys[{index}].scheme must be Ed25519")

        key_id = _non_empty_string(entry.get("key_id"), f"keys[{index}].key_id")
        issuer = _non_empty_string(entry.get("issuer"), f"keys[{index}].issuer")
        authority_role = _non_empty_string(
            entry.get("authority_role"), f"keys[{index}].authority_role"
        )
        if authority_role not in ALLOWED_AUTHORITY_ROLES:
            raise ValueError(
                f"keys[{index}].authority_role must be one of "
                f"{sorted(ALLOWED_AUTHORITY_ROLES)}"
            )
        if key_id in indexed:
            raise ValueError(f"duplicate key_id: {key_id}")

        raw_key = _b64url_decode(entry.get("public_key"))
        if len(raw_key) != 32:
            raise ValueError(f"keys[{index}].public_key must decode to 32 bytes")
        owner = public_key_owners.get(raw_key)
        current = (issuer, authority_role)
        if owner and owner != current:
            raise ValueError(
                "the same public key cannot represent different issuers or authority roles"
            )
        public_key_owners[raw_key] = current
        indexed[key_id] = {**entry, "_raw_public_key": raw_key}
    return indexed


def verify_action_proofs(
    packet: Any, keyset: dict[str, dict[str, Any]]
) -> list[str]:
    errors: list[str] = []
    if Ed25519PublicKey is None:
        return [
            "cryptography package is required for Ed25519 verification; "
            "install protocols/caep/requirements-crypto.txt"
        ]
    if not isinstance(packet, dict):
        return ["packet must be a JSON object"]
    records = packet.get("records")
    if not isinstance(records, list):
        return ["records must be an array"]

    used_keys: dict[str, str] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        record_type = record.get("record_type")
        required_role = ACTION_ROLES.get(record_type)
        if not required_role:
            continue
        record_id = record.get("record_id", "<unknown>")
        proof = record.get("integrity_proof")
        if not isinstance(proof, dict):
            errors.append(f"{record_id}: missing integrity_proof")
            continue
        missing = sorted(REQUIRED_PROOF_FIELDS - proof.keys())
        if missing:
            errors.append(
                f"{record_id}: integrity_proof missing fields: {', '.join(missing)}"
            )
            continue
        if set(proof) != REQUIRED_PROOF_FIELDS:
            extras = sorted(set(proof) - REQUIRED_PROOF_FIELDS)
            errors.append(
                f"{record_id}: integrity_proof contains unsupported fields: {extras}"
            )
            continue
        if proof.get("scheme") != PROOF_SCHEME:
            errors.append(f"{record_id}: proof scheme must be {PROOF_SCHEME}")
            continue

        key_id = proof.get("key_id")
        if not isinstance(key_id, str) or not key_id:
            errors.append(f"{record_id}: proof key_id must be non-empty")
            continue
        key = keyset.get(key_id)
        if not key:
            errors.append(f"{record_id}: unknown key_id {key_id!r}")
            continue
        if key.get("issuer") != record.get("issuer"):
            errors.append(f"{record_id}: proof key issuer does not match record issuer")
        if key.get("authority_role") != required_role:
            errors.append(
                f"{record_id}: authority role must be {required_role}, "
                f"got {key.get('authority_role')!r}"
            )
        previous_role = used_keys.get(key_id)
        if previous_role and previous_role != required_role:
            errors.append(
                f"{record_id}: key {key_id!r} is reused across authority roles"
            )
        used_keys[key_id] = required_role

        try:
            signature = _b64url_decode(proof.get("value"))
            if len(signature) != 64:
                raise ValueError("Ed25519 signature must decode to 64 bytes")
            public_key = Ed25519PublicKey.from_public_bytes(key["_raw_public_key"])
            public_key.verify(signature, canonical_bytes(record_payload(record)))
        except (ValueError, CanonicalizationError) as exc:
            errors.append(f"{record_id}: invalid proof encoding: {exc}")
        except InvalidSignature:
            errors.append(f"{record_id}: Ed25519 signature verification failed")

    return errors


def verify_packet(
    packet: Any, keyset: dict[str, dict[str, Any]]
) -> tuple[list[str], list[str]]:
    level = packet.get("evidence_level") if isinstance(packet, dict) else None
    proof_errors = verify_action_proofs(packet, keyset)
    level_errors: list[str] = []
    if level not in HIGH_EVIDENCE_LEVELS:
        level_errors.append(
            "cryptographic verification requires evidence_level F3, F4, or F5"
        )

    proofs_verified = not proof_errors and not level_errors
    semantic_errors, warnings = validate_packet(
        packet, proofs_verified=proofs_verified
    )
    return list(dict.fromkeys(semantic_errors + proof_errors + level_errors)), warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--keyset", required=True, type=Path)
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args(argv)

    packet: Any = None
    try:
        packet = strict_json_load(args.packet)
        keyset = load_keyset(args.keyset)
        errors, warnings = verify_packet(packet, keyset)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors, warnings = [str(exc)], []

    result = {
        "valid": not errors,
        "episode_ref": packet.get("episode_ref") if isinstance(packet, dict) else None,
        "errors": errors,
        "warnings": warnings,
    }
    if args.json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("VERIFIED" if not errors else "INVALID")
        for warning in warnings:
            print(f"warning: {warning}")
        for error in errors:
            print(f"error: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
