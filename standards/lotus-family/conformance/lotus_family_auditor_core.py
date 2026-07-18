from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import shlex
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

PASS = "PASS"
DRIFT = "DRIFT"
UNKNOWN = "UNKNOWN"

_COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_PYTEST_STARTS = (("python", "-m", "pytest"), ("pytest",))
_SAFE_PYTEST_FLAGS = {
    "-q", "--quiet", "-v", "--verbose", "--strict-markers",
    "--strict-config", "--disable-warnings",
}
_SAFE_PYTEST_PREFIXES = (
    "--junitxml=", "--cov=", "--cov-report=", "--color=", "--tb=",
    "--durations=", "--maxfail=",
)
_FORBIDDEN_PYTEST_FLAGS = {
    "--collect-only", "--co", "--setup-only", "--pyargs",
    "-k", "--keyword", "-m", "--markers", "--deselect",
}
_SHELL_CONTROL = {"&&", "||", ";", "|", "&"}


def load_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} root must be an object")
    return value


def _non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _relative_manifest_path(value: Any, field: str) -> str:
    text = _non_empty_string(value, field)
    if "\\" in text:
        raise ValueError(f"{field} must use repository-style '/' separators")
    path = PurePosixPath(text)
    if path.is_absolute() or path == PurePosixPath(".") or ".." in path.parts:
        raise ValueError(f"{field} must stay inside the repository snapshot")
    return path.as_posix()


def _validate_manifest(manifest: Mapping[str, Any]) -> None:
    if manifest.get("schema_version") != "pythia.lotus_family_manifest.v0.1":
        raise ValueError("unsupported Lotus Family manifest schema")
    if manifest.get("authority") != "audit_only":
        raise ValueError("Lotus Family manifest authority must be audit_only")
    repositories = manifest.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        raise ValueError("manifest repositories must be a non-empty list")

    ids: set[str] = set()
    dirs: set[str] = set()
    for repo_index, repo in enumerate(repositories):
        prefix = f"repositories[{repo_index}]"
        if not isinstance(repo, Mapping):
            raise ValueError(f"{prefix} must be an object")
        repo_id = _non_empty_string(repo.get("id"), f"{prefix}.id")
        if repo_id in ids:
            raise ValueError(f"duplicate repository id: {repo_id}")
        ids.add(repo_id)
        _non_empty_string(repo.get("repository"), f"{prefix}.repository")
        snapshot_dir = _relative_manifest_path(
            repo.get("snapshot_dir"), f"{prefix}.snapshot_dir"
        )
        if "/" in snapshot_dir:
            raise ValueError(f"{prefix}.snapshot_dir must be one directory name")
        if snapshot_dir in dirs:
            raise ValueError(f"duplicate snapshot_dir: {snapshot_dir}")
        dirs.add(snapshot_dir)

        checks = repo.get("file_checks")
        if not isinstance(checks, list) or not checks:
            raise ValueError(f"{prefix}.file_checks must be a non-empty list")
        check_ids: set[str] = set()
        checked_paths: set[str] = set()
        for check_index, check in enumerate(checks):
            check_prefix = f"{prefix}.file_checks[{check_index}]"
            if not isinstance(check, Mapping):
                raise ValueError(f"{check_prefix} must be an object")
            check_id = _non_empty_string(check.get("id"), f"{check_prefix}.id")
            if check_id in check_ids:
                raise ValueError(f"duplicate check id in {repo_id}: {check_id}")
            check_ids.add(check_id)
            checked_paths.add(
                _relative_manifest_path(check.get("path"), f"{check_prefix}.path")
            )
            terms = check.get("contains_all")
            if not isinstance(terms, list) or not terms:
                raise ValueError(
                    f"{check_prefix}.contains_all must be a non-empty list"
                )
            for term_index, term in enumerate(terms):
                _non_empty_string(
                    term, f"{check_prefix}.contains_all[{term_index}]"
                )

        discovery = repo.get("ci_discovery")
        if not isinstance(discovery, Mapping):
            raise ValueError(f"{prefix}.ci_discovery must be an object")
        workflows = discovery.get("workflow_paths")
        if not isinstance(workflows, list) or not workflows:
            raise ValueError(
                f"{prefix}.ci_discovery.workflow_paths must be a non-empty list"
            )
        for path_index, workflow_path in enumerate(workflows):
            _relative_manifest_path(
                workflow_path,
                f"{prefix}.ci_discovery.workflow_paths[{path_index}]",
            )

        strategy = discovery.get("strategy")
        if strategy == "contains_any":
            patterns = discovery.get("contains_any")
            if not isinstance(patterns, list) or not patterns:
                raise ValueError(
                    f"{prefix}.ci_discovery.contains_any must be a non-empty list"
                )
            for pattern_index, pattern in enumerate(patterns):
                _non_empty_string(
                    pattern,
                    f"{prefix}.ci_discovery.contains_any[{pattern_index}]",
                )
        elif strategy == "pytest_default_discovery":
            command = _non_empty_string(
                discovery.get("command"), f"{prefix}.ci_discovery.command"
            )
            if command != "python -m pytest":
                raise ValueError(
                    f"{prefix}.ci_discovery.command must be 'python -m pytest'"
                )
            test_path = _relative_manifest_path(
                discovery.get("test_path"), f"{prefix}.ci_discovery.test_path"
            )
            test_name = PurePosixPath(test_path).name
            if not (test_name.startswith("test_") and test_name.endswith(".py")):
                raise ValueError(
                    f"{prefix}.ci_discovery.test_path is not pytest-discoverable"
                )
            if test_path not in checked_paths:
                raise ValueError(
                    f"{prefix}.ci_discovery.test_path must also be a checked file"
                )
        else:
            raise ValueError(
                f"{prefix}.ci_discovery.strategy is unsupported: {strategy}"
            )


