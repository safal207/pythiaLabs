"""Executable checks for the original Lotus causal route model."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from lotus_family_auditor import (
    DRIFT,
    PASS,
    UNKNOWN,
    audit_repository,
    load_manifest,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MANIFEST_PATH = ROOT / "manifest" / "lotus-family-v0.1.json"
GRAPH_PATH = (
    ROOT / "causality" / "lotus-family-causality-v0.1.json"
)
ROUTES_PATH = ROOT / "causality" / "test-paths-v0.1.json"
TRACEABILITY_PATH = ROOT / "causality" / "TRACEABILITY.md"
SHA = "a" * 40
AUTHORITY_GRANTS = (
    "grants_ownership",
    "grants_approval",
    "grants_execution",
    "grants_delivery",
    "grants_merge",
)


def _write(
    root: Path, relative_path: str, content: str
) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _workflow(command: str) -> str:
    body = "\n".join(
        f"          {line}" if line else ""
        for line in command.splitlines()
    )
    return (
        "name: CI\n"
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - name: Run tests\n"
        "        run: |\n"
        f"{body}\n"
    )


def _valid_command(discovery: dict) -> str:
    strategy = discovery["strategy"]
    if strategy == "pytest_default_discovery":
        return (
            "python -m pytest \\\n"
            "  --junitxml=artifacts/junit.xml \\\n"
            "  --cov=cml \\\n"
            "  --cov-fail-under=70"
        )
    if strategy == "mix_default_discovery":
        return "mix test"
    pattern = discovery["contains_any"][0]
    if pattern.endswith(".py"):
        return f"python -m pytest {pattern}"
    if pattern.endswith(".exs"):
        return f"mix test {pattern}"
    return pattern


def _materialize(
    snapshot_root: Path,
    config: dict,
    workflow: str | None = None,
) -> Path:
    repository_root = snapshot_root / config["snapshot_dir"]
    terms_by_path: dict[str, list[str]] = {}
    for check in config["file_checks"]:
        terms_by_path.setdefault(check["path"], []).extend(
            check["contains_all"]
        )
    for relative_path, terms in terms_by_path.items():
        _write(
            repository_root,
            relative_path,
            "\n".join(dict.fromkeys(terms)) + "\n",
        )
    discovery = config["ci_discovery"]
    _write(
        repository_root,
        discovery["workflow_paths"][0],
        (
            workflow
            if workflow is not None
            else _workflow(_valid_command(discovery))
        ),
    )
    return repository_root


class CausalityModelTest(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = load_manifest(MANIFEST_PATH)
        self.graph = json.loads(
            GRAPH_PATH.read_text(encoding="utf-8")
        )
        self.routes = json.loads(
            ROUTES_PATH.read_text(encoding="utf-8")
        )["routes"]

    def config(self, repository_id: str) -> dict:
        return next(
            row
            for row in self.manifest["repositories"]
            if row["id"] == repository_id
        )

    def test_graph_has_unique_nodes_edges_and_no_dangling_references(
        self,
    ) -> None:
        node_ids = [
            node["id"] for node in self.graph["nodes"]
        ]
        edge_ids = [
            edge["id"] for edge in self.graph["edges"]
        ]
        self.assertEqual(len(node_ids), len(set(node_ids)))
        self.assertEqual(len(edge_ids), len(set(edge_ids)))
        known = set(node_ids)
        for edge in self.graph["edges"]:
            self.assertIn(edge["source"], known)
            self.assertIn(edge["target"], known)

    def test_graph_is_acyclic(self) -> None:
        adjacency: dict[str, list[str]] = {}
        for edge in self.graph["edges"]:
            adjacency.setdefault(
                edge["source"], []
            ).append(edge["target"])
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visiting:
                self.fail(
                    "causality graph contains a cycle "
                    f"at {node}"
                )
            if node in visited:
                return
            visiting.add(node)
            for target in adjacency.get(node, []):
                visit(target)
            visiting.remove(node)
            visited.add(node)

        for node in {
            row["id"] for row in self.graph["nodes"]
        }:
            visit(node)

    def test_every_route_is_a_connected_graph_path(
        self,
    ) -> None:
        edges = {
            (edge["source"], edge["target"])
            for edge in self.graph["edges"]
        }
        route_ids: set[str] = set()
        for route in self.routes:
            self.assertNotIn(route["id"], route_ids)
            route_ids.add(route["id"])
            path = route["path"]
            self.assertGreaterEqual(len(path), 2)
            for source, target in zip(path, path[1:]):
                self.assertIn(
                    (source, target), edges, route["id"]
                )

    def test_required_graph_nodes_are_covered_by_routes(
        self,
    ) -> None:
        required_types = set(
            self.graph["coverage_policy"][
                "required_node_types"
            ]
        )
        required_nodes = {
            node["id"]
            for node in self.graph["nodes"]
            if node["type"] in required_types
        }
        covered = {
            node
            for route in self.routes
            for node in route["path"]
        }
        self.assertEqual(required_nodes - covered, set())

    def test_traceability_names_every_executable_route(
        self,
    ) -> None:
        traceability = TRACEABILITY_PATH.read_text(
            encoding="utf-8"
        )
        for route in self.routes:
            self.assertIn(
                f"`{route['id']}`", traceability
            )

    def test_causal_routes_execute_to_their_expected_outcomes(
        self,
    ) -> None:
        for route in self.routes:
            with self.subTest(route=route["id"]):
                scenario = route["scenario"]
                repository_id = route["repository_id"]
                manifest = copy.deepcopy(self.manifest)
                commit_sha = scenario.get(
                    "commit_sha", SHA
                )
                with tempfile.TemporaryDirectory() as directory:
                    snapshot_root = Path(directory)
                    if scenario["kind"] != "missing_snapshot":
                        config = next(
                            row
                            for row in manifest["repositories"]
                            if row["id"] == repository_id
                        )
                        workflow = scenario.get("workflow")
                        repository_root = _materialize(
                            snapshot_root, config, workflow
                        )
                        if scenario["kind"] == "missing_term":
                            check = config["file_checks"][0]
                            path = (
                                repository_root / check["path"]
                            )
                            path.write_text(
                                path.read_text(
                                    encoding="utf-8"
                                ).replace(
                                    check["contains_all"][0],
                                    "",
                                ),
                                encoding="utf-8",
                            )
                        elif (
                            scenario["kind"]
                            == "invalid_manifest"
                        ):
                            config["file_checks"][0][
                                "contains_all"
                            ] = []

                    result = audit_repository(
                        manifest,
                        repository_id=repository_id,
                        snapshot_root=snapshot_root,
                        repository_ref="refs/heads/main",
                        commit_sha=commit_sha,
                    )
                    self.assertEqual(
                        result["outcome"],
                        route["expected"]["outcome"],
                    )
                    self.assertEqual(
                        result["reason_code"],
                        route["expected"]["reason_code"],
                    )
                    identity_mode = scenario.get(
                        "assert_identity_mode"
                    )
                    if identity_mode is not None:
                        self.assertEqual(
                            result["identity_assurance"][
                                "mode"
                            ],
                            identity_mode,
                        )
                    for grant in AUTHORITY_GRANTS:
                        self.assertFalse(
                            result["authority"][grant],
                            f"{route['id']} granted {grant}",
                        )


if __name__ == "__main__":
    unittest.main()
