#!/usr/bin/env python3
"""Build a deterministic, exact-head GPT-5.6 role-review request and evidence manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
PROFILE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
PINNED_REUSABLE_RE = re.compile(
    r"uses:\s*safal207/pythiaLabs/\.github/workflows/gpt56-review-fabric-v1\.yml@([0-9a-f]{40})"
)
EXPECTED_ROLES = [
    "causal_architect",
    "temporal_provenance",
    "adversarial_semantics",
    "authority_safety",
    "ci_reliability",
]
EXPECTED_CLAIM_KINDS = ["fact", "observation", "hypothesis"]
FORBIDDEN_ADAPTER_TOKENS = [
    "pull_request_target",
    "secrets: inherit",
    "contents: write",
    "issues: write",
    "pull-requests: write",
    "actions: write",
    "continue-on-error: true",
    "paths:",
    "paths-ignore:",
]


class ContractError(ValueError):
    """Raised when the profile, adapter, or exact-head binding is unsafe."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot load JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{path}: top-level JSON value must be an object")
    return value


def normalize_sha(value: str, *, label: str) -> str:
    normalized = value.strip().lower()
    if not SHA_RE.fullmatch(normalized):
        raise ContractError(f"{label} must be a full lowercase 40-character Git SHA")
    return normalized


def normalize_repository(value: str, *, label: str) -> str:
    normalized = value.strip()
    if not REPOSITORY_RE.fullmatch(normalized):
        raise ContractError(f"{label} must use owner/repository form")
    return normalized


def validate_registry(registry: dict[str, Any]) -> list[dict[str, Any]]:
    if registry.get("schema_version") != "gpt56-role-registry-v1":
        raise ContractError("unsupported role registry version")
    roles = registry.get("roles")
    if not isinstance(roles, list) or [item.get("id") for item in roles if isinstance(item, dict)] != EXPECTED_ROLES:
        raise ContractError("role registry must contain the five canonical roles in canonical order")
    for role in roles:
        if set(role) != {"id", "purpose", "required_questions"}:
            raise ContractError(f"role {role.get('id')!r} has an unexpected shape")
        if not isinstance(role["purpose"], str) or not role["purpose"].strip():
            raise ContractError(f"role {role['id']!r} requires a purpose")
        questions = role["required_questions"]
        if not isinstance(questions, list) or len(questions) < 2 or not all(isinstance(item, str) and item.strip() for item in questions):
            raise ContractError(f"role {role['id']!r} requires non-empty review questions")
    return roles


def validate_profile(profile: dict[str, Any], *, target_repository: str) -> None:
    expected_keys = {
        "schema_version",
        "repository",
        "profile_id",
        "required_roles",
        "required_claim_kinds",
        "focus",
        "authority",
    }
    if set(profile) != expected_keys:
        raise ContractError(f"profile keys must equal {sorted(expected_keys)}")
    if profile["schema_version"] != "gpt56-review-profile-v1":
        raise ContractError("unsupported profile schema_version")
    if profile["repository"] != target_repository:
        raise ContractError("profile repository does not match the caller repository")
    if not isinstance(profile["profile_id"], str) or not PROFILE_ID_RE.fullmatch(profile["profile_id"]):
        raise ContractError("profile_id has an invalid format")
    if profile["required_roles"] != EXPECTED_ROLES:
        raise ContractError("required_roles may not omit, duplicate, reorder, or rename canonical roles")
    if profile["required_claim_kinds"] != EXPECTED_CLAIM_KINDS:
        raise ContractError("claim taxonomy must distinguish fact, observation, and hypothesis")
    focus = profile["focus"]
    if not isinstance(focus, list) or not 1 <= len(focus) <= 12:
        raise ContractError("focus must contain between 1 and 12 items")
    if len(set(focus)) != len(focus) or not all(isinstance(item, str) and 3 <= len(item.strip()) <= 240 for item in focus):
        raise ContractError("focus items must be unique, bounded, non-empty strings")
    authority = profile["authority"]
    expected_authority = {
        "can_execute": False,
        "can_approve": False,
        "can_merge": False,
        "can_deploy": False,
    }
    if authority != expected_authority:
        raise ContractError("GPT-5.6 review roles are advisory only and may not gain operational authority")


def validate_adapter(adapter_path: Path, *, workflow_sha: str) -> None:
    try:
        text = adapter_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ContractError(f"cannot read caller adapter {adapter_path}: {exc}") from exc
    for token in FORBIDDEN_ADAPTER_TOKENS:
        if token in text:
            raise ContractError(f"caller adapter contains forbidden token: {token}")
    required_tokens = [
        "pull_request:",
        "push:",
        "permissions: {}",
        "contents: read",
        "profile_path: .gpt56/review-profile.json",
    ]
    for token in required_tokens:
        if token not in text:
            raise ContractError(f"caller adapter is missing required token: {token}")
    pins = PINNED_REUSABLE_RE.findall(text)
    if pins != [workflow_sha]:
        raise ContractError("caller adapter must reference this reusable workflow by its exact commit SHA")


