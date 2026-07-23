"""Regression coverage for pytest config affecting explicit test targets."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from lotus_family_auditor import DRIFT, audit_repository, load_manifest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MANIFEST_PATH = ROOT / "manifest" / "lotus-family-v0.1.json"
SHA = "a" * 40


def _write(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _materialize_ls(snapshot_root: Path, manifest: dict) -> Path:
    config = next(
        row for row in manifest["repositories"] if row["id"] == "ls"
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
        (
            "name: CI\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - name: Lotus contract\n"
            "        run: python -m pytest tests/test_lotus_docs_contract.py\n"
        ),
    )
    return repository_root


def _audit_ls(snapshot_root: Path, manifest: dict) -> dict:
    return audit_repository(
        manifest,
        repository_id="ls",
        snapshot_root=snapshot_root,
        repository_ref="refs/heads/main",
        commit_sha=SHA,
    )


def _configuration_check(result: dict) -> dict:
    return next(
        row
        for row in result["checks"]
        if row["check_id"] == "pytest_configuration"
    )


class ExplicitPytestConfigurationTest(unittest.TestCase):
    """Fail closed when pytest config narrows an explicit Python test run."""

    def test_pytest_ini_deselect_blocks_explicit_contract_test(self) -> None:
        manifest = load_manifest(MANIFEST_PATH)
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_ls(snapshot_root, manifest)
            _write(
                repository_root,
                "pytest.ini",
                (
                    "[pytest]\n"
                    "addopts = --deselect "
                    "tests/test_lotus_docs_contract.py\n"
                ),
            )
            result = _audit_ls(snapshot_root, manifest)

        self.assertEqual(result["outcome"], DRIFT)
        self.assertEqual(result["reason_code"], "LOTUS_CONTRACT_DRIFT")
        config_check = _configuration_check(result)
        self.assertEqual(config_check["outcome"], DRIFT)
        self.assertIn("pytest.ini", config_check["blocked_paths"])
        self.assertIn(
            "pytest.ini",
            {row["path"] for row in result["files"]},
        )

    def test_target_parent_pytest_ini_blocks_explicit_contract_test(self) -> None:
        manifest = load_manifest(MANIFEST_PATH)
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_ls(snapshot_root, manifest)
            _write(
                repository_root,
                "tests/pytest.ini",
                (
                    "[pytest]\n"
                    "addopts = --deselect "
                    "tests/test_lotus_docs_contract.py\n"
                ),
            )
            result = _audit_ls(snapshot_root, manifest)

        self.assertEqual(result["outcome"], DRIFT)
        self.assertEqual(result["reason_code"], "LOTUS_CONTRACT_DRIFT")
        config_check = _configuration_check(result)
        self.assertEqual(config_check["outcome"], DRIFT)
        self.assertIn("tests/pytest.ini", config_check["paths"])
        self.assertIn("tests/pytest.ini", config_check["blocked_paths"])
        self.assertIn(
            "tests/pytest.ini",
            {row["path"] for row in result["files"]},
        )


if __name__ == "__main__":
    unittest.main()
