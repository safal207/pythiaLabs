"""Executable validation for the Lotus causal spacetime system model."""

from __future__ import annotations

import copy
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
from lotus_family_system_model import (
    centrality_report,
    load,
    traceability,
    validate_graph,
    validate_routes,
)
from lotus_family_test_sources import pinned_test_source

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
GRAPH = ROOT / "causality" / "lotus-family-system-v0.1.json"
ROUTES = ROOT / "causality" / "system-routes-v0.1.json"
MANIFEST = ROOT / "manifest" / "lotus-family-v0.1.json"
SHA = "a" * 40
AUTHORITY_GRANTS = (
    "grants_ownership",
    "grants_approval",
    "grants_execution",
    "grants_delivery",
    "grants_merge",
)


def workflow(
    command: str,
    *,
    workflow_extra: str = "",
    job_extra: str = "",
    step_extra: str = "",
    prefix_jobs: str = "",
) -> str:
    """Build a small GitHub Actions workflow fixture."""
    body = "\n".join(
        f"          {line}" if line else ""
        for line in command.splitlines()
    )
    return (
        "name: CI\n"
        "on: push\n"
        f"{workflow_extra}"
        "jobs:\n"
        f"{prefix_jobs}"
        "  test:\n"
        "    runs-on: ubuntu-latest\n"
        f"{job_extra}"
        "    steps:\n"
        "      - name: Run tests\n"
        f"{step_extra}"
        "        run: |\n"
        f"{body}\n"
    )


SCENARIOS = {
    "ci-nonrun-001": (
        "name: CI\n"
        "on: push\n"
        "env:\n"
        "  NOTE: python -m pytest\n"
        "jobs: {}\n"
    ),
    "ci-step-skip-001": workflow(
        "python -m pytest",
        step_extra="        if: ${{ false }}\n",
    ),
    "ci-job-skip-001": workflow(
        "python -m pytest",
        job_extra="    if: ${{ false }}\n",
    ),
    "ci-no-runner-001": (
        "name: CI\n"
        "on: push\n"
        "jobs:\n"
        "  test:\n"
        "    steps:\n"
        "      - run: python -m pytest\n"
    ),
    "ci-quoted-env-001": (
        'name: CI\n'
        'env:\n'
        '  "PYTEST_ADDOPTS": '
        '"--ignore=tests/test_lotus_docs_contract.py"\n'
        'jobs:\n'
        '  test:\n'
        '    runs-on: ubuntu-latest\n'
        '    steps:\n'
        '      - run: python -m pytest\n'
    ),
    "ci-shell-control-001": workflow(
        "if false; then\n  python -m pytest\nfi"
    ),
    "cml-subset-001": workflow(
        "python -m pytest tests/test_other.py"
    ),
    "pythia-subset-001": workflow(
        "mix test test/unrelated_test.exs"
    ),
    "ci-fake-steps-001": (
        "name: CI\n"
        "on: push\n"
        "metadata:\n"
        "  fake:\n"
        "    steps:\n"
        "      - run: python -m pytest\n"
        "jobs: {}\n"
    ),
    "ci-custom-shell-001": workflow(
        "python -m pytest",
        step_extra="        shell: cat {0}\n",
    ),
    "ci-shell-noexec-001": workflow(
        "python -m pytest",
        step_extra="        shell: bash -n {0}\n",
    ),
    "ci-shell-version-001": workflow(
        "python -m pytest",
        step_extra="        shell: bash --version {0}\n",
    ),
    "ci-terminator-exit-001": workflow(
        "exit 0\npython -m pytest"
    ),
    "ci-wrapped-terminator-001": workflow(
        "command exit 0\npython -m pytest"
    ),
    "ci-needs-skip-001": workflow(
        "python -m pytest",
        job_extra="    needs: gate\n",
        prefix_jobs=(
            "  gate:\n"
            "    if: ${{ false }}\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - run: echo skipped\n"
        ),
    ),
    "ci-needs-cycle-001": workflow(
        "python -m pytest",
        job_extra=(
            "    needs: gate\n"
            "    if: ${{ always() }}\n"
        ),
        prefix_jobs=(
            "  gate:\n"
            "    needs: test\n"
            "    if: ${{ always() }}\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - run: echo cyclic\n"
        ),
    ),
    "ci-needs-always-pass-001": workflow(
        "python -m pytest",
        job_extra=(
            "    needs: gate\n"
            "    if: ${{ always() }}\n"
        ),
        prefix_jobs=(
            "  gate:\n"
            "    if: ${{ false }}\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - run: echo skipped\n"
        ),
    ),
    "pythia-line-subset-001": workflow(
        "mix test test/lotus_docs_contract_test.exs:12"
    ),
    "ls-node-subset-001": workflow(
        "python -m pytest "
        "tests/test_lotus_docs_contract.py::"
        "test_pr_evidence_is_bound_to_exact_head"
    ),
    "ci-workflow-default-shell-001": workflow(
        "python -m pytest",
        workflow_extra=(
            "defaults:\n"
            "  run:\n"
            "    shell: cat {0}\n"
        ),
    ),
    "ci-job-default-shell-001": workflow(
        "python -m pytest",
        job_extra=(
            "    defaults:\n"
            "      run:\n"
            "        shell: cat {0}\n"
        ),
    ),
    "ci-step-shell-override-pass-001": workflow(
        "python -m pytest",
        workflow_extra=(
            "defaults:\n"
            "  run:\n"
            "    shell: cat {0}\n"
        ),
        step_extra="        shell: bash\n",
    ),
    "ci-workflow-workdir-001": workflow(
        "python -m pytest",
        workflow_extra=(
            "defaults:\n"
            "  run:\n"
            "    working-directory: subdir\n"
        ),
    ),
    "ci-job-workdir-001": workflow(
        "python -m pytest",
        job_extra=(
            "    defaults:\n"
            "      run:\n"
            "        working-directory: subdir\n"
        ),
    ),
    "ci-step-workdir-override-pass-001": workflow(
        "python -m pytest",
        workflow_extra=(
            "defaults:\n"
            "  run:\n"
            "    working-directory: subdir\n"
        ),
        step_extra="        working-directory: .\n",
    ),
}