def git_head(subject_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(subject_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError(f"cannot resolve subject HEAD: {exc}") from exc
    return normalize_sha(result.stdout, label="actual subject HEAD")


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(canonical_bytes(value))
    temporary.replace(path)


def digest(path: Path) -> dict[str, Any]:
    content = path.read_bytes()
    return {"path": path.name, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}


def build_outputs(
    *,
    subject_root: Path,
    profile_path: Path,
    registry_path: Path,
    adapter_path: Path,
    output_dir: Path,
    target_repository: str,
    source_repository: str,
    expected_sha: str,
    change_number: int,
    workflow_repository: str,
    workflow_sha: str,
) -> dict[str, Any]:
    target_repository = normalize_repository(target_repository, label="target repository")
    source_repository = normalize_repository(source_repository, label="source repository")
    workflow_repository = normalize_repository(workflow_repository, label="workflow repository")
    expected_sha = normalize_sha(expected_sha, label="expected subject SHA")
    workflow_sha = normalize_sha(workflow_sha, label="workflow SHA")
    if change_number < 0:
        raise ContractError("change number must be zero or positive")

    actual_sha = git_head(subject_root)
    if actual_sha != expected_sha:
        raise ContractError(f"stale checkout: expected {expected_sha}, got {actual_sha}")

    profile = load_json(profile_path)
    registry = load_json(registry_path)
    roles = validate_registry(registry)
    validate_profile(profile, target_repository=target_repository)
    validate_adapter(adapter_path, workflow_sha=workflow_sha)

    output_dir.mkdir(parents=True, exist_ok=True)
    exact_head = {
        "schema_version": "gpt56-exact-head-evidence-v1",
        "repository": target_repository,
        "source_repository": source_repository,
        "expected_sha": expected_sha,
        "actual_sha": actual_sha,
        "matched": True,
    }
    request = {
        "schema_version": "gpt56-review-request-v1",
        "subject": {
            "repository": target_repository,
            "source_repository": source_repository,
            "change_number": change_number,
            "exact_head_sha": expected_sha,
        },
        "standard": {
            "repository": workflow_repository,
            "workflow_sha": workflow_sha,
            "role_registry": "gpt56-role-registry-v1",
        },
        "profile": {
            "profile_id": profile["profile_id"],
            "focus": profile["focus"],
        },
        "roles": roles,
        "claim_taxonomy": EXPECTED_CLAIM_KINDS,
        "decision_codes": ["READY_FOR_HUMAN_REVIEW", "FIX_THEN_RERUN", "BLOCK", "WAIT_FOR_EVIDENCE"],
        "authority": profile["authority"],
        "trust_boundary": {
            "single_model_role_simulation_must_be_disclosed": True,
            "external_provider_substitute": False,
            "ai_output_authorizes_action": False,
            "ci_output_authorizes_merge": False,
            "human_maintainer_decision_required": True,
            "exact_head_required": True,
            "dissent_must_remain_visible": True,
        },
    }

    exact_path = output_dir / "exact-head.json"
    request_path = output_dir / "review-request.json"
    write_json(exact_path, exact_head)
    write_json(request_path, request)
    artifacts = [digest(exact_path), digest(request_path)]
    manifest = {
        "schema_version": "gpt56-ci-evidence-manifest-v1",
        "algorithm": "sha256",
        "repository": target_repository,
        "source_repository": source_repository,
        "tested_sha": expected_sha,
        "workflow_repository": workflow_repository,
        "workflow_sha": workflow_sha,
        "change_number": change_number,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "profile_sha256": hashlib.sha256(canonical_bytes(profile)).hexdigest(),
    }
    manifest_path = output_dir / "evidence-manifest.json"
    write_json(manifest_path, manifest)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject-root", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--target-repository", required=True)
    parser.add_argument("--source-repository", required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--change-number", type=int, default=0)
    parser.add_argument("--workflow-repository", required=True)
    parser.add_argument("--workflow-sha", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        manifest = build_outputs(
            subject_root=args.subject_root,
            profile_path=args.profile,
            registry_path=args.registry,
            adapter_path=args.adapter,
            output_dir=args.output_dir,
            target_repository=args.target_repository,
            source_repository=args.source_repository,
            expected_sha=args.expected_sha,
            change_number=args.change_number,
            workflow_repository=args.workflow_repository,
            workflow_sha=args.workflow_sha,
        )
    except ContractError as exc:
        raise SystemExit(f"GPT-5.6 Review Fabric failed closed: {exc}") from exc
    print(f"GPT-5.6 Review Fabric produced {manifest['artifact_count']} exact-head evidence files")


if __name__ == "__main__":
    main()
