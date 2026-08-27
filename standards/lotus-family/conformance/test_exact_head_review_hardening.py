"""Regression checks for the final exact-head review findings."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from lotus_family_auditor import DRIFT, PASS, audit_repository, load_manifest
from lotus_family_workflow import ci_discovery


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MANIFEST_PATH = ROOT / "manifest" / "lotus-family-v0.1.json"
SHA = "a" * 40
DISCOVERY = {
    "strategy": "pytest_default_discovery",
    "test_path": "tests/test_lotus_docs_contract.py",
    "command": "python -m pytest",
}


def _workflow(*, shell: str | None = None, job_continue: str | None = None) -> str:
    shell_line = f"        shell: {shell}\n" if shell is not None else ""
    continue_line = (
        f"    continue-on-error: {job_continue}\n"
        if job_continue is not None
        else ""
    )
    return (
        "name: CI\n"
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-latest\n"
        f"{continue_line}"
        "    steps:\n"
        "      - name: Contract test\n"
        f"{shell_line}"
        "        run: python -m pytest\n"
    )


def _write(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _materialize_cml(snapshot_root: Path, manifest: dict) -> Path:
    config = next(
        row for row in manifest["repositories"] if row["id"] == "cml"
    )
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
    _write(
        repository_root,
        config["ci_discovery"]["workflow_paths"][0],
        _workflow(),
    )
    return repository_root


def _materialize_pythia(snapshot_root: Path, manifest: dict) -> Path:
    config = next(
        row for row in manifest["repositories"] if row["id"] == "pythia"
    )
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
    _write(
        repository_root,
        config["ci_discovery"]["workflow_paths"][0],
        _workflow().replace("python -m pytest", "mix test"),
    )
    return repository_root


class WorkflowReviewHardeningTest(unittest.TestCase):
    """Protect workflow failure propagation and gating semantics."""

    def test_custom_shell_without_fail_fast_is_rejected(self) -> None:
        self.assertEqual(
            ci_discovery(DISCOVERY, _workflow(shell="bash {0}")),
            (False, []),
        )

    def test_custom_shell_with_explicit_fail_fast_is_accepted(self) -> None:
        self.assertEqual(
            ci_discovery(DISCOVERY, _workflow(shell="bash -e {0}")),
            (True, ["python -m pytest"]),
        )

    def test_job_level_continue_on_error_is_rejected(self) -> None:
        self.assertEqual(
            ci_discovery(DISCOVERY, _workflow(job_continue="true")),
            (False, []),
        )

    def test_expression_driven_job_failure_policy_is_rejected(self) -> None:
        self.assertEqual(
            ci_discovery(
                DISCOVERY,
                _workflow(job_continue="${{ matrix.experimental }}"),
            ),
            (False, []),
        )


class PytestConfigurationReviewHardeningTest(unittest.TestCase):
    """Bind default pytest discovery to hashed repository configuration."""

    def setUp(self) -> None:
        self.manifest = load_manifest(MANIFEST_PATH)

    def _audit(self, snapshot_root: Path) -> dict:
        return audit_repository(
            self.manifest,
            repository_id="cml",
            snapshot_root=snapshot_root,
            repository_ref="refs/heads/main",
            commit_sha=SHA,
        )

    def _assert_blocked_config(self, result: dict, path: str) -> None:
        self.assertEqual(result["outcome"], DRIFT)
        self.assertEqual(result["reason_code"], "LOTUS_CONTRACT_DRIFT")
        config_check = next(
            row
            for row in result["checks"]
            if row["check_id"] == "pytest_configuration"
        )
        self.assertEqual(config_check["outcome"], DRIFT)
        self.assertIn(path, config_check["blocked_paths"])
        self.assertIn(path, {row["path"] for row in result["files"]})

    def test_active_pyproject_pytest_scope_blocks_default_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_cml(snapshot_root, self.manifest)
            _write(
                repository_root,
                "pyproject.toml",
                "[tool.pytest.ini_options]\naddopts = '-k not lotus'\n",
            )
            result = self._audit(snapshot_root)

        self._assert_blocked_config(result, "pyproject.toml")

    def test_native_pyproject_pytest_scope_blocks_default_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_cml(snapshot_root, self.manifest)
            _write(
                repository_root,
                "pyproject.toml",
                "[tool.pytest]\npython_files = ['not_contract.py']\n",
            )
            result = self._audit(snapshot_root)

        self._assert_blocked_config(result, "pyproject.toml")

    def test_toml_semantic_pytest_headers_block_default_discovery(self) -> None:
        cases = {
            "commented header": (
                "[tool.pytest.ini_options] # valid TOML comment\n"
                "addopts = '-k not lotus'\n"
            ),
            "spaced dotted keys": (
                "[tool . pytest]\n"
                "python_files = ['not_contract.py']\n"
            ),
            "quoted key": (
                "[tool.\"pytest\"]\n"
                "python_files = ['not_contract.py']\n"
            ),
        }
        for name, content in cases.items():
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as directory:
                    snapshot_root = Path(directory)
                    repository_root = _materialize_cml(
                        snapshot_root,
                        self.manifest,
                    )
                    _write(repository_root, "pyproject.toml", content)
                    result = self._audit(snapshot_root)

                self._assert_blocked_config(result, "pyproject.toml")

    def test_invalid_pyproject_blocks_default_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_cml(snapshot_root, self.manifest)
            _write(
                repository_root,
                "pyproject.toml",
                "[tool.pytest\npython_files = ['not_contract.py']\n",
            )
            result = self._audit(snapshot_root)

        self._assert_blocked_config(result, "pyproject.toml")

    def test_hidden_pytest_ini_blocks_default_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_cml(snapshot_root, self.manifest)
            _write(
                repository_root,
                ".pytest.ini",
                "[pytest]\naddopts = --ignore=tests/test_lotus_docs_contract.py\n",
            )
            result = self._audit(snapshot_root)

        self._assert_blocked_config(result, ".pytest.ini")

    def test_conftest_hooks_block_default_discovery(self) -> None:
        for relative_path in ("conftest.py", "support/conftest.py"):
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as directory:
                    snapshot_root = Path(directory)
                    repository_root = _materialize_cml(
                        snapshot_root,
                        self.manifest,
                    )
                    _write(
                        repository_root,
                        relative_path,
                        (
                            "def pytest_ignore_collect(collection_path, config):\n"
                            "    return True\n"
                        ),
                    )
                    result = self._audit(snapshot_root)

                self._assert_blocked_config(result, relative_path)

    def test_non_pytest_pyproject_scope_is_hashed_and_keeps_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_cml(snapshot_root, self.manifest)
            _write(
                repository_root,
                "pyproject.toml",
                "[project]\nname = 'cml-fixture'\n",
            )
            result = self._audit(snapshot_root)

        self.assertEqual(result["outcome"], PASS)
        config_check = next(
            row
            for row in result["checks"]
            if row["check_id"] == "pytest_configuration"
        )
        self.assertEqual(config_check["outcome"], PASS)
        self.assertIn(
            "pyproject.toml",
            {row["path"] for row in result["files"]},
        )


class MixConfigurationReviewHardeningTest(unittest.TestCase):
    """Bind Mix default discovery to hashed collection configuration."""

    def setUp(self) -> None:
        self.manifest = load_manifest(MANIFEST_PATH)

    def _audit(self, snapshot_root: Path) -> dict:
        return audit_repository(
            self.manifest,
            repository_id="pythia",
            snapshot_root=snapshot_root,
            repository_ref="refs/heads/main",
            commit_sha=SHA,
        )

    def _assert_blocked_config(self, result: dict, path: str) -> None:
        self.assertEqual(result["outcome"], DRIFT)
        check = next(
            row
            for row in result["checks"]
            if row["check_id"] == "mix_configuration"
        )
        self.assertEqual(check["outcome"], DRIFT)
        self.assertIn(path, check["blocked_paths"])
        self.assertIn(path, {row["path"] for row in result["files"]})

    def test_mix_test_paths_override_blocks_default_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_pythia(
                snapshot_root, self.manifest
            )
            _write(
                repository_root,
                "mix.exs",
                "def project, do: [test_paths: [\"ignored\"]]\n",
            )
            result = self._audit(snapshot_root)

        self._assert_blocked_config(result, "mix.exs")

    def test_mix_test_pattern_override_blocks_default_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_pythia(
                snapshot_root, self.manifest
            )
            _write(
                repository_root,
                "mix.exs",
                "def project, do: [test_pattern: \"*_other.exs\"]\n",
            )
            result = self._audit(snapshot_root)

        self._assert_blocked_config(result, "mix.exs")

    def test_exunit_selection_override_blocks_default_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_pythia(
                snapshot_root, self.manifest
            )
            _write(
                repository_root,
                "test/test_helper.exs",
                "ExUnit.start(exclude: [:lotus_contract])\n",
            )
            result = self._audit(snapshot_root)

        self._assert_blocked_config(result, "test/test_helper.exs")

    def test_plain_mix_configuration_is_hashed_and_keeps_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_pythia(
                snapshot_root, self.manifest
            )
            _write(
                repository_root,
                "mix.exs",
                "def project, do: [app: :lotus_fixture]\n",
            )
            _write(
                repository_root,
                "test/test_helper.exs",
                "ExUnit.start()\n",
            )
            result = self._audit(snapshot_root)

        self.assertEqual(result["outcome"], PASS)
        check = next(
            row
            for row in result["checks"]
            if row["check_id"] == "mix_configuration"
        )
        self.assertEqual(check["outcome"], PASS)
        self.assertEqual(
            set(check["paths"]), {"mix.exs", "test/test_helper.exs"}
        )


if __name__ == "__main__":
    unittest.main()
