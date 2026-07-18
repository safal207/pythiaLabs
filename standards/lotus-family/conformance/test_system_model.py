from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from lotus_family_auditor import DRIFT, PASS, UNKNOWN, audit_repository, load_manifest
from lotus_family_system_model import centrality_report, load, traceability, validate_graph, validate_routes

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
GRAPH = ROOT / "causality" / "lotus-family-system-v0.1.json"
ROUTES = ROOT / "causality" / "system-routes-v0.1.json"
MANIFEST = ROOT / "manifest" / "lotus-family-v0.1.json"
SHA = "a" * 40


def workflow(command: str, *, job_extra: str = "", step_extra: str = "", prefix_jobs: str = "") -> str:
    body = "\n".join(f"          {line}" if line else "" for line in command.splitlines())
    return f"name: CI\njobs:\n{prefix_jobs}  test:\n    runs-on: ubuntu-latest\n{job_extra}    steps:\n      - name: Run tests\n{step_extra}        run: |\n{body}\n"


SCENARIOS = {
    "ci-nonrun-001": "name: CI\nenv:\n  NOTE: python -m pytest\njobs: {}\n",
    "ci-step-skip-001": workflow("python -m pytest", step_extra="        if: ${{ false }}\n"),
    "ci-job-skip-001": workflow("python -m pytest", job_extra="    if: ${{ false }}\n"),
    "ci-no-runner-001": "name: CI\njobs:\n  test:\n    steps:\n      - run: python -m pytest\n",
    "ci-quoted-env-001": 'name: CI\nenv:\n  "PYTEST_ADDOPTS": "--ignore=tests/test_lotus_docs_contract.py"\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: python -m pytest\n',
    "ci-shell-control-001": workflow("if false; then\n  python -m pytest\nfi"),
    "cml-subset-001": workflow("python -m pytest tests/test_other.py"),
    "pythia-subset-001": workflow("mix test test/unrelated_test.exs"),
    "ci-fake-steps-001": "name: CI\nmetadata:\n  fake:\n    steps:\n      - run: python -m pytest\njobs: {}\n",
    "ci-custom-shell-001": workflow("python -m pytest", step_extra="        shell: cat {0}\n"),
    "ci-terminator-exit-001": workflow("exit 0\npython -m pytest"),
    "ci-needs-skip-001": workflow("python -m pytest", job_extra="    needs: gate\n", prefix_jobs="  gate:\n    if: ${{ false }}\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo skipped\n"),
    "ci-needs-always-pass-001": workflow("python -m pytest", job_extra="    needs: gate\n    if: ${{ always() }}\n", prefix_jobs="  gate:\n    if: ${{ false }}\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo skipped\n"),
    "pythia-line-subset-001": workflow("mix test test/lotus_docs_contract_test.exs:12"),
    "ls-node-subset-001": workflow("python -m pytest tests/test_lotus_docs_contract.py::test_pr_evidence_is_bound_to_exact_head"),
}


def valid_command(discovery: dict) -> str:
    if discovery["strategy"] == "pytest_default_discovery":
        return "python -m pytest"
    if discovery["strategy"] == "mix_default_discovery":
        return "mix test"
    pattern = discovery["contains_any"][0]
    return f"python -m pytest {pattern}" if pattern.endswith(".py") else f"mix test {pattern}"


def materialize(root: Path, config: dict, text: str | None = None) -> Path:
    repo = root / config["snapshot_dir"]
    terms: dict[str, list[str]] = {}
    for check in config["file_checks"]:
        terms.setdefault(check["path"], []).extend(check["contains_all"])
    for name, values in terms.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(dict.fromkeys(values)) + "\n", encoding="utf-8")
    discovery = config["ci_discovery"]
    path = repo / discovery["workflow_paths"][0]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text or workflow(valid_command(discovery)), encoding="utf-8")
    return repo


class SystemModelTest(unittest.TestCase):
    def setUp(self):
        self.graph = load(GRAPH)
        self.route_model = load(ROUTES)
        self.routes = validate_routes(self.graph, self.route_model)
        self.manifest = load_manifest(MANIFEST)

    def test_graph_has_five_dimensions_centers_and_trajectories(self):
        view = validate_graph(self.graph)
        self.assertEqual(len(view["nodes"]), 46)
        self.assertEqual(len(view["edges"]), 62)
        self.assertEqual(len(self.routes), 25)
        self.assertEqual(set(self.graph["dimensions"]), {"causal", "spatial", "temporal", "hierarchy", "trajectory"})

    def test_centrality_is_review_priority_not_authority(self):
        report = centrality_report(self.graph, self.routes)
        self.assertIn("never ownership or authority", report["meaning"])
        self.assertEqual(len(report["nodes"]), 46)

    def test_traceability_is_derived_from_routes(self):
        ledger = traceability(self.routes)
        for route in self.routes:
            self.assertIn(f"`{route['id']}`", ledger)

    def test_runtime_routes_reach_expected_outcomes(self):
        runtime = [route for route in self.routes if route["outcome"] in {PASS, DRIFT, UNKNOWN}]
        for route in runtime:
            with self.subTest(route=route["id"]):
                manifest = copy.deepcopy(self.manifest)
                config = next(row for row in manifest["repositories"] if row["id"] == route["repo"])
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    if route["scenario"] != "missing_snapshot":
                        repo = materialize(root, config, SCENARIOS.get(route["scenario"]))
                        if route["scenario"] == "missing_term":
                            check = config["file_checks"][0]
                            path = repo / check["path"]
                            path.write_text(path.read_text(encoding="utf-8").replace(check["contains_all"][0], ""), encoding="utf-8")
                        elif route["scenario"] == "invalid_manifest":
                            config["file_checks"][0]["contains_all"] = []
                    result = audit_repository(
                        manifest,
                        repository_id=route["repo"],
                        snapshot_root=root,
                        repository_ref="refs/heads/main",
                        commit_sha="main" if route["scenario"] == "invalid_commit" else SHA,
                    )
                    self.assertEqual((result["outcome"], result["reason_code"]), (route["outcome"], route["reason"]))
                    self.assertFalse(result["authority"]["grants_merge"])

    def test_merge_trajectory_never_grants_merge_authority(self):
        model_routes = [route for route in self.routes if route["outcome"] == "MODEL"]
        self.assertEqual({route["id"] for route in model_routes}, {"MERGE-ELIGIBLE-001", "MERGE-STALE-001"})
        self.assertTrue(all(route["path"][-1] in {"authority.advisory_only", "state.merge_blocked"} for route in model_routes))


if __name__ == "__main__":
    unittest.main()