def valid_command(discovery: dict) -> str:
    """Return one valid command for a repository adapter."""
    if discovery["strategy"] == "pytest_default_discovery":
        return "python -m pytest"
    if discovery["strategy"] == "mix_default_discovery":
        return "mix test"
    pattern = discovery["contains_any"][0]
    if pattern.endswith(".py"):
        return f"python -m pytest {pattern}"
    if pattern.endswith(".exs"):
        return f"mix test {pattern}"
    return pattern


def materialize(
    root: Path, config: dict, text: str | None = None
) -> Path:
    """Materialize the minimum valid snapshot required by the manifest."""
    repository = root / config["snapshot_dir"]
    terms: dict[str, list[str]] = {}
    for check in config["file_checks"]:
        terms.setdefault(check["path"], []).extend(
            check["contains_all"]
        )
    for name, values in terms.items():
        path = repository / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "\n".join(dict.fromkeys(values)) + "\n",
            encoding="utf-8",
        )
    for check in config["file_checks"]:
        if "sha256" in check:
            path = repository / check["path"]
            path.write_text(
                pinned_test_source(
                    config["id"],
                    check["path"],
                    check["sha256"],
                ),
                encoding="utf-8",
            )
    discovery = config["ci_discovery"]
    path = repository / discovery["workflow_paths"][0]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        text or workflow(valid_command(discovery)),
        encoding="utf-8",
    )
    return repository


