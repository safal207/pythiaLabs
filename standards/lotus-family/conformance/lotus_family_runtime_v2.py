"""Runtime hardening overlay for Lotus Family conformance v0.1."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping

import lotus_family_runtime as previous
from lotus_family_schema import (
    DRIFT,
    PASS,
    UNKNOWN,
    load_manifest,
    manifest_invalid,
    read_file,
    repository_config,
)


_PYTEST_CONFIG_PATHS = (
    "pytest.toml",
    "pytest.ini",
    "pyproject.toml",
    "tox.ini",
    "setup.cfg",
)


def _has_meaningful_lines(text: str) -> bool:
    """Return true when a dedicated pytest config is not empty/comment-only."""
    return any(
        stripped and not stripped.startswith(("#", ";"))
        for line in text.splitlines()
        if (stripped := line.strip())
    )


def _activates_pytest_configuration(path: str, text: str) -> bool:
    """Detect config scopes that can alter default pytest collection."""
    if path in {"pytest.toml", "pytest.ini"}:
        return _has_meaningful_lines(text)
    if path == "pyproject.toml":
        return bool(
            re.search(
                r"(?mi)^\s*\[\s*tool\.pytest\.ini_options\s*\]\s*$",
                text,
            )
        )
    if path == "tox.ini":
        return bool(re.search(r"(?mi)^\s*\[\s*pytest\s*\]\s*$", text))
    if path == "setup.cfg":
        return bool(
            re.search(
                r"(?mi)^\s*\[\s*(?:tool:pytest|pytest)\s*\]\s*$",
                text,
            )
        )
    return False


def _audit_pytest_configuration(
    repository_root: Path,
    files: list[dict[str, str]],
) -> tuple[list[str], list[str]]:
    """Hash known pytest configs and return active or unreadable blockers."""
    observed: list[str] = []
    blockers: list[str] = []
    for relative_path in _PYTEST_CONFIG_PATHS:
        candidate = repository_root / relative_path
        if not candidate.exists() and not candidate.is_symlink():
            continue
        observed.append(relative_path)
        text, error = read_file(repository_root, relative_path, files)
        if error is not None or text is None:
            blockers.append(f"{relative_path}: {error or 'unreadable'}")
            continue
        if _activates_pytest_configuration(relative_path, text):
            blockers.append(relative_path)
    return observed, blockers


def _deduplicate_files(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Keep one evidence row per exact path and digest pair."""
    unique = {(row["path"], row["sha256"]): row for row in rows}
    return list(unique.values())


def audit_repository(
    manifest: Mapping[str, Any],
    *,
    repository_id: str,
    snapshot_root: Path,
    repository_ref: str,
    commit_sha: str,
) -> dict[str, Any]:
    """Audit a snapshot and fail closed on active pytest configuration."""
    audit = previous.audit_repository(
        manifest,
        repository_id=repository_id,
        snapshot_root=snapshot_root,
        repository_ref=repository_ref,
        commit_sha=commit_sha,
    )
    if audit.get("outcome") != PASS:
        return audit

    config = repository_config(manifest, repository_id)
    if config is None:
        return audit
    discovery = config.get("ci_discovery", {})
    if discovery.get("strategy") != "pytest_default_discovery":
        return audit

    repository_root = (
        snapshot_root.resolve() / str(config["snapshot_dir"])
    ).resolve()
    files = list(audit.get("files", []))
    observed, blockers = _audit_pytest_configuration(repository_root, files)
    check = {
        "check_id": "pytest_configuration",
        "outcome": DRIFT if blockers else PASS,
        "paths": observed,
        "blocked_paths": blockers,
        "detail": (
            "active or unreadable pytest configuration can alter default collection"
            if blockers
            else "known pytest configuration files were absent or hashed without an active pytest scope"
        ),
    }
    audit.setdefault("checks", []).append(check)
    audit["files"] = _deduplicate_files(files)

    if blockers:
        audit["outcome"] = DRIFT
        audit["reason_code"] = "LOTUS_CONTRACT_DRIFT"
        audit["detail"] = "non-conforming checks: pytest_configuration"
    return audit


def main(argv: list[str] | None = None) -> int:
    """Run the hardened command-line auditor and write JSON evidence."""
    parser = argparse.ArgumentParser(
        description=(
            "Audit one repository snapshot against the Lotus Family manifest."
        )
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--snapshot-root", type=Path, required=True)
    parser.add_argument("--repository-id", required=True)
    parser.add_argument("--repository-ref", required=True)
    parser.add_argument("--commit-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        audit = audit_repository(
            load_manifest(args.manifest),
            repository_id=args.repository_id,
            snapshot_root=args.snapshot_root,
            repository_ref=args.repository_ref,
            commit_sha=args.commit_sha,
        )
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        ValueError,
    ) as exc:
        audit = manifest_invalid(
            str(exc),
            args.repository_id,
            args.repository_ref,
            args.commit_sha,
            "",
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(audit, ensure_ascii=False, sort_keys=True))
    return {PASS: 0, DRIFT: 2, UNKNOWN: 3}.get(audit["outcome"], 3)


__all__ = ["audit_repository", "main"]
