"""Aggregate immutable Lotus CI observations into advisory causal memory."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from lotus_family_ci_observation import AUTHORITY_GRANTS, validate_observation

MEMORY_SCHEMA_VERSION = "lotus.ci_causal_memory.v0.1"
GRAPH_ID = "ci-causal-memory-v0.1"


def _canonical(value: object) -> str:
    """Return canonical JSON for deterministic equality and hashing."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _digest(parts: Iterable[object]) -> str:
    """Hash a canonical tuple for stable proposal identities."""
    return hashlib.sha256(_canonical(list(parts)).encode("utf-8")).hexdigest()


def _observation_sort_key(observation: Mapping[str, Any]) -> tuple[object, ...]:
    """Order observations by timestamp, run identity, and immutable ID."""
    temporal = observation["temporal"]
    return (
        temporal["observed_at"],
        int(temporal["workflow_run_id"]),
        temporal["workflow_run_attempt"],
        observation["observation_id"],
    )


def _context_key(observation: Mapping[str, Any]) -> tuple[str, ...]:
    """Return the stable spatial context used for temporal linking."""
    spatial = observation["spatial"]
    return (
        spatial["repository"],
        spatial["workflow"],
        spatial["job"],
        spatial["step"],
        spatial["command"],
    )


def _proposal(signature: Mapping[str, Any]) -> dict[str, Any]:
    """Create a deterministic advisory regression proposal for a recurrence."""
    digest = str(signature["digest"])
    proposal_id = f"proposal-{_digest(('add_regression_fixture', digest))}"
    count = int(signature["occurrence_count"])
    first_seen = str(signature["first_seen_in"])
    last_seen = str(signature["last_seen_in"])
    title = f"Add regression guard for repeated CI signature {digest[:12]}"
    body = (
        "A normalized CI failure signature recurred across immutable Lotus "
        f"observations.\n\n- Signature: `{digest}`\n"
        f"- Occurrences: {count}\n"
        f"- First seen: `{first_seen}`\n"
        f"- Last seen: `{last_seen}`\n\n"
        "Suggested human action: reproduce the failure, identify a confirmed "
        "cause, and add or strengthen a regression fixture. Correlation alone "
        "does not confirm causality. This proposal cannot modify CI, approve, "
        "merge, deploy, or close findings."
    )
    return {
        "proposal_id": proposal_id,
        "kind": "add_regression_fixture",
        "signature_digest": digest,
        "status": "advisory",
        "title": title,
        "body": body,
        "human_acceptance_required": True,
        "automatic_mutation_allowed": False,
    }


