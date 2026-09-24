"""Exact-target pytest configuration hardening for Lotus conformance."""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

import lotus_family_runtime_v2 as previous
from lotus_family_schema import (
    DRIFT,
    PASS,
    UNKNOWN,
    load_manifest,
    manifest_invalid,
)


def _explicit_python_targets(
    discovery: Mapping[str, Any],
) -> list[PurePosixPath]:
    """Return safe repository-relative Python targets from contains_any."""
    if discovery.get("strategy") != "contains_any":
        return []
    values = discovery.get("contains_any")
    if not isinstance(values, list):
        return []

    targets: set[PurePosixPath] = set()
    for value in values:
        if not isinstance(value, str):
            continue
        try:
            tokens = shlex.split(value)
        except ValueError:
            continue
        for token in tokens:
            normalized = token.split("::", 1)[0]
            if not normalized.lower().endswith(".py"):
                continue
            target = PurePosixPath(normalized)
            if target.is_absolute() or ".." in target.parts:
                continue
            targets.add(target)
    return sorted(targets, key=lambda path: path.as_posix())


def _target_ancestor_config_paths(
    discovery: Mapping[str, Any],
) -> list[str]:
    """List pytest config candidates below root and above explicit targets."""
    directories: set[PurePosixPath] = set()
    for target in _explicit_python_targets(discovery):
        parent = target.parent
        while parent != PurePosixPath("."):
            directories.add(parent)
            parent = parent.parent

    names = tuple(
        PurePosixPath(path).name for path in previous._PYTEST_CONFIG_PATHS
    )
    candidates = {
        (directory / name).as_posix()
        for directory in directories
        for name in names
    }
    return sorted(candidates)


def _audit_target_ancestor_configuration(
    repository_root: Path,
    discovery: Mapping[str, Any],
    files: list[dict[str, str]],
) -> tuple[list[str], list[str]]:
    """Hash and block pytest configs found along explicit-target ancestors."""
    observed: list[str] = []
    blockers: list[str] = []
    for relative_path in _target_ancestor_config_paths(discovery):
        candidate = repository_root / relative_path
        if not candidate.exists() and not candidate.is_symlink():
            continue
        observed.append(relative_path)
        text, error = previous.read_file(repository_root, relative_path, files)
        if error is not None or text is None:
            blockers.append(f"{relative_path}: {error or 'unreadable'}")
            continue
        basename = PurePosixPath(relative_path).name
        if previous._activates_pytest_configuration(basename, text):
            blockers.append(relative_path)
    return observed, blockers


def audit_repository(
    manifest: Mapping[str, Any],
    *,
    repository_id: str,
    snapshot_root: Path,
    repository_ref: str,
    commit_sha: str,
) -> dict[str, Any]:
    """Extend v2 with config discovery rooted at explicit Python targets."""
    audit = previous.audit_repository(
        manifest,
        repository_id=repository_id,
        snapshot_root=snapshot_root,
        repository_ref=repository_ref,
        commit_sha=commit_sha,
    )
    if audit.get("outcome") != PASS:
        return audit

    config = previous.repository_config(manifest, repository_id)
    if config is None:
        return audit
    discovery = config.get("ci_discovery", {})
    if not isinstance(discovery, Mapping):
        return audit
    if not _explicit_python_targets(discovery):
        return audit

    repository_root = (
        snapshot_root.resolve() / str(config["snapshot_dir"])
    ).resolve()
    files = list(audit.get("files", []))
    observed, blockers = _audit_target_ancestor_configuration(
        repository_root,
        discovery,
        files,
    )
    if not observed and not blockers:
        return audit

    check = next(
        (
            row
            for row in audit.get("checks", [])
            if row.get("check_id") == "pytest_configuration"
        ),
        None,
    )
    if check is None:
        check = {
            "check_id": "pytest_configuration",
            "outcome": PASS,
            "paths": [],
            "blocked_paths": [],
            "detail": "pytest configuration evidence was evaluated",
        }
        audit.setdefault("checks", []).append(check)

    check["paths"] = list(
        dict.fromkeys([*check.get("paths", []), *observed])
    )
    check["blocked_paths"] = list(
        dict.fromkeys([*check.get("blocked_paths", []), *blockers])
    )
    audit["files"] = previous._deduplicate_files(files)

    if blockers:
        check["outcome"] = DRIFT
        check["detail"] = (
            "active, unreadable, or executable pytest configuration can alter "
            "test collection or selection"
        )
        audit["outcome"] = DRIFT
        audit["reason_code"] = "LOTUS_CONTRACT_DRIFT"
        audit["detail"] = "non-conforming checks: pytest_configuration"
    return audit


def main(argv: list[str] | None = None) -> int:
    """Run the v3 auditor and write JSON evidence."""
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
