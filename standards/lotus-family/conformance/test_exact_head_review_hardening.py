"""Regression checks for the final exact-head review findings."""

from __future__ import annotations

import copy
import py_compile
import tempfile
import unittest
from pathlib import Path

from lotus_family_auditor import DRIFT, PASS, audit_repository, load_manifest
from lotus_family_schema import validate_manifest
from lotus_family_test_sources import pinned_test_source
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
        "on: push\n"
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


def _write_bytes(root: Path, relative_path: str, content: bytes) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _compile_sourceless(root: Path, relative_path: str) -> None:
    target = root / relative_path
    source = target.with_name(f"{target.stem}.source.py")
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("raise SystemExit(0)\n", encoding="utf-8")
    py_compile.compile(str(source), cfile=str(target), doraise=True)
    source.unlink()


def _materialize_python_repository(
    snapshot_root: Path,
    manifest: dict,
    repository_id: str,
) -> Path:
    config = next(
        row
        for row in manifest["repositories"]
        if row["id"] == repository_id
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
    for check in config["file_checks"]:
        if "sha256" in check:
            _write(
                repository_root,
                check["path"],
                pinned_test_source(
                    config["id"],
                    check["path"],
                    check["sha256"],
                ),
            )
    discovery = config["ci_discovery"]
    command = (
        discovery["command"]
        if discovery["strategy"] == "pytest_default_discovery"
        else f"python -m pytest {discovery['test_path']}"
    )
    _write(
        repository_root,
        discovery["workflow_paths"][0],
        _workflow().replace("python -m pytest", command),
    )
    return repository_root


def _materialize_cml(snapshot_root: Path, manifest: dict) -> Path:
    return _materialize_python_repository(
        snapshot_root,
        manifest,
        "cml",
    )


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
    for check in config["file_checks"]:
        if "sha256" in check:
            _write(
                repository_root,
                check["path"],
                pinned_test_source(
                    config["id"],
                    check["path"],
                    check["sha256"],
                ),
            )
    discovery = config["ci_discovery"]
    if discovery["strategy"] == "mix_default_discovery":
        command = discovery["command"]
    else:
        command = discovery["contains_any"][0]
    _write(
        repository_root,
        discovery["workflow_paths"][0],
        _workflow().replace("python -m pytest", command),
    )
    return repository_root


class WorkflowReviewHardeningTest(unittest.TestCase):
    """Protect workflow failure propagation and gating semantics."""

    def test_manual_only_workflow_is_not_ci_evidence(self) -> None:
        manual_only = _workflow().replace(
            "on: push\n", "on: workflow_dispatch\n", 1
        )
        self.assertEqual(ci_discovery(DISCOVERY, manual_only), (False, []))

    def test_job_container_is_not_ci_evidence(self) -> None:
        containerized = _workflow().replace(
            "    runs-on: ubuntu-latest\n",
            "    runs-on: ubuntu-latest\n"
            "    container: attacker.example/fake-python:latest\n",
            1,
        )
        self.assertEqual(ci_discovery(DISCOVERY, containerized), (False, []))

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

    def test_configured_pythia_workflow_remains_discoverable(self) -> None:
        manifest = load_manifest(MANIFEST_PATH)
        config = next(
            row
            for row in manifest["repositories"]
            if row["id"] == "pythia"
        )
        workflow_path = ROOT.parents[1] / config["ci_discovery"][
            "workflow_paths"
        ][0]

        self.assertEqual(
            ci_discovery(
                config["ci_discovery"],
                workflow_path.read_text(encoding="utf-8"),
            ),
            (
                True,
                [
                    (
                        "elixir -e 'ExUnit.start()' "
                        "test/lotus_docs_contract_test.exs --"
                    )
                ],
            ),
        )

    def test_direct_elixir_vm_flag_environment_is_rejected(self) -> None:
        manifest = load_manifest(MANIFEST_PATH)
        config = next(
            row
            for row in manifest["repositories"]
            if row["id"] == "pythia"
        )
        workflow = (
            "name: CI\n"
            "on: push\n"
            "env:\n"
            "  ERL_AFLAGS: -eval halt().\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - run: elixir -e 'ExUnit.start()' "
            "test/lotus_docs_contract_test.exs --\n"
        )

        self.assertEqual(
            ci_discovery(config["ci_discovery"], workflow),
            (False, []),
        )


class ManifestSourceBindingReviewHardeningTest(unittest.TestCase):
    """Bind explicit CI discovery to one immutable checked test source."""

    def setUp(self) -> None:
        self.manifest = copy.deepcopy(load_manifest(MANIFEST_PATH))
        self.config = next(
            row
            for row in self.manifest["repositories"]
            if row["id"] == "pythia"
        )

    def test_contains_any_command_cannot_target_an_unchecked_test(self) -> None:
        self.config["ci_discovery"]["contains_any"] = [
            "elixir -e 'ExUnit.start()' test/unrelated_test.exs --"
        ]

        with self.assertRaisesRegex(
            ValueError,
            "must target only ci_discovery.test_path",
        ):
            validate_manifest(self.manifest)

    def test_direct_elixir_test_source_requires_a_pinned_digest(self) -> None:
        for mutation in ("missing", "null"):
            with self.subTest(mutation=mutation):
                manifest = copy.deepcopy(self.manifest)
                config = next(
                    row
                    for row in manifest["repositories"]
                    if row["id"] == "pythia"
                )
                test_check = next(
                    check
                    for check in config["file_checks"]
                    if check["path"]
                    == "test/lotus_docs_contract_test.exs"
                )
                if mutation == "missing":
                    del test_check["sha256"]
                    error = "must pin sha256 for executed test source"
                else:
                    test_check["sha256"] = None
                    error = "sha256 must be a lowercase SHA-256"

                with self.assertRaisesRegex(ValueError, error):
                    validate_manifest(manifest)

    def test_pytest_test_sources_require_pinned_digests(self) -> None:
        for repository_id in ("cml", "ls"):
            with self.subTest(repository_id=repository_id):
                manifest = copy.deepcopy(self.manifest)
                config = next(
                    row
                    for row in manifest["repositories"]
                    if row["id"] == repository_id
                )
                test_check = next(
                    check
                    for check in config["file_checks"]
                    if check["path"] == config["ci_discovery"]["test_path"]
                )
                del test_check["sha256"]

                with self.assertRaisesRegex(
                    ValueError,
                    "must pin sha256 for executed test source",
                ):
                    validate_manifest(manifest)

    def test_phrase_preserving_pytest_source_replacement_is_drift(self) -> None:
        for repository_id in ("cml", "ls"):
            with self.subTest(repository_id=repository_id):
                manifest = copy.deepcopy(self.manifest)
                with tempfile.TemporaryDirectory() as directory:
                    snapshot_root = Path(directory)
                    repository_root = _materialize_python_repository(
                        snapshot_root,
                        manifest,
                        repository_id,
                    )
                    config = next(
                        row
                        for row in manifest["repositories"]
                        if row["id"] == repository_id
                    )
                    test_check = next(
                        check
                        for check in config["file_checks"]
                        if check["path"]
                        == config["ci_discovery"]["test_path"]
                    )
                    _write(
                        repository_root,
                        test_check["path"],
                        "\n".join(
                            f"# {term}"
                            for term in test_check["contains_all"]
                        )
                        + "\n\ndef test_trivial_pass() -> None:\n    pass\n",
                    )
                    result = audit_repository(
                        manifest,
                        repository_id=repository_id,
                        snapshot_root=snapshot_root,
                        repository_ref="refs/heads/main",
                        commit_sha=SHA,
                    )

                self.assertEqual(result["outcome"], DRIFT)
                check = next(
                    row
                    for row in result["checks"]
                    if row["check_id"] == "regression_protection"
                )
                self.assertEqual(check["missing_terms"], [])
                self.assertIn("pinned source", check["detail"])

    def test_self_disabling_direct_elixir_source_is_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_pythia(
                snapshot_root,
                self.manifest,
            )
            _write(
                repository_root,
                "test/lotus_docs_contract_test.exs",
                (
                    "# PR evidence is bound to exact head and changed context\n"
                    "# English and Russian contracts preserve the "
                    "no-authority boundary\n"
                    "# Lotus remains a limitation contract rather than a "
                    "safety overclaim\n"
                    "System.halt(0)\n"
                ),
            )
            result = audit_repository(
                self.manifest,
                repository_id="pythia",
                snapshot_root=snapshot_root,
                repository_ref="refs/heads/main",
                commit_sha=SHA,
            )

        self.assertEqual(result["outcome"], DRIFT)
        check = next(
            row
            for row in result["checks"]
            if row["check_id"] == "regression_protection"
        )
        self.assertEqual(check["outcome"], DRIFT)
        self.assertEqual(check["missing_terms"], [])
        self.assertIn("pinned source", check["detail"])


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

    def test_repository_pytest_shadows_block_default_discovery(self) -> None:
        cases = (
            "pytest.py",
            "pytest/__init__.py",
            "pytest/__main__.py",
            "pluggy.py",
            "iniconfig.py",
            "_pytest/__init__.py",
            "packaging.py",
            "pygments.py",
            "colorama.py",
            "tomli.py",
            "exceptiongroup.py",
            "py.py",
            "py/__init__.py",
        )
        for relative_path in cases:
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as directory:
                    snapshot_root = Path(directory)
                    repository_root = _materialize_cml(
                        snapshot_root,
                        self.manifest,
                    )
                    _write(repository_root, relative_path, "raise SystemExit(0)\n")
                    result = self._audit(snapshot_root)

                self._assert_blocked_config(result, relative_path)

    def test_sourceless_pytest_bytecode_shadows_block_discovery(self) -> None:
        cases = (
            "pytest.pyc",
            "pytest/__init__.pyc",
            "pytest/__main__.pyc",
            "pluggy.pyc",
            "iniconfig/__init__.pyc",
            "py.pyc",
            "py/__init__.pyc",
            "_pytest/__init__.pyc",
        )
        for relative_path in cases:
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as directory:
                    snapshot_root = Path(directory)
                    repository_root = _materialize_cml(
                        snapshot_root,
                        self.manifest,
                    )
                    _compile_sourceless(repository_root, relative_path)
                    result = self._audit(snapshot_root)

                self._assert_blocked_config(result, relative_path)

    def test_native_pytest_extension_shadows_block_discovery(self) -> None:
        cases = (
            "pytest.cpython-312-x86_64-linux-gnu.so",
            "pytest/__main__.pyd",
            "pluggy.cpython-312-x86_64-linux-gnu.so",
            "py.cpython-312-x86_64-linux-gnu.so",
            "py/__init__.pyd",
            "_pytest/__init__.pyd",
        )
        for relative_path in cases:
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as directory:
                    snapshot_root = Path(directory)
                    repository_root = _materialize_cml(
                        snapshot_root,
                        self.manifest,
                    )
                    _write_bytes(repository_root, relative_path, b"\xffshadow")
                    result = self._audit(snapshot_root)

                self._assert_blocked_config(result, relative_path)

    def test_python_startup_shadows_block_pytest_discovery(self) -> None:
        cases = (
            "sitecustomize.pyc",
            "usercustomize.cpython-312-x86_64-linux-gnu.so",
        )
        for relative_path in cases:
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as directory:
                    snapshot_root = Path(directory)
                    repository_root = _materialize_cml(
                        snapshot_root,
                        self.manifest,
                    )
                    if relative_path.endswith(".pyc"):
                        _compile_sourceless(repository_root, relative_path)
                    else:
                        _write_bytes(
                            repository_root,
                            relative_path,
                            b"\xffshadow",
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
        self.manifest = copy.deepcopy(load_manifest(MANIFEST_PATH))
        config = next(
            row
            for row in self.manifest["repositories"]
            if row["id"] == "pythia"
        )
        config["ci_discovery"] = {
            "workflow_paths": [".github/workflows/ci.yml"],
            "strategy": "mix_default_discovery",
            "command": "mix test",
            "test_path": "test/lotus_docs_contract_test.exs",
        }

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

    def test_mix_keyword_pipeline_override_blocks_default_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_pythia(
                snapshot_root, self.manifest
            )
            _write(
                repository_root,
                "mix.exs",
                (
                    "def project do\n"
                    "  [app: :lotus_fixture, version: \"0.1.0\"]\n"
                    "  |> Keyword.put(:test_paths, [\"ignored\"])\n"
                    "end\n"
                ),
            )
            result = self._audit(snapshot_root)

        self._assert_blocked_config(result, "mix.exs")

    def test_unproven_mix_project_construction_blocks_default_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_pythia(
                snapshot_root, self.manifest
            )
            _write(
                repository_root,
                "mix.exs",
                "def project, do: project_options()\n",
            )
            result = self._audit(snapshot_root)

        self._assert_blocked_config(result, "mix.exs")

    def test_executable_code_outside_mix_project_blocks_default_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_pythia(
                snapshot_root, self.manifest
            )
            _write(
                repository_root,
                "mix.exs",
                (
                    "System.halt(0)\n"
                    "def project, do: [app: :lotus_fixture]\n"
                ),
            )
            result = self._audit(snapshot_root)

        self._assert_blocked_config(result, "mix.exs")

    def test_executable_mix_project_value_blocks_default_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_pythia(
                snapshot_root, self.manifest
            )
            _write(
                repository_root,
                "mix.exs",
                "def project, do: [app: :lotus_fixture, version: System.halt(0)]\n",
            )
            result = self._audit(snapshot_root)

        self._assert_blocked_config(result, "mix.exs")

    def test_executable_test_helper_blocks_default_discovery(self) -> None:
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
                "ExUnit.start()\nSystem.halt(0)\n",
            )
            result = self._audit(snapshot_root)

        self._assert_blocked_config(result, "test/test_helper.exs")

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

    def test_required_mix_file_is_hashed_and_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_pythia(
                snapshot_root, self.manifest
            )
            _write(
                repository_root,
                "mix.exs",
                (
                    'Code.require_file("support.exs", __DIR__)\n'
                    "defmodule Fixture.MixProject do\n"
                    "  use Mix.Project\n"
                    "  def project, do: [app: :lotus_fixture]\n"
                    "end\n"
                ),
            )
            _write(repository_root, "support.exs", "System.halt(0)\n")
            result = self._audit(snapshot_root)

        self.assertEqual(result["outcome"], DRIFT)
        check = next(
            row
            for row in result["checks"]
            if row["check_id"] == "mix_configuration"
        )
        self.assertEqual(check["outcome"], DRIFT)
        self.assertIn("support.exs", set(check["paths"]))
        self.assertIn("support.exs", set(check["blocked_paths"]))
        self.assertIn("support.exs", {row["path"] for row in result["files"]})


if __name__ == "__main__":
    unittest.main()
