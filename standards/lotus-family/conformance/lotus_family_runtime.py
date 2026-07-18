from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from lotus_family_schema import (
    COMMIT_SHA,
    DRIFT,
    PASS,
    UNKNOWN,
    load_manifest,
    manifest_invalid,
    read_file,
    repository_config,
    result,
    validate_manifest,
)
from lotus_family_workflow import ci_discovery


def audit_repository(
    manifest: Mapping[str, Any],
    *,
    repository_id: str,
    snapshot_root: Path,
    repository_ref: str,
    commit_sha: str,
) -> dict[str, Any]:
    schema = str(manifest.get("schema_version", ""))
    try:
        validate_manifest(manifest)
    except (TypeError, ValueError) as exc:
        return manifest_invalid(str(exc), repository_id, repository_ref, commit_sha, schema)
    config = repository_config(manifest, repository_id)
    if config is None:
        return result(outcome=UNKNOWN, reason_code="REPOSITORY_NOT_CONFIGURED",
                      detail=f"repository adapter is not configured: {repository_id}",
                      repository="", repository_id=repository_id, repository_ref=repository_ref,
                      commit_sha=commit_sha, manifest_schema=schema, checks=[], files=[])
    repository = str(config["repository"])
    if not repository_ref:
        return result(outcome=UNKNOWN, reason_code="REPOSITORY_REF_MISSING",
                      detail="an exact repository ref claim is required", repository=repository,
                      repository_id=repository_id, repository_ref=repository_ref, commit_sha=commit_sha,
                      manifest_schema=schema, checks=[], files=[])
    if not COMMIT_SHA.fullmatch(commit_sha):
        return result(outcome=UNKNOWN, reason_code="COMMIT_SHA_INVALID",
                      detail="commit_sha claim must be a lowercase 40-character hexadecimal SHA",
                      repository=repository, repository_id=repository_id, repository_ref=repository_ref,
                      commit_sha=commit_sha, manifest_schema=schema, checks=[], files=[])
    root = snapshot_root.resolve()
    repository_root = (root / str(config["snapshot_dir"])).resolve()
    try:
        repository_root.relative_to(root)
    except ValueError:
        return result(outcome=UNKNOWN, reason_code="SNAPSHOT_UNAVAILABLE",
                      detail="repository snapshot escapes snapshot_root", repository=repository,
                      repository_id=repository_id, repository_ref=repository_ref, commit_sha=commit_sha,
                      manifest_schema=schema, checks=[], files=[])
    if not repository_root.is_dir():
        return result(outcome=UNKNOWN, reason_code="SNAPSHOT_UNAVAILABLE",
                      detail=f"repository snapshot is unavailable: {config['snapshot_dir']}",
                      repository=repository, repository_id=repository_id, repository_ref=repository_ref,
                      commit_sha=commit_sha, manifest_schema=schema, checks=[], files=[])

    checks: list[dict[str, Any]] = []
    files: list[dict[str, str]] = []
    drift: list[str] = []
    for check in config["file_checks"]:
        check_id = str(check["id"])
        name = str(check["path"])
        text, error = read_file(repository_root, name, files)
        if error or text is None:
            checks.append({"check_id": check_id, "outcome": DRIFT, "path": name,
                           "missing_terms": [], "detail": error})
            drift.append(check_id)
            continue
        terms = [str(term) for term in check["contains_all"]]
        missing = [term for term in terms if term not in text]
        outcome = PASS if not missing else DRIFT
        checks.append({"check_id": check_id, "outcome": outcome, "path": name,
                       "missing_terms": missing,
                       "detail": "all required terms are present" if outcome == PASS else "required terms are missing"})
        if outcome == DRIFT:
            drift.append(check_id)

    discovery = config["ci_discovery"]
    workflow_paths = [str(path) for path in discovery["workflow_paths"]]
    texts: list[str] = []
    errors: list[str] = []
    for name in workflow_paths:
        text, error = read_file(repository_root, name, files)
        if error or text is None:
            errors.append(error or f"cannot read {name}")
        else:
            texts.append(text)
    discovered, matched = ci_discovery(discovery, texts)
    if errors and not texts:
        ci_outcome, detail = DRIFT, "; ".join(errors)
    elif discovered:
        ci_outcome, detail = PASS, "contract regression test is discovered by executable CI"
    else:
        ci_outcome, detail = DRIFT, "no configured executable CI discovery rule matched"
    if ci_outcome == DRIFT:
        drift.append("ci_discovery")
    checks.append({"check_id": "ci_discovery", "outcome": ci_outcome,
                   "paths": workflow_paths, "matched_patterns": matched, "detail": detail})

    if drift:
        outcome, reason = DRIFT, "LOTUS_CONTRACT_DRIFT"
        detail = "non-conforming checks: " + ", ".join(sorted(set(drift)))
    else:
        outcome, reason = PASS, "LOTUS_CONTRACT_CONFORMANT"
        detail = "all configured Lotus Family invariants passed for the supplied snapshot and caller-provided identity claims"
    unique = {(row["path"], row["sha256"]): row for row in files}
    return result(outcome=outcome, reason_code=reason, detail=detail, repository=repository,
                  repository_id=repository_id, repository_ref=repository_ref, commit_sha=commit_sha,
                  manifest_schema=schema, checks=checks, files=list(unique.values()))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit one repository snapshot against the Lotus Family manifest.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--snapshot-root", type=Path, required=True)
    parser.add_argument("--repository-id", required=True)
    parser.add_argument("--repository-ref", required=True)
    parser.add_argument("--commit-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        audit = audit_repository(load_manifest(args.manifest), repository_id=args.repository_id,
                                 snapshot_root=args.snapshot_root, repository_ref=args.repository_ref,
                                 commit_sha=args.commit_sha)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        audit = manifest_invalid(str(exc), args.repository_id, args.repository_ref, args.commit_sha, "")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, sort_keys=True))
    return {PASS: 0, DRIFT: 2, UNKNOWN: 3}.get(audit["outcome"], 3)
