#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("build_request.py")
SPEC = importlib.util.spec_from_file_location("gpt56_build_request", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

ROLES = MODULE.EXPECTED_ROLES
WORKFLOW_SHA = "a" * 40


def profile(repository: str) -> dict:
    return {
        "schema_version": "gpt56-review-profile-v1",
        "repository": repository,
        "profile_id": "test-profile",
        "required_roles": ROLES,
        "required_claim_kinds": ["fact", "observation", "hypothesis"],
        "focus": ["Exact-head evidence and deterministic failure behavior."],
        "authority": {
            "can_execute": False,
            "can_approve": False,
            "can_merge": False,
            "can_deploy": False,
        },
    }


class FabricContractTests(unittest.TestCase):
    def test_rejects_role_downgrade(self) -> None:
        candidate = profile("owner/repo")
        candidate["required_roles"] = ROLES[:-1]
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_profile(candidate, target_repository="owner/repo")

    def test_rejects_authority_escalation(self) -> None:
        candidate = profile("owner/repo")
        candidate["authority"]["can_merge"] = True
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_profile(candidate, target_repository="owner/repo")

    def test_rejects_unpinned_or_wrong_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "adapter.yml"
            path.write_text(
                "on:\n  pull_request:\n  push:\npermissions: {}\njobs:\n  fabric:\n    permissions:\n      contents: read\n    uses: safal207/pythiaLabs/.github/workflows/gpt56-review-fabric-v1.yml@main\n    with:\n      profile_path: .gpt56/review-profile.json\n",
                encoding="utf-8",
            )
            with self.assertRaises(MODULE.ContractError):
                MODULE.validate_adapter(path, workflow_sha=WORKFLOW_SHA)

    def test_build_is_deterministic_and_exact_head_bound(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subject = root / "subject"
            subject.mkdir()
            subprocess.run(["git", "init", "-q", subject], check=True)
            subprocess.run(["git", "-C", subject, "config", "user.email", "ci@example.invalid"], check=True)
            subprocess.run(["git", "-C", subject, "config", "user.name", "CI"], check=True)
            (subject / "README.md").write_text("subject\n", encoding="utf-8")
            subprocess.run(["git", "-C", subject, "add", "README.md"], check=True)
            subprocess.run(["git", "-C", subject, "commit", "-q", "-m", "subject"], check=True)
            head = subprocess.run(
                ["git", "-C", subject, "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()

            profile_path = subject / ".gpt56/review-profile.json"
            profile_path.parent.mkdir()
            profile_path.write_text(json.dumps(profile("owner/repo")), encoding="utf-8")
            adapter = subject / ".github/workflows/gpt56-review-fabric.yml"
            adapter.parent.mkdir(parents=True)
            adapter.write_text(
                "name: GPT-5.6 Review Fabric\non:\n  pull_request:\n  push:\npermissions: {}\njobs:\n  fabric:\n    permissions:\n      contents: read\n    uses: safal207/pythiaLabs/.github/workflows/gpt56-review-fabric-v1.yml@" + WORKFLOW_SHA + "\n    with:\n      profile_path: .gpt56/review-profile.json\n",
                encoding="utf-8",
            )
            registry = root / "roles.json"
            registry.write_text(
                json.dumps({
                    "schema_version": "gpt56-role-registry-v1",
                    "roles": [
                        {"id": role, "purpose": "purpose", "required_questions": ["q1", "q2"]}
                        for role in ROLES
                    ],
                }),
                encoding="utf-8",
            )

            outputs = []
            for name in ("one", "two"):
                output = root / name
                MODULE.build_outputs(
                    subject_root=subject,
                    profile_path=profile_path,
                    registry_path=registry,
                    adapter_path=adapter,
                    output_dir=output,
                    target_repository="owner/repo",
                    source_repository="owner/repo",
                    expected_sha=head,
                    change_number=7,
                    workflow_repository="safal207/pythiaLabs",
                    workflow_sha=WORKFLOW_SHA,
                )
                outputs.append({path.name: path.read_bytes() for path in output.iterdir()})
            self.assertEqual(outputs[0], outputs[1])

            with self.assertRaises(MODULE.ContractError):
                MODULE.build_outputs(
                    subject_root=subject,
                    profile_path=profile_path,
                    registry_path=registry,
                    adapter_path=adapter,
                    output_dir=root / "stale",
                    target_repository="owner/repo",
                    source_repository="owner/repo",
                    expected_sha="b" * 40,
                    change_number=7,
                    workflow_repository="safal207/pythiaLabs",
                    workflow_sha=WORKFLOW_SHA,
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