def load_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json_object(path)
    _validate_manifest(manifest)
    return manifest


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _result(
    *,
    outcome: str,
    reason_code: str,
    detail: str,
    repository: str,
    repository_id: str,
    repository_ref: str,
    commit_sha: str,
    manifest_schema: str,
    checks: list[dict[str, Any]],
    files: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "schema_version": "pythia.lotus_family_audit_result.v0.1",
        "outcome": outcome,
        "reason_code": reason_code,
        "detail": detail,
        "repository": repository,
        "repository_id": repository_id,
        "repository_ref": repository_ref,
        "commit_sha": commit_sha,
        "manifest_schema": manifest_schema,
        "checks": checks,
        "files": sorted(files, key=lambda row: row["path"]),
        "authority": {
            "mode": "audit_only",
            "grants_ownership": False,
            "grants_approval": False,
            "grants_execution": False,
            "grants_delivery": False,
            "grants_merge": False,
        },
    }


def _manifest_invalid_result(
    detail: str,
    repository_id: str,
    repository_ref: str,
    commit_sha: str,
    manifest_schema: str,
) -> dict[str, Any]:
    return _result(
        outcome=UNKNOWN,
        reason_code="MANIFEST_INVALID",
        detail=detail,
        repository="",
        repository_id=repository_id,
        repository_ref=repository_ref,
        commit_sha=commit_sha,
        manifest_schema=manifest_schema,
        checks=[],
        files=[],
    )


def _repository_config(
    manifest: Mapping[str, Any], repository_id: str
) -> Mapping[str, Any] | None:
    return next(
        (row for row in manifest["repositories"] if row.get("id") == repository_id),
        None,
    )


def _contained_path(
    root: Path, relative_path: str
) -> tuple[Path | None, str | None]:
    try:
        normalized = _relative_manifest_path(relative_path, "manifest path")
        root_resolved = root.resolve()
        path = (root_resolved / Path(*PurePosixPath(normalized).parts)).resolve()
        path.relative_to(root_resolved)
        return path, None
    except (OSError, ValueError):
        return None, f"path escapes repository snapshot: {relative_path}"


def _read_file(
    root: Path,
    relative_path: str,
    files: list[dict[str, str]],
) -> tuple[str | None, str | None]:
    path, error = _contained_path(root, relative_path)
    if error is not None or path is None:
        return None, error
    if not path.is_file():
        return None, f"required file is missing: {relative_path}"
    try:
        text = path.read_text(encoding="utf-8")
        files.append({"path": relative_path, "sha256": _sha256(path)})
        return text, None
    except (OSError, UnicodeError) as exc:
        return None, f"cannot read {relative_path}: {exc.__class__.__name__}"


