"""Runtime hardening overlay for Lotus Family conformance v0.1."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

import lotus_family_runtime as previous
import tomllib
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


_PYTEST_SHADOW_PATHS = (
    "pytest.py",
    "pytest/__init__.py",
    "pytest/__main__.py",
)


_DEDICATED_PYTEST_CONFIGS = {
    "pytest.toml",
    ".pytest.toml",
    "pytest.ini",
    ".pytest.ini",
}


_MIX_CONFIG_PATHS = ("mix.exs", "test/test_helper.exs")


_MIX_PROJECT_DEFINITION = re.compile(
    r"(?m)^[ \t]*def[ \t]+project(?:[ \t]*\([ \t]*\))?[ \t]*"
    r"(?:(?P<block>do)\b|,[ \t]*do:[ \t]*)",
)


_MIX_PROJECT_KEY = re.compile(r"([A-Za-z_][A-Za-z0-9_?!]*)\s*:")


_MIX_SAFE_PROJECT_VALUE = re.compile(
    r"(?:"
    r":[A-Za-z_][A-Za-z0-9_?!@]*|"
    r'"(?:\\.|[^"\\])*"|'
    r"'(?:\\.|[^'\\])*'|"
    r"-?[0-9]+(?:\.[0-9]+)?|"
    r"true|false|nil"
    r")\Z"
)


_MIX_REQUIRE_FILE = re.compile(
    r'Code\.require_file\("(?P<path>[^"\\]+)",[ \t]*__DIR__\)'
)


_MIX_MODULE = re.compile(
    r"defmodule[ \t]+[A-Z][A-Za-z0-9_.]*[ \t]+do\b"
)


_MIX_USE_PROJECT = re.compile(r"use[ \t]+Mix\.Project\b")


_MIX_COLLECTION_KEYS = {"test_paths", "test_pattern"}


_MIX_SAFE_TEST_HELPER = re.compile(r"ExUnit\.start\s*\(\s*\)")


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
    if path in _PYTEST_SHADOW_PATHS:
        return True
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
        *_PYTEST_SHADOW_PATHS,
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


def _skip_elixir_space_and_comments(text: str, start: int) -> int:
    """Advance over whitespace and line comments outside an Elixir value."""
    index = start
    while index < len(text):
        if text[index].isspace():
            index += 1
            continue
        if text[index] == "#":
            newline = text.find("\n", index)
            index = len(text) if newline < 0 else newline + 1
            continue
        break
    return index


def _mix_keyword_entries(
    text: str, start: int
) -> tuple[list[str], int] | None:
    """Split one literal top-level Elixir list without evaluating its values."""
    stack = ["["]
    matching = {")": "(", "]": "[", "}": "{"}
    entries: list[str] = []
    entry_start = start + 1
    quote: str | None = None
    escaped = False
    comment = False

    for index in range(start + 1, len(text)):
        char = text[index]
        if comment:
            if char == "\n":
                comment = False
            continue
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char == "#":
            comment = True
            continue
        if char in {"'", '"'}:
            if text[index : index + 3] == char * 3:
                return None
            quote = char
            continue
        if char in "([{":
            stack.append(char)
            continue
        if char in ")]}" and matching[char] != stack[-1]:
            return None
        if char in ")]}" and len(stack) > 1:
            stack.pop()
            continue
        if char == "]" and stack == ["["]:
            entries.append(text[entry_start:index])
            return entries, index + 1
        if stack == ["["] and char == ",":
            entries.append(text[entry_start:index])
            entry_start = index + 1
        elif stack == ["["] and char == "|":
            return None
    return None


def _mix_wrapper(
    text: str,
    definition_start: int,
    definition_end: int,
) -> list[str] | None:
    """Accept a bare project/0 or one ordinary Mix.Project module wrapper."""
    cursor = _skip_elixir_space_and_comments(text, 0)
    required_files: list[str] = []
    while match := _MIX_REQUIRE_FILE.match(text, cursor):
        path = PurePosixPath(match.group("path"))
        if (
            path.is_absolute()
            or path == PurePosixPath(".")
            or ".." in path.parts
            or path.suffix not in {".ex", ".exs"}
        ):
            return None
        required_files.append(path.as_posix())
        cursor = _skip_elixir_space_and_comments(text, match.end())

    module = _MIX_MODULE.match(text, cursor)
    if module is None:
        if required_files:
            return None
        return (
            []
            if _skip_elixir_space_and_comments(text, 0) == definition_start
            and _skip_elixir_space_and_comments(text, definition_end) == len(text)
            else None
        )

    cursor = _skip_elixir_space_and_comments(text, module.end())
    use_project = _MIX_USE_PROJECT.match(text, cursor)
    if use_project is None:
        return None
    cursor = _skip_elixir_space_and_comments(text, use_project.end())
    if cursor != _skip_elixir_space_and_comments(text, definition_start):
        return None

    cursor = _skip_elixir_space_and_comments(text, definition_end)
    end_match = re.match(r"end\b", text[cursor:])
    if end_match is None:
        return None
    cursor = _skip_elixir_space_and_comments(
        text, cursor + end_match.end()
    )
    if cursor != len(text):
        return None
    if len(required_files) != len(set(required_files)):
        return None
    return required_files


def _literal_mix_project(
    text: str,
) -> tuple[set[str], list[str]] | None:
    """Prove one literal project/0 inside a bounded ordinary Mix wrapper."""
    definitions = list(_MIX_PROJECT_DEFINITION.finditer(text))
    if len(definitions) != 1:
        return None
    definition = definitions[0]
    cursor = _skip_elixir_space_and_comments(text, definition.end())
    if cursor >= len(text) or text[cursor] != "[":
        return None
    parsed = _mix_keyword_entries(text, cursor)
    if parsed is None:
        return None
    entries, list_end = parsed

    if definition.group("block") is not None:
        tail = _skip_elixir_space_and_comments(text, list_end)
        end_match = re.match(r"end\b", text[tail:])
        if end_match is None:
            return None
        definition_end = tail + end_match.end()
    else:
        line_end = text.find("\n", list_end)
        line_end = len(text) if line_end < 0 else line_end
        if text[list_end:line_end].split("#", 1)[0].strip():
            return None
        definition_end = list_end

    required_files = _mix_wrapper(
        text,
        definition.start(),
        definition_end,
    )
    if required_files is None:
        return None

    keys: set[str] = set()
    for entry in entries:
        entry_start = _skip_elixir_space_and_comments(entry, 0)
        if entry_start == len(entry):
            continue
        match = _MIX_PROJECT_KEY.match(entry, entry_start)
        if match is None:
            return None
        key = match.group(1)
        value = entry[match.end():].strip()
        if key in keys or _MIX_SAFE_PROJECT_VALUE.fullmatch(value) is None:
            return None
        keys.add(key)
    return keys, required_files


def _literal_mix_project_keys(text: str) -> set[str] | None:
    """Return keys from one proven literal Mix project/0 definition."""
    project = _literal_mix_project(text)
    return None if project is None else project[0]


def _activates_mix_configuration(path: str, text: str) -> bool:
    """Detect Mix and ExUnit settings that can hide contract tests."""
    if path == "mix.exs":
        project_keys = _literal_mix_project_keys(text)
        return project_keys is None or bool(project_keys & _MIX_COLLECTION_KEYS)
    if path == "test/test_helper.exs":
        cursor = _skip_elixir_space_and_comments(text, 0)
        match = _MIX_SAFE_TEST_HELPER.match(text, cursor)
        if match is None:
            return True
        return _skip_elixir_space_and_comments(text, match.end()) != len(text)
    return False


def _audit_mix_configuration(
    repository_root: Path,
    files: list[dict[str, str]],
) -> tuple[list[str], list[str]]:
    """Hash known Mix configs and block collection-affecting settings."""
    observed: list[str] = []
    blockers: list[str] = []
    required_files: list[str] = []
    for relative_path in _MIX_CONFIG_PATHS:
        candidate = repository_root / relative_path
        if not candidate.exists() and not candidate.is_symlink():
            continue
        observed.append(relative_path)
        text, error = read_file(repository_root, relative_path, files)
        if error is not None or text is None:
            blockers.append(f"{relative_path}: {error or 'unreadable'}")
            continue
        if relative_path == "mix.exs":
            project = _literal_mix_project(text)
            if project is None or project[0] & _MIX_COLLECTION_KEYS:
                blockers.append(relative_path)
            else:
                required_files.extend(project[1])
        elif _activates_mix_configuration(relative_path, text):
            blockers.append(relative_path)
    for relative_path in required_files:
        observed.append(relative_path)
        text, error = read_file(repository_root, relative_path, files)
        if error is not None or text is None:
            blockers.append(f"{relative_path}: {error or 'unreadable'}")
            continue
        # Requiring an arbitrary Elixir file executes it while Mix loads the
        # project. Hashing cannot prove that execution reaches the tests.
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
