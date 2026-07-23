#!/usr/bin/env python3
"""Strict CAEP validation profile.

Adds causal hand-off, time ordering, and honest evidence-level checks on top of
the base semantic validator.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_caep import load_packet, validate_packet as base_validate

HIGH_EVIDENCE_LEVELS = {"F3", "F4", "F5"}


def _time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _record(records: list[dict[str, Any]], kind: str) -> dict[str, Any] | None:
    found = [item for item in records if item.get("record_type") == kind]
    return found[0] if len(found) == 1 else None


def _sequence_key(record: dict[str, Any]) -> int:
    value = record.get("sequence")
    if isinstance(value, int) and not isinstance(value, bool) and value >= 1:
        return value
    return 10**12


def _parent(child, parent, label: str, errors: list[str]) -> None:
    if not child or not parent:
        return
    parents = child.get("causal_parent_record_ids")
    if not isinstance(parents, list) or parent.get("record_id") not in parents:
        errors.append(f"{label} must reference causal parent {parent.get('record_id')!r}")


def _ordered(first: Any, second: Any, label: str, errors: list[str]) -> None:
    left, right = _time(first), _time(second)
    if left is not None and right is not None and left > right:
        errors.append(f"time ordering violation: {label}")


def validate_packet(
    packet: Any, *, proofs_verified: bool = False
) -> tuple[list[str], list[str]]:
    errors, warnings = base_validate(packet)
    if not isinstance(packet, dict) or not isinstance(packet.get("records"), list):
        return errors, warnings

    records = [item for item in packet["records"] if isinstance(item, dict)]
    intent = _record(records, "intent")
    auth = _record(records, "authorization")
    dispatch = _record(records, "dispatch")
    outcome = _record(records, "outcome")
    recovery = _record(records, "recovery")

    _parent(auth, intent, "authorization", errors)
    _parent(dispatch, auth, "dispatch", errors)
    _parent(outcome, dispatch, "outcome", errors)
    _parent(recovery, outcome, "recovery", errors)

    previous = None
    previous_id = None
    for item in sorted(records, key=_sequence_key):
        current = _time(item.get("observed_at"))
        if previous is not None and current is not None and previous > current:
            errors.append(
                f"observed_at is not monotonic: {previous_id!r} occurs after "
                f"{item.get('record_id')!r}"
            )
        if current is not None:
            previous, previous_id = current, item.get("record_id")

    if intent:
        _ordered(intent.get("valid_time"), intent.get("transaction_time"),
                 "intent.valid_time <= intent.transaction_time", errors)
    if intent and auth:
        _ordered(intent.get("transaction_time"), auth.get("observed_at"),
                 "intent.transaction_time <= authorization.observed_at", errors)
    if auth and dispatch:
        _ordered(auth.get("observed_at"), dispatch.get("dispatch_time"),
                 "authorization.observed_at <= dispatch.dispatch_time", errors)
    if dispatch and outcome:
        _ordered(dispatch.get("dispatch_time"), outcome.get("observed_at"),
                 "dispatch.dispatch_time <= outcome.observed_at", errors)
    if outcome and recovery:
        _ordered(outcome.get("observed_at"), recovery.get("observed_at"),
                 "outcome.observed_at <= recovery.observed_at", errors)

    level = packet.get("evidence_level")
    if level in HIGH_EVIDENCE_LEVELS and not proofs_verified:
        errors.append(
            f"{level} cannot be established by semantic validation alone; "
            "verify required proofs against a trusted keyset"
        )

    return list(dict.fromkeys(errors)), list(dict.fromkeys(warnings))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args(argv)
    try:
        packet = load_packet(args.packet)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}")
        return 2
    errors, warnings = validate_packet(packet)
    result = {"valid": not errors, "errors": errors, "warnings": warnings}
    if args.json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("VALID" if not errors else "INVALID")
        for warning in warnings:
            print(f"warning: {warning}")
        for error in errors:
            print(f"error: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