def _strip_unquoted_shell_comment(line: str) -> str:
    in_single = False
    in_double = False
    escaped = False
    for index, character in enumerate(line):
        if escaped:
            escaped = False
            continue
        if character == "\\" and not in_single:
            escaped = True
            continue
        if character == "'" and not in_double:
            in_single = not in_single
            continue
        if character == '"' and not in_single:
            in_double = not in_double
            continue
        if character == "#" and not in_single and not in_double:
            return line[:index]
    return line


def _shell_commands(text: str) -> list[str]:
    lines = text.splitlines()
    commands: list[str] = []
    index = 0
    while index < len(lines):
        first = _strip_unquoted_shell_comment(lines[index]).strip()
        if not first:
            index += 1
            continue
        parts = [first]
        while parts[-1].rstrip().endswith("\\") and index + 1 < len(lines):
            parts[-1] = parts[-1].rstrip()[:-1]
            index += 1
            continuation = _strip_unquoted_shell_comment(lines[index]).strip()
            if continuation:
                parts.append(continuation)
        commands.append(" ".join(parts))
        index += 1
    return commands


def _tokenize_executed_command(command: str) -> list[str] | None:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    if not tokens or any(token in _SHELL_CONTROL for token in tokens):
        return None
    index = 0
    while index < len(tokens) and re.fullmatch(
        r"[A-Za-z_][A-Za-z0-9_]*=.*", tokens[index]
    ):
        index += 1
    return tokens[index:] or None


def _pytest_parts(tokens: list[str]) -> tuple[list[str], list[str]] | None:
    for start in _PYTEST_STARTS:
        if tuple(tokens[: len(start)]) == start:
            return list(start), tokens[len(start) :]
    return None


def _normalize_repo_pattern(value: str) -> str:
    normalized = value.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.rstrip("/")


def _ignore_path_covers_test(ignore_path: str, test_path: str) -> bool:
    normalized = _normalize_repo_pattern(ignore_path)
    if not normalized:
        return True
    ignored = PurePosixPath(normalized)
    test = PurePosixPath(test_path)
    if ignored.is_absolute() or ".." in ignored.parts:
        return True
    return ignored == test or ignored in test.parents


def _ignore_glob_covers_test(pattern: str, test_path: str) -> bool:
    normalized = _normalize_repo_pattern(pattern)
    if not normalized:
        return True
    test = PurePosixPath(test_path)
    candidates = [test.as_posix(), test.name]
    candidates.extend(
        parent.as_posix()
        for parent in test.parents
        if parent != PurePosixPath(".")
    )
    return any(
        fnmatch.fnmatchcase(candidate, normalized) for candidate in candidates
    )


def _pytest_arguments_safe(
    arguments: list[str], test_path: str, *, require_test_path: bool
) -> bool:
    positive_paths: list[str] = []
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        if argument in _FORBIDDEN_PYTEST_FLAGS or argument.startswith(
            ("-k=", "--keyword=", "-m=", "--markers=", "--deselect=")
        ):
            return False
        if argument.startswith("--ignore="):
            if _ignore_path_covers_test(argument.split("=", 1)[1], test_path):
                return False
        elif argument == "--ignore":
            if index + 1 >= len(arguments):
                return False
            if _ignore_path_covers_test(arguments[index + 1], test_path):
                return False
            index += 1
        elif argument.startswith("--ignore-glob="):
            if _ignore_glob_covers_test(argument.split("=", 1)[1], test_path):
                return False
        elif argument == "--ignore-glob":
            if index + 1 >= len(arguments):
                return False
            if _ignore_glob_covers_test(arguments[index + 1], test_path):
                return False
            index += 1
        elif argument in _SAFE_PYTEST_FLAGS or argument.startswith(
            _SAFE_PYTEST_PREFIXES
        ):
            pass
        elif argument.startswith("-"):
            return False
        else:
            positive_paths.append(
                _normalize_repo_pattern(argument.split("::", 1)[0])
            )
        index += 1

    normalized_test = _normalize_repo_pattern(test_path)
    if require_test_path:
        return normalized_test in positive_paths
    return not positive_paths


