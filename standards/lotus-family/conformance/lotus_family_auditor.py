from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

PASS = "PASS"
DRIFT = "DRIFT"
UNKNOWN = "UNKNOWN"

_COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")


def load_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} root must be an object")
    return value


def load_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json_object(path)
    if manifest.get("schema_version") != "pythia.lotus_family_manifest.v0.1":
        raise ValueError("unsupported Lotus Family manifest schema")
    if manifest.get("authority") != "audit_only":
        raise ValueError("Lotus Family manifest authority must be audit_only")
    repositories = manifest.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        raise ValueError("manifest repositories must be a non-empty list")
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


def _repository_config(
    manifest: Mapping[str, Any], repository_id: str
) -> Mapping[str, Any] | None:
    for row in manifest["repositories"]:
        if row.get("id") == repository_id:
            return row
    return None


def _read_file(
    root: Path,
    relative_path: str,
    files: list[dict[str, str]],
) -> tuple[str | None, str | None]:
    path = root / relative_path
    if not path.is_file():
        return None, f"required file is missing: {relative_path}"
    try:
        text = path.read_text(encoding="utf-8")
        files.append({"path": relative_path, "sha256": _sha256(path)})
        return text, None
    except (OSError, UnicodeError) as exc:
        return None, f"cannot read {relative_path}: {exc.__class__.__name__}"


def audit_repository(
    manifest: Mapping[str, Any],
    *,
    repository_id: str,
    snapshot_root: Path,
    repository_ref: str,
    commit_sha: str,
) -> dict[str, Any]:
    manifest_schema = str(manifest.get("schema_version", ""))
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

    repository_root = snapshot_root / str(config["snapshot_dir"])
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

    for check in config.get("file_checks", []):
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

        missing_terms = [
            term for term in check.get("contains_all", []) if term not in text
        ]
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

    discovery = config.get("ci_discovery")
    if discovery:
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
        patterns = [str(pattern) for pattern in discovery["contains_any"]]
        discovered = any(pattern in combined for pattern in patterns)
        if read_errors and not workflow_texts:
            outcome = DRIFT
            detail = "; ".join(read_errors)
            drift.append("ci_discovery")
        elif discovered:
            outcome = PASS
            detail = "contract regression test is discovered by CI"
        else:
            outcome = DRIFT
            detail = "no configured CI discovery pattern was found"
            drift.append("ci_discovery")
        checks.append(
            {
                "check_id": "ci_discovery",
                "outcome": outcome,
                "paths": workflow_paths,
                "matched_patterns": [
                    pattern for pattern in patterns if pattern in combined
                ],
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
        result = {
            "schema_version": "pythia.lotus_family_audit_result.v0.1",
            "outcome": UNKNOWN,
            "reason_code": "MANIFEST_INVALID",
            "detail": str(exc),
            "authority": {
                "mode": "audit_only",
                "grants_ownership": False,
                "grants_approval": False,
                "grants_execution": False,
                "grants_delivery": False,
                "grants_merge": False,
            },
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return {PASS: 0, DRIFT: 2, UNKNOWN: 3}.get(result["outcome"], 3)


if __name__ == "__main__":
    raise SystemExit(main())
