import tempfile
import unittest
from pathlib import Path
import lotus_family_auditor_legacy_tests as old


def workflow(command, env=""):
    env_block = "env:\n" + "\n".join(f"  {x}" for x in env.splitlines()) + "\n" if env else ""
    body = "\n".join(f"          {x}" if x else "" for x in command.splitlines())
    return ("name: CI\n" + env_block + "jobs:\n  test:\n    runs-on: ubuntu-latest\n"
            "    steps:\n      - name: Run tests\n        run: |\n" + body + "\n")


def fixture(discovery):
    if discovery.get("strategy") == "pytest_default_discovery":
        command = "python -m pytest \\\n  --junitxml=artifacts/junit.xml \\\n  --cov=cml\n"
    else:
        pattern = discovery["contains_any"][0]
        command = f"python -m pytest {pattern}\n" if pattern.endswith(".py") else pattern + "\n"
    return workflow(command)


def assert_drift(self, repo_id, command, *, raw=False, env=""):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = old._materialize_repository(root, self.config(repo_id))
        self.workflow(repo).write_text(command if raw else workflow(command, env), encoding="utf-8")
        result = self.audit(repo_id, root)
        self.assertEqual(result["outcome"], old.DRIFT)
        self.assertEqual(self.discovery(result)["outcome"], old.DRIFT)
        self.assertEqual(self.discovery(result)["matched_patterns"], [])


old._discovery_fixture = fixture
old.LotusFamilyAuditorTest.assert_ci_drift = assert_drift


def bare(self):
    self.assert_ci_drift("cml", "python -m pytest\n", raw=True)


def workflow_env_text(self):
    self.assert_ci_drift("cml", "name: CI\nenv:\n  NOTE: |\n    python -m pytest\n"
                         "jobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n"
                         "      - uses: actions/checkout@v4\n", raw=True)


def step_env_text(self):
    self.assert_ci_drift("cml", "name: CI\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
                         "    steps:\n      - name: Metadata only\n        env:\n"
                         "          NOTE: python -m pytest\n        uses: actions/checkout@v4\n", raw=True)


def fake_steps_in_metadata(self):
    self.assert_ci_drift("cml", "name: CI\nmetadata:\n  fake-job:\n    steps:\n"
                         "      - run: python -m pytest\njobs: {}\n", raw=True)


def cml_addopts(self):
    self.assert_ci_drift("cml", "PYTEST_ADDOPTS='--ignore=tests/test_lotus_docs_contract.py' python -m pytest\n")


def ls_addopts(self):
    self.assert_ci_drift("ls", "PYTEST_ADDOPTS='--ignore=tests/test_lotus_docs_contract.py' "
                          "python -m pytest tests/test_lotus_docs_contract.py\n")


def yaml_addopts(self):
    self.assert_ci_drift("cml", "python -m pytest\n",
                         env="PYTEST_ADDOPTS: --ignore=tests/test_lotus_docs_contract.py")


def pytest_plugins(self):
    self.assert_ci_drift("cml", "PYTEST_PLUGINS=custom_plugin python -m pytest\n")


new_tests = {
    "test_bare_shell_text_is_not_a_run_step": bare,
    "test_pytest_text_in_workflow_env_value_is_not_executed": workflow_env_text,
    "test_pytest_text_in_step_env_value_is_not_executed": step_env_text,
    "test_steps_outside_jobs_are_not_executable": fake_steps_in_metadata,
    "test_cml_pytest_addopts_assignment_is_drift": cml_addopts,
    "test_ls_pytest_addopts_assignment_is_drift": ls_addopts,
    "test_workflow_pytest_addopts_env_is_drift": yaml_addopts,
    "test_pytest_plugin_environment_assignment_is_drift": pytest_plugins,
}
for name, method in new_tests.items():
    setattr(old.LotusFamilyAuditorTest, name, method)

LotusFamilyAuditorTest = old.LotusFamilyAuditorTest

if __name__ == "__main__":
    unittest.main()
