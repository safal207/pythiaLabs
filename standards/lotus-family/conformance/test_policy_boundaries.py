"""Focused fail-closed regression checks for Lotus policy boundaries."""

from __future__ import annotations

import copy
import unittest

from lotus_family_system_model import EDGE_COLS, NODE_COLS, ROUTE_COLS, rows
from lotus_family_workflow import ci_discovery


def workflow(command: str, *, env: str = "") -> str:
    """Build one workflow with a single multiline run step."""
    env_block = f"env:\n  {env}\n" if env else ""
    body = "\n".join(
        f"          {line}" for line in command.splitlines()
    )
    return (
        "name: CI\n"
        f"{env_block}"
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - name: Run tests\n"
        "        run: |\n"
        f"{body}\n"
    )


def workflow_steps(steps: str) -> str:
    """Build one workflow from already indented step-list entries."""
    return (
        "name: CI\n"
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        f"{steps}"
    )


DISCOVERY = {
    "strategy": "pytest_default_discovery",
    "test_path": "tests/test_lotus_docs_contract.py",
    "command": "python -m pytest",
}
MIX_DISCOVERY = {
    "strategy": "mix_default_discovery",
    "test_path": "test/lotus_docs_contract_test.exs",
    "command": "mix test",
}
EXPLICIT_PY_DISCOVERY = {
    "strategy": "contains_any",
    "contains_any": ["tests/test_lotus_docs_contract.py"],
}
EXPLICIT_MIX_DISCOVERY = {
    "strategy": "contains_any",
    "contains_any": ["test/lotus_docs_contract_test.exs"],
}


class WorkflowBoundaryTest(unittest.TestCase):
    """Exercise public fail-closed workflow discovery boundaries."""

    def test_workflow_documents_are_evaluated_independently(self) -> None:
        blocked = workflow(
            "echo no tests",
            env=(
                "PYTEST_ADDOPTS: "
                "--ignore=tests/test_lotus_docs_contract.py"
            ),
        )
        clean = workflow("python -m pytest")
        self.assertEqual(
            ci_discovery(DISCOVERY, [blocked, clean]),
            (True, ["python -m pytest"]),
        )

    def test_anchored_pytest_env_mapping_blocks_discovery(self) -> None:
        text = (
            "name: CI\n"
            "env: &pytest_env\n"
            "  PYTEST_ADDOPTS: "
            "--ignore=tests/test_lotus_docs_contract.py\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - name: Contract test\n"
            "        run: python -m pytest\n"
        )
        self.assertEqual(ci_discovery(DISCOVERY, text), (False, []))

    def test_aliased_env_mapping_fails_closed(self) -> None:
        text = (
            "name: CI\n"
            "pytest-env: &pytest_env\n"
            "  SAFE_VALUE: true\n"
            "env: *pytest_env\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - name: Contract test\n"
            "        run: python -m pytest\n"
        )
        self.assertEqual(ci_discovery(DISCOVERY, text), (False, []))

    def test_unknown_failing_predecessor_blocks_later_pytest(self) -> None:
        self.assertEqual(
            ci_discovery(
                DISCOVERY,
                workflow("false\npython -m pytest"),
            ),
            (False, []),
        )

    def test_known_safe_shell_prelude_keeps_pytest_reachable(self) -> None:
        self.assertEqual(
            ci_discovery(
                DISCOVERY,
                workflow("set -euo pipefail\npython -m pytest"),
            ),
            (True, ["python -m pytest"]),
        )

    def test_earlier_run_step_can_block_later_test_step(self) -> None:
        text = workflow_steps(
            "      - name: Earlier failure\n"
            "        run: false\n"
            "      - name: Contract test\n"
            "        run: python -m pytest\n"
        )
        self.assertEqual(
            ci_discovery(DISCOVERY, text),
            (False, []),
        )

    def test_normal_setup_step_keeps_later_mix_test_discoverable(self) -> None:
        text = workflow_steps(
            "      - name: Install local tooling\n"
            "        run: mix local.hex --force\n"
            "      - name: Contract test\n"
            "        run: mix test\n"
        )
        self.assertEqual(
            ci_discovery(MIX_DISCOVERY, text),
            (True, ["mix test"]),
        )

    def test_explicitly_ignored_predecessor_keeps_test_reachable(self) -> None:
        text = workflow_steps(
            "      - name: Allowed failure\n"
            "        continue-on-error: true\n"
            "        run: false\n"
            "      - name: Contract test\n"
            "        run: python -m pytest\n"
        )
        self.assertEqual(
            ci_discovery(DISCOVERY, text),
            (True, ["python -m pytest"]),
        )

    def test_test_step_cannot_ignore_its_own_failure(self) -> None:
        text = workflow_steps(
            "      - name: Non-gating contract test\n"
            "        continue-on-error: true\n"
            "        run: python -m pytest\n"
        )
        self.assertEqual(
            ci_discovery(DISCOVERY, text),
            (False, []),
        )

    def test_path_qualified_shell_template_is_rejected(self) -> None:
        text = workflow_steps(
            "      - name: Repo controlled shell\n"
            "        shell: ./bash {0}\n"
            "        run: python -m pytest\n"
        )
        self.assertEqual(
            ci_discovery(DISCOVERY, text),
            (False, []),
        )

    def test_dynamic_test_arguments_fail_closed(self) -> None:
        cases = (
            (
                EXPLICIT_PY_DISCOVERY,
                "python -m pytest tests/test_lotus_docs_contract.py $FILTER",
            ),
            (
                EXPLICIT_MIX_DISCOVERY,
                "mix test test/lotus_docs_contract_test.exs ${FILTER}",
            ),
        )
        for discovery, command in cases:
            with self.subTest(command=command):
                self.assertEqual(
                    ci_discovery(discovery, workflow(command)),
                    (False, []),
                )

    def test_github_env_mutation_blocks_later_test(self) -> None:
        text = workflow_steps(
            "      - name: Mutate future pytest selection\n"
            "        run: echo 'PYTEST_ADDOPTS=-k smoke' >> \"$GITHUB_ENV\"\n"
            "      - name: Contract test\n"
            "        run: python -m pytest\n"
        )
        self.assertEqual(
            ci_discovery(DISCOVERY, text),
            (False, []),
        )


class CompactModelBoundaryTest(unittest.TestCase):
    """Exercise compact graph and route collection boundaries."""

    def test_compact_collections_must_be_non_empty_lists(self) -> None:
        for key, columns in (
            ("nodes", NODE_COLS),
            ("edges", EDGE_COLS),
            ("routes", ROUTE_COLS),
        ):
            with self.subTest(key=key):
                model = {
                    f"{key[:-1]}_columns": copy.deepcopy(columns),
                    key: [],
                }
                with self.assertRaisesRegex(
                    ValueError, "non-empty list"
                ):
                    rows(model, key, columns)


if __name__ == "__main__":
    unittest.main()
