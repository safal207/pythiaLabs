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
_PYTEST_START = ("python", "-m", "pytest")


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
    path_text = _non_empty_string(value, field)
    if "\\" in path_text:
        raise ValueError(f"{field} must use repository-style '/' separators")
    path = PurePosixPath(path_text)
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

    repository_ids: set[str] = set()
    snapshot_dirs: set[str] = set()
    for repository_index, repository in enumerate(repositories):
        prefix = f"repositories[{repository_index}]"
        if not isinstance(repository, Mapping):
            raise ValueError(f"{prefix} must be an object")

        repository_id = _non_empty_string(repository.get("id"), f"{prefix}.id")
        if repository_id in repository_ids:
            raise ValueError(f"duplicate repository id: {repository_id}")
        repository_ids.add(repository_id)

        _non_empty_string(repository.get("repository"), f"{prefix}.repository")
        snapshot_dir = _relative_manifest_path(
            repository.get("snapshot_dir"), f"{prefix}.snapshot_dir"
        )
        if "/" in snapshot_dir:
            raise ValueError(f"{prefix}.snapshot_dir must be one directory name")
        if snapshot_dir in snapshot_dirs:
            raise ValueError(f"duplicate snapshot_dir: {snapshot_dir}")
        snapshot_dirs.add(snapshot_dir)

        file_checks = repository.get("file_checks")
        if not isinstance(file_checks, list) or not file_checks:
            raise ValueError(f"{prefix}.file_checks must be a non-empty list")

        check_ids: set[str] = set()
        checked_paths: set[str] = set()
        for check_index, check in enumerate(file_checks):
            check_prefix = f"{prefix}.file_checks[{check_index}]"
            if not isinstance(check, Mapping):
                raise ValueError(f"{check_prefix} must be an object")

            check_id = _non_empty_string(check.get("id"), f"{check_prefix}.id")
            if check_id in check_ids:
                raise ValueError(f"duplicate check id in {repository_id}: {check_id}")
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

        discovery = repository.get("ci_discovery")
        if not isinstance(discovery, Mapping):
            raise ValueError(f"{prefix}.ci_discovery must be an object")

        workflow_paths = discovery.get("workflow_paths")
        if not isinstance(workflow_paths, list) or not workflow_paths:
            raise ValueError(
                f"{prefix}.ci_discovery.workflow_paths must be a non-empty list"
            )
        for path_index, workflow_path in enumerate(workflow_paths):
            _relative_manifest_path(
                workflow_path,
                f"{prefix}.ci_discovery.workflow_paths[{path_index}]",
            )

        strategy = discovery.get("strategy", "contains_any")
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
    *,
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
    for row in manifest["repositories"]:
        if row.get("id") == repository_id:
            return row
    return None


def _contained_path(root: Path, relative_path: str) -> tuple[Path | None, str | None]:
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
    path, containment_error = _contained_path(root, relative_path)
    if containment_error is not None or path is None:
        return None, containment_error
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
        stripped = _strip_unquoted_shell_comment(lines[index]).strip()
        if "python -m pytest" not in stripped:
            index += 1
            continue

        parts = [stripped]
        while parts[-1].rstrip().endswith("\\") and index + 1 < len(lines):
            parts[-1] = parts[-1].rstrip()[:-1]
            index += 1
            continuation = _strip_unquoted_shell_comment(lines[index]).strip()
            if continuation:
                parts.append(continuation)
        commands.append(" ".join(parts))
        index += 1
    return commands


def _ignore_path_covers_test(ignore_path: str, test_path: str) -> bool:
    normalized = ignore_path.strip().replace("\\", "/").rstrip("/")
    if not normalized:
        return True
    ignored = PurePosixPath(normalized)
    test = PurePosixPath(test_path)
    if ignored.is_absolute() or ".." in ignored.parts:
        return True
    return ignored == test or ignored in test.parents


def _ignore_glob_covers_test(pattern: str, test_path: str) -> bool:
    normalized = pattern.strip().replace("\\", "/")
    if not normalized:
        return True
    test = PurePosixPath(test_path)
    candidates = [test.as_posix(), test.name]
    candidates.extend(
        parent.as_posix()
        for parent in test.parents
        if parent != PurePosixPath(".")
    )
    return any(fnmatch.fnmatchcase(candidate, normalized) for candidate in candidates)


def _is_pytest_default_discovery(command: str, test_path: str) -> bool:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False

    start = None
    for index in range(len(tokens) - 2):
        if tuple(tokens[index : index + 3]) == _PYTEST_START:
            start = index + 3
            break
    if start is None:
        return False

    arguments = tokens[start:]
    forbidden_options = {"--collect-only", "--co", "--setup-only"}
    if any(argument in forbidden_options for argument in arguments):
        return False
    if any(test_path in argument for argument in arguments):
        return False

    for index, argument in enumerate(arguments):
        if argument.startswith("--ignore="):
            if _ignore_path_covers_test(argument.split("=", 1)[1], test_path):
                return False
        elif argument == "--ignore":
            if index + 1 >= len(arguments):
                return False
            if _ignore_path_covers_test(arguments[index + 1], test_path):
                return False
        elif argument.startswith("--ignore-glob="):
            if _ignore_glob_covers_test(argument.split("=", 1)[1], test_path):
                return False
        elif argument == "--ignore-glob":
            if index + 1 >= len(arguments):
                return False
            if _ignore_glob_covers_test(arguments[index + 1], test_path):
                return False

    # Fail closed on positional selectors. The supported full-discovery form may
    # carry options, but it may not name a test file, directory, or node id.
    return all(argument.startswith("-") for argument in arguments)


def _ci_discovery(
    discovery: Mapping[str, Any],
    combined: str,
) -> tuple[bool, list[str]]:
    strategy = discovery.get("strategy", "contains_any")
    if strategy == "contains_any":
        patterns = [str(pattern) for pattern in discovery["contains_any"]]
        matches = [pattern for pattern in patterns if pattern in combined]
        return bool(matches), matches

    if strategy == "pytest_default_discovery":
        command_name = str(discovery["command"])
        test_path = str(discovery["test_path"])
        matches = [
            command
            for command in _shell_commands(combined)
            if _is_pytest_default_discovery(command, test_path)
        ]
        return bool(matches), [command_name] if matches else []

    return False, []


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
            detail=str(exc),
            repository_id=repository_id,
            repository_ref=repository_ref,
            commit_sha=commit_sha,
            manifest_schema=manifest_schema,
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
        if error is not None:
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
        if error is not None:
            read_errors.append(error)
        else:
            workflow_texts.append(text)

    combined = "\n".join(workflow_texts)
    discovered, matched_patterns = _ci_discovery(discovery, combined)
    if read_errors and not workflow_texts:
        outcome = DRIFT
        detail = "; ".join(read_errors)
        drift.append("ci_discovery")
    elif discovered:
        outcome = PASS
        detail = "contract regression test is discovered by CI"
    else:
        outcome = DRIFT
        detail = "no configured contract-specific CI discovery rule matched"
        drift.append("ci_discovery")
    checks.append(
        {
            "check_id": "ci_discovery",
            "outcome": outcome,
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
            detail=str(exc),
            repository_id=args.repository_id,
            repository_ref=args.repository_ref,
            commit_sha=args.commit_sha,
            manifest_schema="",
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