def _is_pytest_default_discovery(command: str, test_path: str) -> bool:
    tokens = _tokenize_executed_command(command)
    if tokens is None:
        return False
    parts = _pytest_parts(tokens)
    return parts is not None and _pytest_arguments_safe(
        parts[1], test_path, require_test_path=False
    )


def _is_explicit_pytest_test_command(command: str, test_path: str) -> bool:
    tokens = _tokenize_executed_command(command)
    if tokens is None:
        return False
    parts = _pytest_parts(tokens)
    return parts is not None and _pytest_arguments_safe(
        parts[1], test_path, require_test_path=True
    )


def _is_command_prefix(command: str, prefix: str) -> bool:
    tokens = _tokenize_executed_command(command)
    if tokens is None:
        return False
    try:
        required = shlex.split(prefix)
    except ValueError:
        return False
    return tokens[: len(required)] == required


def _ci_discovery(
    discovery: Mapping[str, Any], combined: str
) -> tuple[bool, list[str]]:
    commands = _shell_commands(combined)
    strategy = discovery["strategy"]
    if strategy == "pytest_default_discovery":
        test_path = str(discovery["test_path"])
        matched = any(
            _is_pytest_default_discovery(command, test_path)
            for command in commands
        )
        return matched, [str(discovery["command"])] if matched else []

    matches: list[str] = []
    for pattern_value in discovery["contains_any"]:
        pattern = str(pattern_value)
        if pattern.endswith(".py"):
            if any(
                _is_explicit_pytest_test_command(command, pattern)
                for command in commands
            ):
                matches.append(pattern)
        elif any(_is_command_prefix(command, pattern) for command in commands):
            matches.append(pattern)
    return bool(matches), matches


