"""Regression coverage for cross-run CI causal memory learning."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from lotus_family_ci_memory import (
    GRAPH_ID,
    MEMORY_SCHEMA_VERSION,
    aggregate_observations,
    main,
    validate_memory,
)
from lotus_family_ci_observation import AUTHORITY_GRANTS, build_observation

HERE = Path(__file__).resolve().parent
GRAPH_PATH = HERE.parent / "ci-memory" / "ci-causal-memory-graph-v0.1.json"
COMMAND = "python -m unittest discover -s standards/lotus-family/conformance -p 'test_*.py' -v"


def observation(
    *,
    run_id: str,
    commit: str,
    observed_at: str,
    conclusion: str,
    reason_code: str | None = None,
    attempt: int = 1,
) -> dict:
    return build_observation(
        repository="safal207/pythiaLabs",
        ref="agent/ci-causal-memory-v0-1",
        commit_sha=commit,
        workflow="Lotus Family conformance",
        workflow_run_id=run_id,
        workflow_run_attempt=attempt,
        job="conformance",
        step="Run Lotus Family conformance suite",
        command=COMMAND,
        test_target="standards/lotus-family/conformance/test_*.py",
        conclusion=conclusion,
        reason_code=reason_code,
        changed_paths=[],
        runner_os="Linux",
        runner_arch="X64",
        python_version="3.12.13",
        observed_at=observed_at,
    )


class CiMemoryTest(unittest.TestCase):
    """Keep recurrence learning deterministic, advisory, and graph-bound."""

    def test_graph_routes_use_existing_nodes_and_edges(self) -> None:
        graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
        self.assertEqual(graph["graph_id"], GRAPH_ID)
        node_ids = [row[0] for row in graph["nodes"]]
        edge_ids = [row[0] for row in graph["edges"]]
        self.assertEqual(len(node_ids), len(set(node_ids)))
        self.assertEqual(len(edge_ids), len(set(edge_ids)))

        node_set = set(node_ids)
        edge_pairs = {(row[1], row[2]) for row in graph["edges"]}
        for edge in graph["edges"]:
            self.assertIn(edge[1], node_set)
            self.assertIn(edge[2], node_set)
        for trajectory in graph["trajectories"]:
            path = trajectory["path"]
            self.assertGreaterEqual(len(path), 2)
            for source, target in zip(path, path[1:], strict=False):
                self.assertIn(
                    (source, target),
                    edge_pairs,
                    msg=f"route gap in {trajectory['id']}: {source} -> {target}",
                )

        invariants = graph["invariants"]
        self.assertTrue(invariants["correlation_is_not_confirmation"])
        self.assertFalse(invariants["automatic_mutation_allowed"])
        self.assertTrue(invariants["human_acceptance_required"])

    def test_repeated_signature_creates_one_advisory_proposal(self) -> None:
        first = observation(
            run_id="29660131336",
            commit="a" * 40,
            observed_at="2026-07-18T20:39:58Z",
            conclusion="failure",
            reason_code="UNITTEST_FAILURE",
        )
        second = observation(
            run_id="29660140000",
            commit="b" * 40,
            observed_at="2026-07-18T20:45:00Z",
            conclusion="failure",
            reason_code="UNITTEST_FAILURE",
        )

        memory = aggregate_observations([second, first])

        self.assertEqual(memory["schema_version"], MEMORY_SCHEMA_VERSION)
        self.assertEqual(memory["observation_count"], 2)
        self.assertEqual(len(memory["signatures"]), 1)
        signature = memory["signatures"][0]
        self.assertEqual(signature["occurrence_count"], 2)
        self.assertEqual(signature["state"], "repeated")
        self.assertEqual(signature["cause_state"], "unconfirmed")
        self.assertEqual(len(memory["proposals"]), 1)
        proposal = memory["proposals"][0]
        self.assertEqual(proposal["status"], "advisory")
        self.assertTrue(proposal["human_acceptance_required"])
        self.assertFalse(proposal["automatic_mutation_allowed"])
        self.assertIn(signature["digest"], proposal["body"])
        self.assertEqual(memory["learning"]["confirmed_cause_count"], 0)
        validate_memory(memory)

    def test_failure_then_success_is_only_fix_correlated(self) -> None:
        failure = observation(
            run_id="29660131336",
            commit="a" * 40,
            observed_at="2026-07-18T20:39:58Z",
            conclusion="failure",
            reason_code="IMPORT_ERROR",
        )
        success = observation(
            run_id="29660150000",
            commit="c" * 40,
            observed_at="2026-07-18T20:50:00Z",
            conclusion="success",
        )

        memory = aggregate_observations([success, failure])

        self.assertEqual(len(memory["temporal_edges"]), 1)
        self.assertEqual(len(memory["validation_links"]), 1)
        link = memory["validation_links"][0]
        self.assertEqual(link["relation"], "success_after_failure")
        self.assertEqual(link["state"], "fix_correlated")
        self.assertEqual(link["cause_state"], "unconfirmed")
        self.assertEqual(memory["learning"]["confirmed_cause_count"], 0)
        self.assertEqual(len(memory["proposals"]), 0)

    def test_mixed_offsets_are_ordered_by_instant(self) -> None:
        later = observation(
            run_id="2",
            commit="b" * 40,
            observed_at="2026-07-18T10:00:00-05:00",
            conclusion="success",
        )
        earlier = observation(
            run_id="1",
            commit="a" * 40,
            observed_at="2026-07-18T14:30:00Z",
            conclusion="success",
        )

        memory = aggregate_observations([later, earlier])

        self.assertEqual(
            memory["observation_ids"],
            [earlier["observation_id"], later["observation_id"]],
        )
        self.assertEqual(
            memory["temporal_edges"],
            [
                {
                    "source": earlier["observation_id"],
                    "target": later["observation_id"],
                    "relation": "preceded_by",
                }
            ],
        )

    def test_distinct_signatures_do_not_create_recurrence(self) -> None:
        first = observation(
            run_id="1",
            commit="a" * 40,
            observed_at="2026-07-18T20:00:00Z",
            conclusion="failure",
            reason_code="IMPORT_ERROR",
        )
        second = observation(
            run_id="2",
            commit="b" * 40,
            observed_at="2026-07-18T20:01:00Z",
            conclusion="failure",
            reason_code="ASSERTION_FAILURE",
        )

        memory = aggregate_observations([first, second])

        self.assertEqual(len(memory["signatures"]), 2)
        self.assertTrue(
            all(row["state"] == "observed_once" for row in memory["signatures"])
        )
        self.assertEqual(memory["proposals"], [])

    def test_duplicate_observation_is_deduplicated_and_conflict_rejected(self) -> None:
        first = observation(
            run_id="1",
            commit="a" * 40,
            observed_at="2026-07-18T20:00:00Z",
            conclusion="failure",
            reason_code="IMPORT_ERROR",
        )
        memory = aggregate_observations([first, copy.deepcopy(first)])
        self.assertEqual(memory["observation_count"], 1)

        conflicting = copy.deepcopy(first)
        conflicting["limitations"].append("conflicting_copy")
        with self.assertRaisesRegex(ValueError, "conflicting observation payload"):
            aggregate_observations([first, conflicting])

    def test_memory_preserves_full_authority_boundary(self) -> None:
        memory = aggregate_observations([])
        self.assertEqual(memory["authority"]["mode"], "advisory_only")
        for grant in AUTHORITY_GRANTS:
            self.assertFalse(memory["authority"][grant])
        self.assertFalse(memory["learning"]["automatic_mutation_allowed"])
        self.assertEqual(memory["learning"]["confirmed_cause_count"], 0)

    def test_cli_writes_memory_and_draft_proposal(self) -> None:
        first = observation(
            run_id="1",
            commit="a" * 40,
            observed_at="2026-07-18T20:00:00Z",
            conclusion="failure",
            reason_code="UNITTEST_FAILURE",
        )
        second = observation(
            run_id="2",
            commit="b" * 40,
            observed_at="2026-07-18T20:01:00Z",
            conclusion="failure",
            reason_code="UNITTEST_FAILURE",
        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_path = root / "first.json"
            second_path = root / "second.json"
            output = root / "memory.json"
            proposal_dir = root / "proposals"
            first_path.write_text(json.dumps(first), encoding="utf-8")
            second_path.write_text(json.dumps(second), encoding="utf-8")

            exit_code = main(
                [
                    "--observation",
                    str(second_path),
                    "--observation",
                    str(first_path),
                    "--output",
                    str(output),
                    "--proposal-dir",
                    str(proposal_dir),
                ]
            )
            memory = json.loads(output.read_text(encoding="utf-8"))
            proposal_files = sorted(proposal_dir.glob("proposal-*.md"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(memory["observation_count"], 2)
        self.assertEqual(len(memory["proposals"]), 1)
        self.assertEqual(len(proposal_files), 1)
        validate_memory(memory)


if __name__ == "__main__":
    unittest.main()
