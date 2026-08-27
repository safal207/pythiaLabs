from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

PASS, DRIFT, UNKNOWN = "PASS", "DRIFT", "UNKNOWN"
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
ACTION_SHA_REF = re.compile(
    r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}$"
)


def load_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} root must be an object")
    return value


def non_empty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def relative_path(value: Any, field: str) -> str:
    text = non_empty(value, field)
    if "\\" in text:
        raise ValueError(f"{field} must use repository-style '/' separators")
    path = PurePosixPath(text)
    if path.is_absolute() or path == PurePosixPath(".") or ".." in path.parts:
        raise ValueError(f"{field} must stay inside the repository snapshot")
    return path.as_posix()


def validate_manifest(manifest: Mapping[str, Any]) -> None:
    if manifest.get("schema_version") != "pythia.lotus_family_manifest.v0.1":
        raise ValueError("unsupported Lotus Family manifest schema")
    if manifest.get("authority") != "audit_only":
        raise ValueError("Lotus Family manifest authority must be audit_only")
    repos = manifest.get("repositories")
    if not isinstance(repos, list) or not repos:
        raise ValueError("manifest repositories must be a non-empty list")
    ids: set[str] = set()
    dirs: set[str] = set()
    for ri, repo in enumerate(repos):
        prefix = f"repositories[{ri}]"
        if not isinstance(repo, Mapping):
            raise ValueError(f"{prefix} must be an object")
        repo_id = non_empty(repo.get("id"), f"{prefix}.id")
        if repo_id in ids:
            raise ValueError(f"duplicate repository id: {repo_id}")
        ids.add(repo_id)
        non_empty(repo.get("repository"), f"{prefix}.repository")
        snapshot_dir = relative_path(repo.get("snapshot_dir"), f"{prefix}.snapshot_dir")
        if "/" in snapshot_dir or snapshot_dir in dirs:
            raise ValueError(f"invalid or duplicate snapshot_dir: {snapshot_dir}")
        dirs.add(snapshot_dir)
        checks = repo.get("file_checks")
        if not isinstance(checks, list) or not checks:
            raise ValueError(f"{prefix}.file_checks must be a non-empty list")
        check_ids: set[str] = set()
        checked: set[str] = set()
        for ci, check in enumerate(checks):
            cp = f"{prefix}.file_checks[{ci}]"
            if not isinstance(check, Mapping):
                raise ValueError(f"{cp} must be an object")
            check_id = non_empty(check.get("id"), f"{cp}.id")
            if check_id in check_ids:
                raise ValueError(f"duplicate check id in {repo_id}: {check_id}")
            check_ids.add(check_id)
            checked.add(relative_path(check.get("path"), f"{cp}.path"))
            terms = check.get("contains_all")
            if not isinstance(terms, list) or not terms:
                raise ValueError(f"{cp}.contains_all must be a non-empty list")
            for ti, term in enumerate(terms):
                non_empty(term, f"{cp}.contains_all[{ti}]")
        discovery = repo.get("ci_discovery")
        if not isinstance(discovery, Mapping):
            raise ValueError(f"{prefix}.ci_discovery must be an object")
        workflows = discovery.get("workflow_paths")
        if not isinstance(workflows, list) or not workflows:
            raise ValueError(f"{prefix}.ci_discovery.workflow_paths must be a non-empty list")
        for wi, workflow in enumerate(workflows):
            relative_path(workflow, f"{prefix}.ci_discovery.workflow_paths[{wi}]")
        trusted_actions = discovery.get("trusted_prerequisite_actions", [])
        if not isinstance(trusted_actions, list):
            raise ValueError(
                f"{prefix}.ci_discovery.trusted_prerequisite_actions must be a list"
            )
        if any(not isinstance(action, str) for action in trusted_actions):
            raise ValueError(
                f"{prefix}.ci_discovery.trusted_prerequisite_actions must contain strings"
            )
        if len(trusted_actions) != len(set(trusted_actions)):
            raise ValueError(
                f"{prefix}.ci_discovery.trusted_prerequisite_actions must be unique"
            )
        for ai, action in enumerate(trusted_actions):
            field = (
                f"{prefix}.ci_discovery.trusted_prerequisite_actions[{ai}]"
            )
            if not ACTION_SHA_REF.fullmatch(action):
                raise ValueError(
                    f"{field} must be an owner/repository action pinned to a full SHA"
                )
        strategy = discovery.get("strategy")
        if strategy == "contains_any":
            patterns = discovery.get("contains_any")
            if not isinstance(patterns, list) or not patterns:
                raise ValueError(f"{prefix}.ci_discovery.contains_any must be a non-empty list")
            for pi, pattern in enumerate(patterns):
                text = non_empty(pattern, f"{prefix}.ci_discovery.contains_any[{pi}]")
                if text.endswith((".py", ".exs")) and relative_path(text, f"{prefix}.ci_discovery.contains_any[{pi}]") not in checked:
                    raise ValueError(f"{prefix}.ci_discovery pattern must also be a checked file")
        elif strategy in {"pytest_default_discovery", "mix_default_discovery"}:
            expected = "python -m pytest" if strategy.startswith("pytest") else "mix test"
            if non_empty(discovery.get("command"), f"{prefix}.ci_discovery.command") != expected:
                raise ValueError(f"{prefix}.ci_discovery.command must be {expected!r}")
            test_path = relative_path(discovery.get("test_path"), f"{prefix}.ci_discovery.test_path")
            name = PurePosixPath(test_path).name
            if strategy.startswith("pytest") and not (name.startswith("test_") and name.endswith(".py")):
                raise ValueError(f"{prefix}.ci_discovery.test_path is not pytest-discoverable")
            if strategy.startswith("mix") and not name.endswith("_test.exs"):
                raise ValueError(f"{prefix}.ci_discovery.test_path is not Mix-test-discoverable")
            if test_path not in checked:
                raise ValueError(f"{prefix}.ci_discovery.test_path must also be a checked file")
        else:
            raise ValueError(f"{prefix}.ci_discovery.strategy is unsupported: {strategy}")


