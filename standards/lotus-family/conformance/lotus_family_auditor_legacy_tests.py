from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from lotus_family_auditor import DRIFT, PASS, UNKNOWN, audit_repository, load_manifest
from lotus_family_test_sources import pinned_test_source

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MANIFEST_PATH = ROOT / "manifest" / "lotus-family-v0.1.json"
SHA = "a" * 40


def _write(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _discovery_fixture(discovery: dict) -> str:
    if discovery.get("strategy") == "pytest_default_discovery":
        return (
            "python -m pytest \\\n"
            "  --junitxml=artifacts/junit.xml \\\n"
            "  --cov=cml\n"
        )
    pattern = discovery["contains_any"][0]
    if pattern.endswith(".py"):
        return f"python -m pytest {pattern}\n"
    return pattern + "\n"


def _materialize_repository(snapshot_root: Path, config: dict) -> Path:
    repository_root = snapshot_root / config["snapshot_dir"]
    terms_by_path: dict[str, list[str]] = {}
    for check in config["file_checks"]:
        terms_by_path.setdefault(check["path"], []).extend(check["contains_all"])
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
    _write(
        repository_root,
        discovery["workflow_paths"][0],
        _discovery_fixture(discovery),
    )
    return repository_root


class LotusFamilyAuditorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = load_manifest(MANIFEST_PATH)

    def config(self, repository_id: str) -> dict:
        return next(
            row
            for row in self.manifest["repositories"]
            if row["id"] == repository_id
        )

    def audit(self, repository_id: str, snapshot_root: Path):
        return audit_repository(
            self.manifest,
            repository_id=repository_id,
            snapshot_root=snapshot_root,
            repository_ref="refs/heads/main",
            commit_sha=SHA,
        )

    def workflow(self, repository_root: Path) -> Path:
        return repository_root / ".github/workflows/ci.yml"

    def discovery(self, result: dict) -> dict:
        return next(
            row for row in result["checks"] if row["check_id"] == "ci_discovery"
        )

    def assert_ci_drift(self, repository_id: str, command: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_repository(
                snapshot_root, self.config(repository_id)
            )
            self.workflow(repository_root).write_text(command, encoding="utf-8")
            result = self.audit(repository_id, snapshot_root)
            self.assertEqual(result["outcome"], DRIFT)
            self.assertEqual(self.discovery(result)["outcome"], DRIFT)
            self.assertEqual(self.discovery(result)["matched_patterns"], [])

    def test_manifest_has_three_repository_adapters_and_audit_only_authority(self):
        self.assertEqual(self.manifest["authority"], "audit_only")
        self.assertEqual(
            {row["id"] for row in self.manifest["repositories"]},
            {"pythia", "cml", "ls"},
        )

    def test_valid_pythia_snapshot_passes_with_exact_identity_and_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            _materialize_repository(snapshot_root, self.config("pythia"))
            result = self.audit("pythia", snapshot_root)
            self.assertEqual(
                (result["outcome"], result["reason_code"]),
                (PASS, "LOTUS_CONTRACT_CONFORMANT"),
            )
            self.assertEqual(result["repository"], "safal207/pythiaLabs")
            self.assertEqual(result["repository_ref"], "refs/heads/main")
            self.assertEqual(result["commit_sha"], SHA)
            self.assertTrue(result["files"])
            for row in result["files"]:
                self.assertRegex(row["sha256"], r"^[0-9a-f]{64}$")
            self.assertFalse(result["authority"]["grants_merge"])

    def test_valid_cml_default_pytest_discovery_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            _materialize_repository(snapshot_root, self.config("cml"))
            result = self.audit("cml", snapshot_root)
            self.assertEqual(result["outcome"], PASS)
            self.assertEqual(
                self.discovery(result)["matched_patterns"],
                ["python -m pytest"],
            )

    def test_valid_ls_explicit_contract_test_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            _materialize_repository(snapshot_root, self.config("ls"))
            result = self.audit("ls", snapshot_root)
            self.assertEqual(result["outcome"], PASS)
            self.assertEqual(
                self.discovery(result)["matched_patterns"],
                ["tests/test_lotus_docs_contract.py"],
            )

    def test_bilingual_authority_deletion_is_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_repository(
                snapshot_root, copy.deepcopy(self.config("cml"))
            )
            contract = repository_root / "docs/LOTUS.md"
            contract.write_text(
                contract.read_text(encoding="utf-8").replace(
                    "не имеет права собственности", ""
                ),
                encoding="utf-8",
            )
            result = self.audit("cml", snapshot_root)
            self.assertEqual(result["outcome"], DRIFT)
            check = next(
                row
                for row in result["checks"]
                if row["check_id"] == "bilingual_contract"
            )
            self.assertIn("не имеет права собственности", check["missing_terms"])

    def test_contract_test_not_discovered_by_ci_is_drift(self):
        self.assert_ci_drift("ls", "python -m pytest tests/test_other.py\n")

    def test_cml_unrelated_pytest_subset_is_not_full_discovery(self):
        self.assert_ci_drift("cml", "python -m pytest tests/test_other.py\n")

    def test_cml_pytest_ignore_of_contract_test_is_drift(self):
        self.assert_ci_drift(
            "cml",
            "python -m pytest --ignore=tests/test_lotus_docs_contract.py\n",
        )

    def test_cml_commented_pytest_command_is_drift(self):
        self.assert_ci_drift("cml", "# python -m pytest\n")

    def test_cml_pytest_ignore_directory_covering_contract_test_is_drift(self):
        self.assert_ci_drift("cml", "python -m pytest --ignore=tests\n")

    def test_cml_pytest_ignore_glob_covering_contract_test_is_drift(self):
        self.assert_ci_drift(
            "cml", "python -m pytest --ignore-glob='tests/*'\n"
        )

    def test_cml_pytest_ignore_glob_with_dot_prefix_is_drift(self):
        self.assert_ci_drift(
            "cml", "python -m pytest --ignore-glob='./tests/*'\n"
        )

    def test_cml_echo_pytest_is_not_executed(self):
        self.assert_ci_drift("cml", "echo python -m pytest\n")

    def test_cml_false_and_pytest_is_not_executed(self):
        self.assert_ci_drift("cml", "false && python -m pytest\n")

    def test_cml_pytest_k_filter_is_drift(self):
        self.assert_ci_drift(
            "cml", "python -m pytest -k='not lotus_docs_contract'\n"
        )

    def test_ls_commented_contract_test_is_drift(self):
        self.assert_ci_drift(
            "ls", "# python -m pytest tests/test_lotus_docs_contract.py\n"
        )

    def test_ls_ignored_contract_test_is_drift(self):
        self.assert_ci_drift(
            "ls",
            "python -m pytest --ignore=tests/test_lotus_docs_contract.py "
            "tests/test_lotus_docs_contract.py\n",
        )

    def test_ls_echo_contract_test_is_drift(self):
        self.assert_ci_drift(
            "ls", "echo python -m pytest tests/test_lotus_docs_contract.py\n"
        )

    def test_pythia_commented_mix_test_is_drift(self):
        self.assert_ci_drift("pythia", "# mix test\n")

    def test_pythia_echo_mix_test_is_drift(self):
        self.assert_ci_drift("pythia", "echo mix test\n")

    def test_empty_manifest_term_list_is_unknown_not_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            _materialize_repository(snapshot_root, self.config("pythia"))
            manifest = copy.deepcopy(self.manifest)
            manifest["repositories"][0]["file_checks"][0]["contains_all"] = []
            result = audit_repository(
                manifest,
                repository_id="pythia",
                snapshot_root=snapshot_root,
                repository_ref="refs/heads/main",
                commit_sha=SHA,
            )
            self.assertEqual(
                (result["outcome"], result["reason_code"]),
                (UNKNOWN, "MANIFEST_INVALID"),
            )

    def test_manifest_path_traversal_is_unknown_and_not_hashed(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            _materialize_repository(snapshot_root, self.config("pythia"))
            (snapshot_root / "outside.md").write_text(
                "all required terms\n", encoding="utf-8"
            )
            manifest = copy.deepcopy(self.manifest)
            manifest["repositories"][0]["file_checks"][0]["path"] = (
                "../outside.md"
            )
            result = audit_repository(
                manifest,
                repository_id="pythia",
                snapshot_root=snapshot_root,
                repository_ref="refs/heads/main",
                commit_sha=SHA,
            )
            self.assertEqual(
                (result["outcome"], result["reason_code"]),
                (UNKNOWN, "MANIFEST_INVALID"),
            )
            self.assertEqual(result["files"], [])

    def test_missing_repository_snapshot_is_unknown_not_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.audit("pythia", Path(directory))
            self.assertEqual(
                (result["outcome"], result["reason_code"]),
                (UNKNOWN, "SNAPSHOT_UNAVAILABLE"),
            )

    def test_invalid_commit_sha_is_unknown_not_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            _materialize_repository(snapshot_root, self.config("pythia"))
            result = audit_repository(
                self.manifest,
                repository_id="pythia",
                snapshot_root=snapshot_root,
                repository_ref="refs/heads/main",
                commit_sha="main",
            )
            self.assertEqual(
                (result["outcome"], result["reason_code"]),
                (UNKNOWN, "COMMIT_SHA_INVALID"),
            )

    def test_file_hash_changes_when_checked_content_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            repository_root = _materialize_repository(
                snapshot_root, self.config("pythia")
            )
            first = self.audit("pythia", snapshot_root)
            contract = repository_root / "LOTUS.md"
            contract.write_text(
                contract.read_text(encoding="utf-8") + "extra evidence\n",
                encoding="utf-8",
            )
            second = self.audit("pythia", snapshot_root)
            first_hash = next(
                row["sha256"]
                for row in first["files"]
                if row["path"] == "LOTUS.md"
            )
            second_hash = next(
                row["sha256"]
                for row in second["files"]
                if row["path"] == "LOTUS.md"
            )
            self.assertNotEqual(first_hash, second_hash)


if __name__ == "__main__":
    unittest.main()
