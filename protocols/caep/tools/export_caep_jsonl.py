#!/usr/bin/env python3
"""Export and verify CAEP packets as digest-bound JSON Lines.

JSONL transport verification checks canonical record digests and packet
semantics. It does not replace F3 signature verification.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from caep_canonical import (
    canonical_bytes,
    record_digest,
    strict_json_load,
    strict_json_loads,
)
from validate_caep import validate_packet


def export_lines(packet: dict[str, Any]) -> list[bytes]:
    errors, _warnings = validate_packet(packet)
    if errors:
        raise ValueError("packet is not semantically valid: " + "; ".join(errors))
    records = packet["records"]
    header = {
        "line_type": "caep.header",
        "caep_version": packet["caep_version"],
        "episode_ref": packet["episode_ref"],
        "evidence_level": packet["evidence_level"],
        "record_count": len(records),
    }
    lines = [canonical_bytes(header)]
    for record in records:
        lines.append(
            canonical_bytes(
                {
                    "line_type": "caep.record",
                    "episode_ref": packet["episode_ref"],
                    "sequence": record["sequence"],
                    "record_digest": record_digest(record),
                    "record": record,
                }
            )
        )
    return lines


def write_jsonl(packet: dict[str, Any], output: Path) -> None:
    output.write_bytes(b"\n".join(export_lines(packet)) + b"\n")


def verify_jsonl(path: Path) -> tuple[list[str], dict[str, Any] | None]:
    errors: list[str] = []
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    if not raw_lines:
        return ["JSONL file is empty"], None
    try:
        parsed = [strict_json_loads(line) for line in raw_lines]
    except (json.JSONDecodeError, ValueError) as exc:
        return [f"invalid JSONL: {exc}"], None

    header = parsed[0]
    if not isinstance(header, dict) or header.get("line_type") != "caep.header":
        return ["first line must be caep.header"], None
    envelopes = parsed[1:]
    if header.get("record_count") != len(envelopes):
        errors.append("record_count does not match number of record lines")

    records: list[dict[str, Any]] = []
    expected_sequence = 1
    for index, envelope in enumerate(envelopes, start=2):
        if not isinstance(envelope, dict) or envelope.get("line_type") != "caep.record":
            errors.append(f"line {index} must be caep.record")
            continue
        record = envelope.get("record")
        if not isinstance(record, dict):
            errors.append(f"line {index}.record must be an object")
            continue
        if envelope.get("episode_ref") != header.get("episode_ref"):
            errors.append(f"line {index} episode_ref does not match header")
        if envelope.get("sequence") != expected_sequence:
            errors.append(f"line {index} sequence is not contiguous")
        expected_sequence += 1
        if envelope.get("record_digest") != record_digest(record):
            errors.append(f"line {index} record_digest does not match record")
        records.append(record)

    packet = {
        "caep_version": header.get("caep_version"),
        "episode_ref": header.get("episode_ref"),
        "evidence_level": header.get("evidence_level"),
        "records": records,
    }
    semantic_errors, _warnings = validate_packet(packet)
    errors.extend(semantic_errors)
    return list(dict.fromkeys(errors)), packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("packet", type=Path)
    export_parser.add_argument("output", type=Path)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("jsonl", type=Path)
    args = parser.parse_args(argv)

    if args.command == "export":
        packet = strict_json_load(args.packet)
        write_jsonl(packet, args.output)
        print(args.output)
        return 0

    errors, _packet = verify_jsonl(args.jsonl)
    print("VALID" if not errors else "INVALID")
    for error in errors:
        print(f"error: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