def audit_repository(
    manifest: Mapping[str, Any],
    *,
    repository_id: str,
    snapshot_root: Path,
    repository_ref: str,
    commit_sha: str,
) -> dict[str, Any]:
    manifest_schema = str(manifest.get("schema_version", ""))
    try:
        _validate_manifest(manifest)
    except (TypeError, ValueError) as exc:
        return _manifest_invalid_result(
            str(exc),
            repository_id,
            repository_ref,
            commit_sha,
            manifest_schema,
        )

    config = _repository_config(manifest, repository_id)
    if config is None:
        return _result(
            outcome=UNKNOWN,
            reason_code="REPOSITORY_NOT_CONFIGURED",
            detail=f"repository adapter is not configured: {repository_id}",
            repository="",
            repository_id=repository_id,
            repository_ref=repository_ref,
            commit_sha=commit_sha,
            manifest_schema=manifest_schema,
            checks=[],
            files=[],
        )

    repository = str(config["repository"])
    if not repository_ref:
        return _result(
            outcome=UNKNOWN,
            reason_code="REPOSITORY_REF_MISSING",
            detail="an exact repository ref is required",
            repository=repository,
            repository_id=repository_id,
            repository_ref=repository_ref,
            commit_sha=commit_sha,
            manifest_schema=manifest_schema,
            checks=[],
            files=[],
        )
    if not _COMMIT_SHA.fullmatch(commit_sha):
        return _result(
            outcome=UNKNOWN,
            reason_code="COMMIT_SHA_INVALID",
            detail="commit_sha must be a lowercase 40-character hexadecimal SHA",
            repository=repository,
            repository_id=repository_id,
            repository_ref=repository_ref,
            commit_sha=commit_sha,
            manifest_schema=manifest_schema,
            checks=[],
            files=[],
        )

    snapshot_root_resolved = snapshot_root.resolve()
    repository_root = (
        snapshot_root_resolved / str(config["snapshot_dir"])
    ).resolve()
    try:
        repository_root.relative_to(snapshot_root_resolved)
    except ValueError:
        return _result(
            outcome=UNKNOWN,
            reason_code="SNAPSHOT_UNAVAILABLE",
            detail="repository snapshot escapes snapshot_root",
            repository=repository,
            repository_id=repository_id,
            repository_ref=repository_ref,
            commit_sha=commit_sha,
            manifest_schema=manifest_schema,
            checks=[],
            files=[],
        )
    if not repository_root.is_dir():
        return _result(
            outcome=UNKNOWN,
            reason_code="SNAPSHOT_UNAVAILABLE",
            detail=f"repository snapshot is unavailable: {config['snapshot_dir']}",
            repository=repository,
            repository_id=repository_id,
            repository_ref=repository_ref,
            commit_sha=commit_sha,
            manifest_schema=manifest_schema,
            checks=[],
            files=[],
        )

    checks: list[dict[str, Any]] = []
    files: list[dict[str, str]] = []
    drift: list[str] = []
    for check in config["file_checks"]:
        check_id = str(check["id"])
        relative_path = str(check["path"])
        text, error = _read_file(repository_root, relative_path, files)
        if error is not None or text is None:
            checks.append(
                {
                    "check_id": check_id,
                    "outcome": DRIFT,
                    "path": relative_path,
                    "missing_terms": [],
                    "detail": error,
                }
            )
            drift.append(check_id)
            continue
        terms = [str(term) for term in check["contains_all"]]
        missing_terms = [term for term in terms if term not in text]
        outcome = PASS if not missing_terms else DRIFT
        checks.append(
            {
                "check_id": check_id,
                "outcome": outcome,
                "path": relative_path,
                "missing_terms": missing_terms,
                "detail": (
                    "all required terms are present"
                    if outcome == PASS
                    else "required terms are missing"
                ),
            }
        )
        if outcome == DRIFT:
            drift.append(check_id)

    discovery = config["ci_discovery"]
    workflow_paths = [str(path) for path in discovery["workflow_paths"]]
    workflow_texts: list[str] = []
    read_errors: list[str] = []
    for relative_path in workflow_paths:
        text, error = _read_file(repository_root, relative_path, files)
        if error is not None or text is None:
            read_errors.append(error or f"cannot read {relative_path}")
        else:
            workflow_texts.append(text)

    discovered, matched_patterns = _ci_discovery(
        discovery, "\n".join(workflow_texts)
    )
    if read_errors and not workflow_texts:
        ci_outcome = DRIFT
        detail = "; ".join(read_errors)
    elif discovered:
        ci_outcome = PASS
        detail = "contract regression test is discovered by executable CI"
    else:
        ci_outcome = DRIFT
        detail = "no configured executable CI discovery rule matched"
    if ci_outcome == DRIFT:
        drift.append("ci_discovery")
    checks.append(
        {
            "check_id": "ci_discovery",
            "outcome": ci_outcome,
            "paths": workflow_paths,
            "matched_patterns": matched_patterns,
            "detail": detail,
        }
    )

    if drift:
        outcome = DRIFT
        reason_code = "LOTUS_CONTRACT_DRIFT"
        detail = "non-conforming checks: " + ", ".join(sorted(set(drift)))
    else:
        outcome = PASS
        reason_code = "LOTUS_CONTRACT_CONFORMANT"
        detail = "all configured Lotus Family invariants passed"

    unique_files = {(row["path"], row["sha256"]): row for row in files}
    return _result(
        outcome=outcome,
        reason_code=reason_code,
        detail=detail,
        repository=repository,
        repository_id=repository_id,
        repository_ref=repository_ref,
        commit_sha=commit_sha,
        manifest_schema=manifest_schema,
        checks=checks,
        files=list(unique_files.values()),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit one exact repository snapshot against the Lotus Family manifest."
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--snapshot-root", type=Path, required=True)
    parser.add_argument("--repository-id", required=True)
    parser.add_argument("--repository-ref", required=True)
    parser.add_argument("--commit-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        manifest = load_manifest(args.manifest)
        result = audit_repository(
            manifest,
            repository_id=args.repository_id,
            snapshot_root=args.snapshot_root,
            repository_ref=args.repository_ref,
            commit_sha=args.commit_sha,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        result = _manifest_invalid_result(
            str(exc),
            args.repository_id,
            args.repository_ref,
            args.commit_sha,
            "",
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return {PASS: 0, DRIFT: 2, UNKNOWN: 3}.get(result["outcome"], 3)


if __name__ == "__main__":
    raise SystemExit(main())