def load_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json_object(path)
    validate_manifest(manifest)
    return manifest


def repository_config(manifest: Mapping[str, Any], repository_id: str) -> Mapping[str, Any] | None:
    return next((row for row in manifest["repositories"] if row.get("id") == repository_id), None)


def contained_path(root: Path, name: str) -> tuple[Path | None, str | None]:
    try:
        normalized = relative_path(name, "manifest path")
        resolved_root = root.resolve()
        path = (resolved_root / Path(*PurePosixPath(normalized).parts)).resolve()
        path.relative_to(resolved_root)
        return path, None
    except (OSError, ValueError):
        return None, f"path escapes repository snapshot: {name}"


def read_file(root: Path, name: str, files: list[dict[str, str]]) -> tuple[str | None, str | None]:
    path, error = contained_path(root, name)
    if error or path is None:
        return None, error
    if not path.is_file():
        return None, f"required file is missing: {name}"
    try:
        data = path.read_bytes()
        text = data.decode("utf-8")
        files.append({"path": name, "sha256": hashlib.sha256(data).hexdigest()})
        return text, None
    except (OSError, UnicodeError) as exc:
        return None, f"cannot read {name}: {exc.__class__.__name__}"


def result(*, outcome: str, reason_code: str, detail: str, repository: str, repository_id: str,
           repository_ref: str, commit_sha: str, manifest_schema: str,
           checks: list[dict[str, Any]], files: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "pythia.lotus_family_audit_result.v0.1",
        "outcome": outcome,
        "reason_code": reason_code,
        "detail": detail,
        "repository": repository,
        "repository_id": repository_id,
        "repository_ref": repository_ref,
        "commit_sha": commit_sha,
        "identity_assurance": {
            "mode": "caller_claim_only",
            "remote_repository_verified": False,
            "commit_reachability_verified": False,
            "working_tree_clean_verified": False,
        },
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


def manifest_invalid(detail: str, repository_id: str, repository_ref: str, commit_sha: str, schema: str) -> dict[str, Any]:
    return result(outcome=UNKNOWN, reason_code="MANIFEST_INVALID", detail=detail,
                  repository="", repository_id=repository_id, repository_ref=repository_ref,
                  commit_sha=commit_sha, manifest_schema=schema, checks=[], files=[])
