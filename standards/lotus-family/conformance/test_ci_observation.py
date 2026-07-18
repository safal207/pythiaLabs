"""Regression coverage for immutable CI causal observation artifacts."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from lotus_family_ci_observation import (
    AUTHORITY_GRANTS,
    SCHEMA_VERSION,
    build_observation,
    main,
    validate_observation,
)

HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE.parent / "ci-memory" / "ci-causal-observation-v0.1.schema.json"
SHA_A = "a" * 40
SHA_B = "b" * 40
OBSERVED_AT = "2026-07-18T20:30:00Z"
COMMAND = (
    "python -m unittest discover -s standards/lotus-family/conformance "
    "-p 'test_*.py' -v"
)


def observation(**overrides: object) -> dict:
    values: dict[str, object] = {
        "repository": "safal207/pythiaLabs",
        "ref": "refs/pull/233/merge",
        "commit_sha": SHA_A,
        "workflow": "Lotus Family conformance",
        "workflow_run_id": "29660000000",
        "workflow_run_attempt": 1,
        "job": "conformance",
        "step": "Run Lotus Family conformance suite",
        "command": COMMAND,
        "test_target": "standards/lotus-family/conformance/test_*.py",
        "conclusion": "success",
        "reason_code": None,
        "changed_paths": [
            "standards/lotus-family/conformance/test_ci_observation.py",
            "standards/lotus-family/ci-memory/SCHEMA.md",
        ],
        "runner_os": "Linux",
        "runner_arch": "X64",
        "python_version": "3.12.4",
        "observed_at": OBSERVED_AT,
        "predecessor_observation_id": None,
    }
    values.update(overrides)
    return build_observation(**values)  # type: ignore[arg-type]


class CiObservationTest(unittest.TestCase):
    """Protect deterministic identity, causal uncertainty, and authority limits."""

    def test_schema_declares_closed_required_sections(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            schema["properties"]["schema_version"]["const"],
            SCHEMA_VERSION,
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            set(schema["required"]),
            {
                "schema_version",
                "observation_id",
                "spatial",
                "temporal",
                "causal",
                "evidence",
                "learning",
                "limitations",
                "authority",
            },
        )

    def test_success_observation_is_deterministic_and_advisory(self) -> None:
        first = observation()
        second = observation(changed_paths=reversed(first["spatial"]["changed_paths"]))

        self.assertEqual(first, second)
        self.assertIsNone(first["causal"]["failure_signature"])
        self.assertEqual(first["causal"]["cause_state"], "unconfirmed")
        self.assertEqual(first["learning"]["confidence"], "observed_once")
        self.assertFalse(first["learning"]["automatic_mutation_allowed"])
        self.assertEqual(first["authority"]["mode"], "advisory_only")
        for grant in AUTHORITY_GRANTS:
            self.assertFalse(first["authority"][grant])
        validate_observation(first)

    def test_failure_signature_repeats_across_run_and_commit_identity(self) -> None:
        first = observation(
            conclusion="failure",
            reason_code="UNITTEST_FAILURE",
        )
        second = observation(
            commit_sha=SHA_B,
            workflow_run_id="29660000001",
            workflow_run_attempt=2,
            observed_at="2026-07-18T20:35:00Z",
            conclusion="failure",
            reason_code="UNITTEST_FAILURE",
        )

        self.assertNotEqual(first["observation_id"], second["observation_id"])
        self.assertEqual(
            first["causal"]["failure_signature"],
            second["causal"]["failure_signature"],
        )
        self.assertEqual(first["causal"]["cause_state"], "unconfirmed")
        self.assertEqual(second["causal"]["cause_state"], "unconfirmed")

    def test_failure_signature_changes_with_reason_code(self) -> None:
        first = observation(conclusion="failure", reason_code="IMPORT_ERROR")
        second = observation(conclusion="failure", reason_code="ASSERTION_FAILURE")
        self.assertNotEqual(
            first["causal"]["failure_signature"]["digest"],
            second["causal"]["failure_signature"]["digest"],
        )

    def test_rejects_unsafe_changed_paths_and_invalid_commit(self) -> None:
        with self.assertRaisesRegex(ValueError, "escapes repository"):
            observation(changed_paths=["../secret.txt"])
        with self.assertRaisesRegex(ValueError, "40 hexadecimal"):
            observation(commit_sha="main")

    def test_cli_writes_one_valid_observation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "observation.json"
            exit_code = main(
                [
                    "--repository",
                    "safal207/pythiaLabs",
                    "--ref",
                    "refs/pull/233/merge",
                    "--commit-sha",
                    SHA_A,
                    "--workflow",
                    "Lotus Family conformance",
                    "--workflow-run-id",
                    "29660000000",
                    "--workflow-run-attempt",
                    "1",
                    "--job",
                    "conformance",
                    "--step",
                    "Run Lotus Family conformance suite",
                    "--command",
                    COMMAND,
                    "--test-target",
                    "standards/lotus-family/conformance/test_*.py",
                    "--conclusion",
                    "failure",
                    "--reason-code",
                    "UNITTEST_FAILURE",
                    "--runner-os",
                    "Linux",
                    "--runner-arch",
                    "X64",
                    "--python-version",
                    "3.12.4",
                    "--observed-at",
                    OBSERVED_AT,
                    "--output",
                    str(output),
                ]
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["schema_version"], SCHEMA_VERSION)
        self.assertEqual(payload["causal"]["conclusion"], "failure")
        self.assertIsNotNone(payload["causal"]["failure_signature"])
        self.assertIn("changed_paths_unavailable", payload["limitations"])
        validate_observation(payload)


if __name__ == "__main__":
    unittest.main()