class SystemModelTest(unittest.TestCase):
    """Validate graph integrity and execute every runtime route."""

    def setUp(self) -> None:
        self.graph = load(GRAPH)
        self.route_model = load(ROUTES)
        self.routes = validate_routes(
            self.graph, self.route_model
        )
        self.manifest = load_manifest(MANIFEST)

    def test_graph_has_five_dimensions_centers_and_trajectories(
        self,
    ) -> None:
        view = validate_graph(self.graph)
        self.assertEqual(len(view["nodes"]), 49)
        self.assertEqual(len(view["edges"]), 64)
        self.assertEqual(len(self.routes), 36)
        self.assertEqual(
            set(self.graph["dimensions"]),
            {
                "causal",
                "spatial",
                "temporal",
                "hierarchy",
                "trajectory",
            },
        )

    def test_route_model_is_bound_to_exact_graph(self) -> None:
        wrong = copy.deepcopy(self.route_model)
        wrong["graph"] = "different-system-graph.json"
        with self.assertRaisesRegex(
            ValueError, "different system graph"
        ):
            validate_routes(self.graph, wrong)

    def test_runtime_pass_does_not_claim_exact_head_freshness(
        self,
    ) -> None:
        runtime_passes = [
            route
            for route in self.routes
            if route["outcome"] == PASS
            and route["trajectory"] == "audit"
        ]
        for route in runtime_passes:
            self.assertNotIn(
                "center.exact_head", route["path"], route["id"]
            )
            self.assertNotIn(
                "time.evidence_fresh", route["path"], route["id"]
            )
            self.assertIn(
                "limitation.identity_unverified",
                route["path"],
                route["id"],
            )

    def test_centrality_is_review_priority_not_authority(
        self,
    ) -> None:
        report = centrality_report(self.graph, self.routes)
        self.assertIn(
            "never ownership or authority", report["meaning"]
        )
        self.assertEqual(len(report["nodes"]), 49)

    def test_traceability_is_derived_from_routes(self) -> None:
        ledger = traceability(self.routes)
        for route in self.routes:
            self.assertIn(f"`{route['id']}`", ledger)

    def test_runtime_routes_reach_expected_outcomes(
        self,
    ) -> None:
        runtime = [
            route
            for route in self.routes
            if route["outcome"] in {PASS, DRIFT, UNKNOWN}
        ]
        for route in runtime:
            with self.subTest(route=route["id"]):
                manifest = copy.deepcopy(self.manifest)
                config = next(
                    row
                    for row in manifest["repositories"]
                    if row["id"] == route["repo"]
                )
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    if route["scenario"] != "missing_snapshot":
                        repository = materialize(
                            root,
                            config,
                            SCENARIOS.get(route["scenario"]),
                        )
                        if route["scenario"] == "missing_term":
                            check = config["file_checks"][0]
                            path = repository / check["path"]
                            path.write_text(
                                path.read_text(
                                    encoding="utf-8"
                                ).replace(
                                    check["contains_all"][0], ""
                                ),
                                encoding="utf-8",
                            )
                        elif (
                            route["scenario"]
                            == "invalid_manifest"
                        ):
                            config["file_checks"][0][
                                "contains_all"
                            ] = []

                    repository_ref = (
                        "   "
                        if route["scenario"] == "blank_ref"
                        else "refs/heads/main"
                    )
                    commit_sha = (
                        "main"
                        if route["scenario"]
                        == "invalid_commit"
                        else SHA
                    )
                    result = audit_repository(
                        manifest,
                        repository_id=route["repo"],
                        snapshot_root=root,
                        repository_ref=repository_ref,
                        commit_sha=commit_sha,
                    )
                    self.assertEqual(
                        (
                            result["outcome"],
                            result["reason_code"],
                        ),
                        (
                            route["outcome"],
                            route["reason"],
                        ),
                    )
                    for grant in AUTHORITY_GRANTS:
                        self.assertFalse(
                            result["authority"][grant],
                            f"{route['id']} granted {grant}",
                        )

    def test_merge_trajectory_never_grants_merge_authority(
        self,
    ) -> None:
        model_routes = [
            route
            for route in self.routes
            if route["outcome"] == "MODEL"
        ]
        self.assertEqual(
            {route["id"] for route in model_routes},
            {"MERGE-ELIGIBLE-001", "MERGE-STALE-001"},
        )
        eligible = next(
            route
            for route in model_routes
            if route["id"] == "MERGE-ELIGIBLE-001"
        )
        self.assertIn(
            "gate.provenance_verified", eligible["path"]
        )
        self.assertTrue(
            all(
                route["path"][-1]
                in {
                    "authority.advisory_only",
                    "state.merge_blocked",
                }
                for route in model_routes
            )
        )


if __name__ == "__main__":
    unittest.main()
