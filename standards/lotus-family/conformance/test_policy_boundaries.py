"""Focused fail-closed regression checks for Lotus policy boundaries."""

from __future__ import annotations

import copy
import unittest

from lotus_family_system_model import EDGE_COLS, NODE_COLS, ROUTE_COLS, rows
from lotus_family_workflow import ci_discovery


def workflow(command: str, *, env: str = "") -> str:
    env_block = f"env:\n  {env}\n" if env else ""
    body = "\n".join(f"          {line}" for line in command.splitlines())
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


DISCOVERY = {
    "strategy": "pytest_default_discovery",
    "test_path": "tests/test_lotus_docs_contract.py",
    "command": "python -m pytest",
}


class WorkflowBoundaryTest(unittest.TestCase):
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


class CompactModelBoundaryTest(unittest.TestCase):
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
                with self.assertRaisesRegex(ValueError, "non-empty list"):
                    rows(model, key, columns)


if __name__ == "__main__":
    unittest.main()
