"""Runtime hardening overlay for Lotus Family conformance v0.1."""

from __future__ import annotations

import argparse
import json
import os
import re
import tomllib
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
    ".pytest.toml",
    "pytest.ini",
    ".pytest.ini",
    "pyproject.toml",
    "tox.ini",
    "setup.cfg",
)


_DEDICATED_PYTEST_CONFIGS = {
    "pytest.toml",
    ".pytest.toml",
    "pytest.ini",
    ".pytest.ini",
}


_MIX_CONFIG_PATHS = ("mix.exs", "test/test_helper.exs")


_MIX_PROJECT_COLLECTION_SETTING = re.compile(
    r"\b(?:test_paths|test_pattern)\s*:",
)


_EXUNIT_SELECTION_SETTING = re.compile(
    r"\bExUnit\.(?:start|configure)\s*\([^)]*\b(?:exclude|include)\s*:",
    re.DOTALL,
)


def _has_meaningful_lines(text: str) -> bool:
    """Return true when a dedicated pytest config is not empty/comment-only."""
    return any(
        stripped and not stripped.startswith(("#", ";"))
        for line in text.splitlines()
        if (stripped := line.strip())
    )


def _is_conftest(path: str) -> bool:
    """Return true for a repository-relative pytest conftest path."""
    return path == "conftest.py" or path.endswith("/conftest.py")


def _contains_python_test_reference(value: object) -> bool:
    """Return true when a discovery value names a Python test target."""
    if not isinstance(value, str):
        return False
    for token in value.split():
        normalized = token.strip("'\"").split("::", 1)[0]
        if normalized.lower().endswith(".py"):
            return True
    return False


def _requires_pytest_configuration_audit(
    discovery: Mapping[str, Any],
) -> bool:
    """Identify discovery strategies whose execution is affected by pytest config."""
    strategy = discovery.get("strategy")
    if strategy == "pytest_default_discovery":
        return True
    if strategy != "contains_any":
        return False
    candidates = discovery.get("contains_any")
    return isinstance(candidates, list) and any(
        _contains_python_test_reference(candidate) for candidate in candidates
    )


def _requires_mix_configuration_audit(
    discovery: Mapping[str, Any],
) -> bool:
    """Identify discovery strategies affected by Mix test configuration."""
    strategy = discovery.get("strategy")
    if strategy == "mix_default_discovery":
        return True
    if strategy != "contains_any":
        return False
    candidates = discovery.get("contains_any")
    return isinstance(candidates, list) and any(
        isinstance(candidate, str)
        and candidate.split("::", 1)[0].strip("'\"").lower().endswith(".exs")
        for candidate in candidates
    )


def _activates_pytest_configuration(path: str, text: str) -> bool:
    """Detect config scopes or hooks that can alter default pytest collection."""
    if _is_conftest(path):
        return True
    if path in _DEDICATED_PYTEST_CONFIGS:
        return _has_meaningful_lines(text)
    if path == "pyproject.toml":
        try:
            document = tomllib.loads(text)
        except tomllib.TOMLDecodeError:
            return True
        tool = document.get("tool")
        return isinstance(tool, dict) and "pytest" in tool
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


def _discover_conftest_paths(repository_root: Path) -> list[str]:
    """Find conftest files deterministically without traversing symlink dirs."""
    discovered: list[str] = []
    for directory, dirnames, filenames in os.walk(
        repository_root,
        followlinks=False,
    ):
        directory_path = Path(directory)
        dirnames[:] = sorted(
            name
            for name in dirnames
            if not (directory_path / name).is_symlink()
        )
        if "conftest.py" not in filenames:
            continue
        candidate = directory_path / "conftest.py"
        try:
            relative_path = candidate.relative_to(repository_root).as_posix()
        except ValueError:
            continue
        discovered.append(relative_path)
    return sorted(set(discovered))


def _audit_pytest_configuration(
    repository_root: Path,
    files: list[dict[str, str]],
) -> tuple[list[str], list[str]]:
    """Hash pytest configs and fail closed on active, unreadable, or hook files."""
    observed: list[str] = []
    blockers: list[str] = []
    candidate_paths = (
        *_PYTEST_CONFIG_PATHS,
        *_discover_conftest_paths(repository_root),
    )
    for relative_path in dict.fromkeys(candidate_paths):
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


def _activates_mix_configuration(path: str, text: str) -> bool:
    """Detect Mix and ExUnit settings that can hide contract tests."""
    if path == "mix.exs":
        return bool(_MIX_PROJECT_COLLECTION_SETTING.search(text))
    if path == "test/test_helper.exs":
        return bool(_EXUNIT_SELECTION_SETTING.search(text))
    return False


def _audit_mix_configuration(
    repository_root: Path,
    files: list[dict[str, str]],
) -> tuple[list[str], list[str]]:
    """Hash known Mix configs and block collection-affecting settings."""
    observed: list[str] = []
    blockers: list[str] = []
    for relative_path in _MIX_CONFIG_PATHS:
        candidate = repository_root / relative_path
        if not candidate.exists() and not candidate.is_symlink():
            continue
        observed.append(relative_path)
        text, error = read_file(repository_root, relative_path, files)
        if error is not None or text is None:
            blockers.append(f"{relative_path}: {error or 'unreadable'}")
            continue
        if _activates_mix_configuration(relative_path, text):
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
    if not isinstance(discovery, Mapping):
        return audit

    repository_root = (
        snapshot_root.resolve() / str(config["snapshot_dir"])
    ).resolve()
    files = list(audit.get("files", []))
    all_blockers: list[str] = []

    if _requires_pytest_configuration_audit(discovery):
        observed, blockers = _audit_pytest_configuration(
            repository_root, files
        )
        check = {
            "check_id": "pytest_configuration",
            "outcome": DRIFT if blockers else PASS,
            "paths": observed,
            "blocked_paths": blockers,
            "detail": (
                "active, unreadable, or executable pytest configuration can "
                "alter test collection or selection"
                if blockers
                else "known pytest configuration and conftest files were "
                "absent or hashed without an active pytest scope"
            ),
        }
        audit.setdefault("checks", []).append(check)
        all_blockers.extend(blockers)

    if _requires_mix_configuration_audit(discovery):
        observed, blockers = _audit_mix_configuration(repository_root, files)
        check = {
            "check_id": "mix_configuration",
            "outcome": DRIFT if blockers else PASS,
            "paths": observed,
            "blocked_paths": blockers,
            "detail": (
                "active, unreadable, or collection-changing Mix "
                "configuration can alter test discovery or selection"
                if blockers
                else "known Mix project and test-helper configuration was "
                "absent or hashed without collection-changing settings"
            ),
        }
        audit.setdefault("checks", []).append(check)
        all_blockers.extend(blockers)

    audit["files"] = _deduplicate_files(files)

    if all_blockers:
        audit["outcome"] = DRIFT
        audit["reason_code"] = "LOTUS_CONTRACT_DRIFT"
        failed_checks = [
            row["check_id"]
            for row in audit["checks"]
            if row.get("outcome") == DRIFT
        ]
        audit["detail"] = "non-conforming checks: " + ", ".join(
            sorted(set(failed_checks))
        )
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
