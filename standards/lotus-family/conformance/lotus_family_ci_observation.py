"""Emit deterministic, advisory CI causal observations for Lotus Family runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

SCHEMA_VERSION = "lotus.ci_causal_observation.v0.1"
EMITTER_VERSION = "0.1"
ALLOWED_CONCLUSIONS = {"success", "failure", "cancelled", "skipped", "unknown"}
AUTHORITY_GRANTS = (
    "ownership",
    "approval",
    "execution",
    "delivery",
    "deployment",
    "merge",
)
_HEX_40 = re.compile(r"^[0-9a-f]{40}$")
_HEX_64 = re.compile(r"^[0-9a-f]{64}$")
_OBSERVATION_ID = re.compile(r"^obs-[0-9a-f]{64}$")


def _required_text(value: object, field: str) -> str:
    """Return a stripped non-empty string or raise a stable validation error."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _commit_sha(value: object) -> str:
    """Normalize and validate an exact 40-character commit SHA claim."""
    normalized = _required_text(value, "commit_sha").lower()
    if not _HEX_40.fullmatch(normalized):
        raise ValueError("commit_sha must be exactly 40 hexadecimal characters")
    return normalized


def _timestamp(value: object) -> str:
    """Validate an RFC3339 timestamp with an explicit timezone."""
    text = _required_text(value, "observed_at")
    candidate = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError("observed_at must be an RFC3339 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError("observed_at must include a timezone")
    return text


def _safe_paths(values: Iterable[str]) -> list[str]:
    """Normalize repository-relative changed paths without traversal."""
    normalized: set[str] = set()
    for raw in values:
        value = _required_text(raw, "changed_path").replace("\\", "/")
        path = PurePosixPath(value)
        if path.is_absolute() or ".." in path.parts or path == PurePosixPath("."):
            raise ValueError(f"changed_path escapes repository: {value}")
        normalized.add(path.as_posix())
    return sorted(normalized)


def _digest(parts: Iterable[object]) -> str:
    """Hash a canonical JSON tuple without timestamps or secret-bearing logs."""
    payload = json.dumps(
        list(parts),
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _optional_text(value: object) -> str | None:
    """Return a stripped optional string."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("optional text fields must be strings or null")
    stripped = value.strip()
    return stripped or None


def build_observation(
    *,
    repository: str,
    ref: str,
    commit_sha: str,
    workflow: str,
    workflow_run_id: str,
    workflow_run_attempt: int,
    job: str,
    step: str,
    command: str,
    test_target: str | None,
    conclusion: str,
    reason_code: str | None,
    changed_paths: Iterable[str],
    runner_os: str | None,
    runner_arch: str | None,
    python_version: str | None,
    observed_at: str,
    predecessor_observation_id: str | None = None,
) -> dict[str, Any]:
    """Build one immutable observation with separate run and failure identities."""
    repository_value = _required_text(repository, "repository")
    ref_value = _required_text(ref, "ref")
    sha_value = _commit_sha(commit_sha)
    workflow_value = _required_text(workflow, "workflow")
    run_id_value = _required_text(workflow_run_id, "workflow_run_id")
    if not run_id_value.isdigit():
        raise ValueError("workflow_run_id must contain only digits")
    if not isinstance(workflow_run_attempt, int) or workflow_run_attempt < 1:
        raise ValueError("workflow_run_attempt must be a positive integer")
    job_value = _required_text(job, "job")
    step_value = _required_text(step, "step")
    command_value = _required_text(command, "command")
    conclusion_value = _required_text(conclusion, "conclusion").lower()
    if conclusion_value not in ALLOWED_CONCLUSIONS:
        raise ValueError(f"unsupported conclusion: {conclusion_value}")
    reason_value = _optional_text(reason_code)
    target_value = _optional_text(test_target)
    observed_value = _timestamp(observed_at)
    changed_values = _safe_paths(changed_paths)

    predecessor_value = _optional_text(predecessor_observation_id)
    if predecessor_value is not None and not _OBSERVATION_ID.fullmatch(
        predecessor_value
    ):
        raise ValueError("predecessor_observation_id is invalid")

    observation_digest = _digest(
        (
            SCHEMA_VERSION,
            repository_value,
            ref_value,
            sha_value,
            workflow_value,
            run_id_value,
            workflow_run_attempt,
            job_value,
            step_value,
        )
    )

    failure_signature: dict[str, str] | None = None
    if conclusion_value != "success":
        failure_signature = {
            "algorithm": "sha256",
            "digest": _digest(
                (
                    SCHEMA_VERSION,
                    repository_value,
                    workflow_value,
                    job_value,
                    step_value,
                    command_value,
                    conclusion_value,
                    reason_value or "",
                )
            ),
            "basis": (
                "schema_version|repository|workflow|job|step|command|"
                "conclusion|reason_code"
            ),
        }

    limitations = [
        "repository_ref_and_commit_are_platform_or_caller_claims",
        "raw_logs_are_not_persisted",
        "cross_run_cause_is_not_confirmed",
    ]
    if not changed_values:
        limitations.append("changed_paths_unavailable")
    if predecessor_value is None:
        limitations.append("predecessor_not_linked")

    observation = {
        "schema_version": SCHEMA_VERSION,
        "observation_id": f"obs-{observation_digest}",
        "spatial": {
            "repository": repository_value,
            "ref": ref_value,
            "commit_sha": sha_value,
            "workflow": workflow_value,
            "job": job_value,
            "step": step_value,
            "command": command_value,
            "test_target": target_value,
            "changed_paths": changed_values,
        },
        "temporal": {
            "workflow_run_id": run_id_value,
            "workflow_run_attempt": workflow_run_attempt,
            "observed_at": observed_value,
            "predecessor_observation_id": predecessor_value,
        },
        "causal": {
            "conclusion": conclusion_value,
            "reason_code": reason_value,
            "failure_signature": failure_signature,
            "cause_state": "unconfirmed",
        },
        "evidence": {
            "command_sha256": hashlib.sha256(
                command_value.encode("utf-8")
            ).hexdigest(),
            "detector_versions": {
                "lotus_ci_observation": EMITTER_VERSION,
                "lotus_workflow_policy": "v3",
            },
            "environment_fingerprint": {
                "runner_os": _optional_text(runner_os),
                "runner_arch": _optional_text(runner_arch),
                "python_version": _optional_text(python_version),
            },
        },
        "learning": {
            "confidence": "observed_once",
            "proposal_allowed": True,
            "automatic_mutation_allowed": False,
        },
        "limitations": sorted(limitations),
        "authority": {
            "mode": "advisory_only",
            **{grant: False for grant in AUTHORITY_GRANTS},
        },
    }
    validate_observation(observation)
    return observation


def validate_observation(observation: Mapping[str, Any]) -> None:
    """Validate the invariants required before an observation can be emitted."""
    if observation.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("schema_version mismatch")
    observation_id = observation.get("observation_id")
    if not isinstance(observation_id, str) or not _OBSERVATION_ID.fullmatch(
        observation_id
    ):
        raise ValueError("observation_id is invalid")

    spatial = observation.get("spatial")
    temporal = observation.get("temporal")
    causal = observation.get("causal")
    evidence = observation.get("evidence")
    learning = observation.get("learning")
    authority = observation.get("authority")
    if not all(
        isinstance(section, Mapping)
        for section in (spatial, temporal, causal, evidence, learning, authority)
    ):
        raise ValueError("observation sections must be mappings")

    assert isinstance(spatial, Mapping)
    if not _HEX_40.fullmatch(str(spatial.get("commit_sha", ""))):
        raise ValueError("spatial.commit_sha is invalid")
    _safe_paths(spatial.get("changed_paths", []))

    assert isinstance(temporal, Mapping)
    if not str(temporal.get("workflow_run_id", "")).isdigit():
        raise ValueError("temporal.workflow_run_id is invalid")
    if not isinstance(temporal.get("workflow_run_attempt"), int):
        raise ValueError("temporal.workflow_run_attempt is invalid")
    _timestamp(temporal.get("observed_at"))

    assert isinstance(causal, Mapping)
    conclusion = causal.get("conclusion")
    if conclusion not in ALLOWED_CONCLUSIONS:
        raise ValueError("causal.conclusion is invalid")
    signature = causal.get("failure_signature")
    if conclusion == "success" and signature is not None:
        raise ValueError("successful observations cannot have a failure signature")
    if conclusion != "success":
        if not isinstance(signature, Mapping) or not _HEX_64.fullmatch(
            str(signature.get("digest", ""))
        ):
            raise ValueError("non-success observations require a failure signature")
    if causal.get("cause_state") != "unconfirmed":
        raise ValueError("single-run observations cannot confirm a cause")

    assert isinstance(evidence, Mapping)
    if not _HEX_64.fullmatch(str(evidence.get("command_sha256", ""))):
        raise ValueError("evidence.command_sha256 is invalid")

    assert isinstance(learning, Mapping)
    if learning.get("confidence") != "observed_once":
        raise ValueError("single-run confidence must be observed_once")
    if learning.get("proposal_allowed") is not True:
        raise ValueError("advisory proposals must remain available")
    if learning.get("automatic_mutation_allowed") is not False:
        raise ValueError("automatic mutation is forbidden")

    assert isinstance(authority, Mapping)
    if authority.get("mode") != "advisory_only":
        raise ValueError("authority mode must be advisory_only")
    for grant in AUTHORITY_GRANTS:
        if authority.get(grant) is not False:
            raise ValueError(f"authority grant must remain false: {grant}")


def _now() -> str:
    """Return an RFC3339 UTC timestamp at second precision."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def main(argv: list[str] | None = None) -> int:
    """Write one schema-valid CI causal observation JSON artifact."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--commit-sha", required=True)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--workflow-run-id", required=True)
    parser.add_argument("--workflow-run-attempt", type=int, required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--step", required=True)
    parser.add_argument("--command", required=True)
    parser.add_argument("--test-target")
    parser.add_argument("--conclusion", required=True)
    parser.add_argument("--reason-code")
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--runner-os")
    parser.add_argument("--runner-arch")
    parser.add_argument("--python-version")
    parser.add_argument("--observed-at", default=None)
    parser.add_argument("--predecessor-observation-id")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        observation = build_observation(
            repository=args.repository,
            ref=args.ref,
            commit_sha=args.commit_sha,
            workflow=args.workflow,
            workflow_run_id=args.workflow_run_id,
            workflow_run_attempt=args.workflow_run_attempt,
            job=args.job,
            step=args.step,
            command=args.command,
            test_target=args.test_target,
            conclusion=args.conclusion,
            reason_code=args.reason_code,
            changed_paths=args.changed_path,
            runner_os=args.runner_os,
            runner_arch=args.runner_arch,
            python_version=args.python_version,
            observed_at=args.observed_at or _now(),
            predecessor_observation_id=args.predecessor_observation_id,
        )
    except ValueError as exc:
        print(f"invalid CI causal observation: {exc}", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(observation, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(observation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
