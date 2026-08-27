"""Regression coverage for the exact-head workflow policy v3 fixes."""

from __future__ import annotations

import unittest

from lotus_family_workflow import ci_discovery

DISCOVERY = {
    "strategy": "pytest_default_discovery",
    "test_path": "tests/test_lotus_docs_contract.py",
    "command": "python -m pytest",
}


def workflow_steps(steps: str) -> str:
    """Build one runnable workflow from indented step-list entries."""
    return (
        "name: CI\n"
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        f"{steps}"
    )


class WorkflowPolicyV3BoundaryTest(unittest.TestCase):
    """Keep unknown policy, blockers, and runner resolution fail-closed."""

    def test_expression_continue_on_error_blocks_later_test(self) -> None:
        text = workflow_steps(
            "      - name: Matrix-controlled contract test\n"
            "        continue-on-error: ${{ matrix.allow_failure }}\n"
            "        run: python -m pytest\n"
            "      - name: Later contract test\n"
            "        run: python -m pytest\n"
        )
        self.assertEqual(ci_discovery(DISCOVERY, text), (False, []))

    def test_wrapped_false_blocks_later_test(self) -> None:
        for command in ("command false", "builtin false"):
            with self.subTest(command=command):
                text = workflow_steps(
                    "      - name: Proven wrapped failure\n"
                    f"        run: {command}\n"
                    "      - name: Contract test\n"
                    "        run: python -m pytest\n"
                )
                self.assertEqual(ci_discovery(DISCOVERY, text), (False, []))

    def test_github_path_mutation_blocks_later_test(self) -> None:
        text = workflow_steps(
            "      - name: Replace command resolution\n"
            "        run: echo \"$PWD/bin\" >> \"$GITHUB_PATH\"\n"
            "      - name: Contract test\n"
            "        run: python -m pytest\n"
        )
        self.assertEqual(ci_discovery(DISCOVERY, text), (False, []))

    def test_local_action_blocks_later_test(self) -> None:
        text = workflow_steps(
            "      - name: Repository-controlled setup\n"
            "        uses: ./fake-runner\n"
            "      - name: Contract test\n"
            "        run: python -m pytest\n"
        )
        self.assertEqual(ci_discovery(DISCOVERY, text), (False, []))

    def test_external_action_blocks_later_test(self) -> None:
        text = workflow_steps(
            "      - name: Unproven external setup\n"
            "        uses: attacker/fake-python@v1\n"
            "      - name: Contract test\n"
            "        run: python -m pytest\n"
        )
        self.assertEqual(ci_discovery(DISCOVERY, text), (False, []))

    def test_direct_path_and_runner_alias_mutations_block_later_test(self) -> None:
        commands = (
            "export PATH=\"$PWD/bin:$PATH\"",
            "alias python='true'",
            "python() { true; }",
        )
        for command in commands:
            with self.subTest(command=command):
                text = workflow_steps(
                    "      - name: Mutate runner resolution\n"
                    f"        run: {command}\n"
                    "      - name: Contract test\n"
                    "        run: python -m pytest\n"
                )
                self.assertEqual(ci_discovery(DISCOVERY, text), (False, []))

    def test_yaml_command_resolution_environment_is_rejected(self) -> None:
        cases = (
            (
                "workflow PATH",
                "env:\n  PATH: ./fake-bin:/usr/bin\n",
                "",
                "",
            ),
            (
                "job PYTHONPATH",
                "",
                "    env:\n      PYTHONPATH: ./fake-modules\n",
                "",
            ),
            (
                "step PATH",
                "",
                "",
                "        env:\n          PATH: ./fake-bin:/usr/bin\n",
            ),
            (
                "anchored workflow PATH",
                "env: &runner_env\n  PATH: ./fake-bin:/usr/bin\n",
                "",
                "",
            ),
            (
                "unresolved job env alias",
                "x-runner-env: &runner_env\n  FOO: bar\n",
                "    env: *runner_env\n",
                "",
            ),
        )
        for name, workflow_env, job_env, step_env in cases:
            with self.subTest(name=name):
                text = (
                    "name: CI\n"
                    f"{workflow_env}"
                    "jobs:\n"
                    "  test:\n"
                    "    runs-on: ubuntu-latest\n"
                    f"{job_env}"
                    "    steps:\n"
                    "      - name: Contract test\n"
                    f"{step_env}"
                    "        run: python -m pytest\n"
                )
                self.assertEqual(
                    ci_discovery(DISCOVERY, text),
                    (False, []),
                )


if __name__ == "__main__":
    unittest.main()
