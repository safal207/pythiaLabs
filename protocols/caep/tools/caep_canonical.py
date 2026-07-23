#!/usr/bin/env python3
"""Canonicalization helpers for CAEP signed records.

CAEP-JCS-INT-1 is a deliberately narrow RFC 8785-compatible profile for the
CAEP v0.1 data domain. It rejects floating-point numbers, unsafe integers,
non-ASCII object member names, duplicate members, and non-finite JSON values so
independent runtimes do not silently sign different byte sequences.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

CANONICALIZATION = "caep-jcs-int-v1"
MAX_SAFE_INTEGER = (1 << 53) - 1


class CanonicalizationError(ValueError):
    """Raised when a value is outside the CAEP canonical JSON domain."""


def _check_domain(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool)):
        if isinstance(value, str):
            try:
                value.encode("utf-8")
            except UnicodeEncodeError as exc:
                raise CanonicalizationError(
                    f"{path} contains an invalid Unicode surrogate"
                ) from exc
        return
    if isinstance(value, int):
        if isinstance(value, bool):
            return
        if abs(value) > MAX_SAFE_INTEGER:
            raise CanonicalizationError(
                f"{path} integer is outside the interoperable JSON range"
            )
        return
    if isinstance(value, float):
        raise CanonicalizationError(
            f"{path} contains a floating-point number; "
            "CAEP-JCS-INT-1 permits integers only"
        )
    if isinstance(value, list):
        for index, item in enumerate(value):
            _check_domain(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalizationError(f"{path} contains a non-string object key")
            if not key.isascii():
                raise CanonicalizationError(
                    f"{path} contains non-ASCII object member name {key!r}"
                )
            _check_domain(key, f"{path}.<key>")
            _check_domain(item, f"{path}.{key}")
        return
    raise CanonicalizationError(
        f"{path} contains unsupported type {type(value).__name__}"
    )


def canonical_bytes(value: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes for the CAEP canonical domain."""
    _check_domain(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def record_payload(record: dict[str, Any]) -> dict[str, Any]:
    """Return the record fields covered by an integrity proof."""
    return {key: value for key, value in record.items() if key != "integrity_proof"}


def sha256_digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def record_payload_digest(record: dict[str, Any]) -> str:
    """Digest the signed payload, excluding the proof envelope."""
    return sha256_digest(record_payload(record))


def record_digest(record: dict[str, Any]) -> str:
    """Digest the complete transport record, including its proof envelope."""
    return sha256_digest(record)


def strict_json_loads(text: str) -> Any:
    """Parse JSON and reject duplicate members and non-finite constants."""

    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON member: {key}")
            result[key] = value
        return result

    def reject_constant(value: str) -> Any:
        raise ValueError(f"non-finite JSON constant is not permitted: {value}")

    return json.loads(
        text,
        object_pairs_hook=no_duplicates,
        parse_constant=reject_constant,
    )


def strict_json_load(path) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return strict_json_loads(handle.read())