def aggregate_observations(
    observations: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build deterministic cross-run memory without confirming causal claims."""
    unique: dict[str, dict[str, Any]] = {}
    for raw in observations:
        normalized = json.loads(_canonical(raw))
        validate_observation(normalized)
        observation_id = normalized["observation_id"]
        existing = unique.get(observation_id)
        if existing is not None and _canonical(existing) != _canonical(normalized):
            raise ValueError(f"conflicting observation payload: {observation_id}")
        unique[observation_id] = normalized

    ordered = sorted(unique.values(), key=_observation_sort_key)
    temporal_edges: list[dict[str, str]] = []
    validation_links: list[dict[str, str]] = []

    by_context: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for observation in ordered:
        by_context[_context_key(observation)].append(observation)

    for context in sorted(by_context):
        sequence = by_context[context]
        for previous, current in zip(sequence, sequence[1:], strict=False):
            temporal_edges.append(
                {
                    "source": previous["observation_id"],
                    "target": current["observation_id"],
                    "relation": "preceded_by",
                }
            )
            previous_conclusion = previous["causal"]["conclusion"]
            current_conclusion = current["causal"]["conclusion"]
            if previous_conclusion != "success" and current_conclusion == "success":
                validation_links.append(
                    {
                        "source": previous["observation_id"],
                        "target": current["observation_id"],
                        "relation": "success_after_failure",
                        "state": "fix_correlated",
                        "cause_state": "unconfirmed",
                    }
                )

    signature_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for observation in ordered:
        signature = observation["causal"]["failure_signature"]
        if signature is None:
            continue
        signature_groups[signature["digest"]].append(observation)

    signatures: list[dict[str, Any]] = []
    for digest in sorted(signature_groups):
        group = signature_groups[digest]
        observation_ids = [item["observation_id"] for item in group]
        signatures.append(
            {
                "digest": digest,
                "algorithm": "sha256",
                "basis": group[0]["causal"]["failure_signature"]["basis"],
                "occurrence_count": len(group),
                "state": "repeated" if len(group) > 1 else "observed_once",
                "first_seen_in": observation_ids[0],
                "last_seen_in": observation_ids[-1],
                "observation_ids": observation_ids,
                "reason_codes": sorted(
                    {
                        item["causal"]["reason_code"]
                        for item in group
                        if item["causal"]["reason_code"] is not None
                    }
                ),
                "cause_state": "unconfirmed",
            }
        )

    proposals = [_proposal(row) for row in signatures if row["state"] == "repeated"]
    memory = {
        "schema_version": MEMORY_SCHEMA_VERSION,
        "graph_id": GRAPH_ID,
        "observation_count": len(ordered),
        "observation_ids": [row["observation_id"] for row in ordered],
        "temporal_edges": temporal_edges,
        "validation_links": validation_links,
        "signatures": signatures,
        "proposals": proposals,
        "learning": {
            "highest_confidence": (
                "repeated" if any(row["state"] == "repeated" for row in signatures)
                else "observed_once"
                if signatures
                else "no_failure_observed"
            ),
            "confirmed_cause_count": 0,
            "automatic_mutation_allowed": False,
        },
        "limitations": [
            "correlation_does_not_confirm_cause",
            "trusted_materialization_not_established",
            "human_acceptance_required_for_proposals",
        ],
        "authority": {
            "mode": "advisory_only",
            **{grant: False for grant in AUTHORITY_GRANTS},
        },
    }
    validate_memory(memory)
    return memory


def validate_memory(memory: Mapping[str, Any]) -> None:
    """Validate cross-run learning and authority invariants."""
    if memory.get("schema_version") != MEMORY_SCHEMA_VERSION:
        raise ValueError("memory schema_version mismatch")
    if memory.get("graph_id") != GRAPH_ID:
        raise ValueError("memory graph_id mismatch")
    observation_ids = memory.get("observation_ids")
    if not isinstance(observation_ids, list) or len(observation_ids) != len(
        set(observation_ids)
    ):
        raise ValueError("memory observation_ids must be a unique list")
    if memory.get("observation_count") != len(observation_ids):
        raise ValueError("memory observation_count mismatch")

    signatures = memory.get("signatures")
    proposals = memory.get("proposals")
    if not isinstance(signatures, list) or not isinstance(proposals, list):
        raise ValueError("memory signatures and proposals must be lists")
    for signature in signatures:
        if signature.get("cause_state") != "unconfirmed":
            raise ValueError("aggregated correlation cannot confirm a cause")
        count = signature.get("occurrence_count")
        state = signature.get("state")
        if not isinstance(count, int) or count < 1:
            raise ValueError("signature occurrence_count is invalid")
        expected = "repeated" if count > 1 else "observed_once"
        if state != expected:
            raise ValueError("signature state does not match occurrence_count")

    for proposal in proposals:
        if proposal.get("status") != "advisory":
            raise ValueError("proposal status must be advisory")
        if proposal.get("human_acceptance_required") is not True:
            raise ValueError("proposal requires human acceptance")
        if proposal.get("automatic_mutation_allowed") is not False:
            raise ValueError("proposal cannot mutate CI automatically")

    learning = memory.get("learning")
    if not isinstance(learning, Mapping):
        raise ValueError("memory learning must be a mapping")
    if learning.get("confirmed_cause_count") != 0:
        raise ValueError("aggregator cannot confirm causes")
    if learning.get("automatic_mutation_allowed") is not False:
        raise ValueError("memory cannot mutate CI automatically")

    authority = memory.get("authority")
    if not isinstance(authority, Mapping) or authority.get("mode") != "advisory_only":
        raise ValueError("memory authority mode must be advisory_only")
    for grant in AUTHORITY_GRANTS:
        if authority.get(grant) is not False:
            raise ValueError(f"memory authority grant must remain false: {grant}")


def _load_observations(paths: Iterable[Path]) -> list[Mapping[str, Any]]:
    """Load observation objects from JSON files."""
    observations: list[Mapping[str, Any]] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"observation file must contain an object: {path}")
        observations.append(payload)
    return observations


def main(argv: list[str] | None = None) -> int:
    """Aggregate observation files and optionally render draft issue proposals."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observation", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--proposal-dir", type=Path)
    args = parser.parse_args(argv)

    try:
        memory = aggregate_observations(_load_observations(args.observation))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"cannot aggregate CI causal memory: {exc}", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(memory, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if args.proposal_dir is not None:
        args.proposal_dir.mkdir(parents=True, exist_ok=True)
        for proposal in memory["proposals"]:
            path = args.proposal_dir / f"{proposal['proposal_id']}.md"
            path.write_text(
                f"# {proposal['title']}\n\n{proposal['body']}\n",
                encoding="utf-8",
            )

    print(json.dumps(memory, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
