from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from lotus_family_auditor import DRIFT, PASS, UNKNOWN, audit_repository, load_manifest

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
        return "python -m pytest \\\n  --junitxml=artifacts/junit.xml \\\n  --cov=cml\n"
    return "\n".join(discovery["contains_any"]) + "\n"


def _materialize_repository(snapshot_root: Path, config: dict) -> Path:
    repository_root = snapshot_root / config["snapshot_dir"]
    terms_by_path: dict[str, list[str]] = {}
    for check in config["file_checks"]:
        terms_by_path.setdefault(check["path"], []).extend(check["contains_all"])
    for relative_path, terms in terms_by_path.items():
        _write(repository_root, relative_path, "\n".join(dict.fromkeys(terms)) + "\n")
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
            row for row in self.manifest["repositories"] if row["id"] == repository_id
        )

    def audit(self, repository_id: str, snapshot_root: Path):
        return audit_repository(
            self.manifest,
            repository_id=repository_id,
            snapshot_root=snapshot_root,
            repository_ref="refs/heads/main",
            commit_sha=SHA,
        )

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
            discovery = next(
                row for row in result["checks"] if row["check_id"] == "ci_discovery"
            )
            self.assertEqual(discovery["matched_patterns"], ["python -m pytest"])

    def test_bilingual_authority_deletion_is_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            config = copy.deepcopy(self.config("cml"))
            repository_root = _materialize_repository(snapshot_root, config)
            contract = repository_root / "docs/LOTUS.md"
            contract.write_text(
                contract.read_text(encoding="utf-8").replace(
                    "не имеет права собственности", ""
                ),
                encoding="utf-8",
            )

            result = self.audit("cml", snapshot_root)

            self.assertEqual(result["outcome"], DRIFT)
            self.assertEqual(result["reason_code"], "LOTUS_CONTRACT_DRIFT")
            authority_check = next(
                row
                for row in result["checks"]
                if row["check_id"] == "bilingual_contract"
            )
            self.assertIn(
                "не имеет права собственности",
                authority_check["missing_terms"],
            )

    def test_contract_test_not_discovered_by_ci_is_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            config = self.config("ls")
            repository_root = _materialize_repository(snapshot_root, config)
            workflow = repository_root / ".github/workflows/ci.yml"
            workflow.write_text("python -m pytest tests/test_other.py\n", encoding="utf-8")

            result = self.audit("ls", snapshot_root)

            self.assertEqual(result["outcome"], DRIFT)
            discovery = next(
                row for row in result["checks"] if row["check_id"] == "ci_discovery"
            )
            self.assertEqual(discovery["outcome"], DRIFT)
            self.assertEqual(discovery["matched_patterns"], [])

    def test_cml_unrelated_pytest_subset_is_not_full_discovery(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            config = self.config("cml")
            repository_root = _materialize_repository(snapshot_root, config)
            workflow = repository_root / ".github/workflows/ci.yml"
            workflow.write_text(
                "python -m pytest tests/test_other.py\n",
                encoding="utf-8",
            )

            result = self.audit("cml", snapshot_root)

            self.assertEqual(result["outcome"], DRIFT)
            discovery = next(
                row for row in result["checks"] if row["check_id"] == "ci_discovery"
            )
            self.assertEqual(discovery["outcome"], DRIFT)
            self.assertEqual(discovery["matched_patterns"], [])

    def test_cml_pytest_ignore_of_contract_test_is_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            config = self.config("cml")
            repository_root = _materialize_repository(snapshot_root, config)
            workflow = repository_root / ".github/workflows/ci.yml"
            workflow.write_text(
                "python -m pytest --ignore=tests/test_lotus_docs_contract.py\n",
                encoding="utf-8",
            )

            result = self.audit("cml", snapshot_root)

            self.assertEqual(result["outcome"], DRIFT)
            discovery = next(
                row for row in result["checks"] if row["check_id"] == "ci_discovery"
            )
            self.assertEqual(discovery["outcome"], DRIFT)

    def test_cml_commented_pytest_command_is_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            config = self.config("cml")
            repository_root = _materialize_repository(snapshot_root, config)
            workflow = repository_root / ".github/workflows/ci.yml"
            workflow.write_text("# python -m pytest\n", encoding="utf-8")

            result = self.audit("cml", snapshot_root)

            self.assertEqual(result["outcome"], DRIFT)
            discovery = next(
                row for row in result["checks"] if row["check_id"] == "ci_discovery"
            )
            self.assertEqual(discovery["matched_patterns"], [])

    def test_cml_pytest_ignore_directory_covering_contract_test_is_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            config = self.config("cml")
            repository_root = _materialize_repository(snapshot_root, config)
            workflow = repository_root / ".github/workflows/ci.yml"
            workflow.write_text(
                "python -m pytest --ignore=tests\n",
                encoding="utf-8",
            )

            result = self.audit("cml", snapshot_root)

            self.assertEqual(result["outcome"], DRIFT)
            discovery = next(
                row for row in result["checks"] if row["check_id"] == "ci_discovery"
            )
            self.assertEqual(discovery["matched_patterns"], [])

    def test_cml_pytest_ignore_glob_covering_contract_test_is_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory)
            config = self.config("cml")
            repository_root = _materialize_repository(snapshot_root, config)
            workflow = repository_root / ".github/workflows/ci.yml"
            workflow.write_text(
                "python -m pytest --ignore-glob='tests/*'\n",
                encoding="utf-8",
            )

            result = self.audit("cml", snapshot_root)

            self.assertEqual(result["outcome"], DRIFT)
            discovery = next(
                row for row in result["checks"] if row["check_id"] == "ci_discovery"
            )
            self.assertEqual(discovery["matched_patterns"], [])

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
            outside = snapshot_root / "outside.md"
            outside.write_text("all required terms\n", encoding="utf-8")
            manifest = copy.deepcopy(self.manifest)
            manifest["repositories"][0]["file_checks"][0]["path"] = "../outside.md"

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
                row["sha256"] for row in first["files"] if row["path"] == "LOTUS.md"
            )
            second_hash = next(
                row["sha256"] for row in second["files"] if row["path"] == "LOTUS.md"
            )
            self.assertNotEqual(first_hash, second_hash)


if __name__ == "__main__":
    unittest.main()
