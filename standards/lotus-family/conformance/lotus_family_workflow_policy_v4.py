"""Exact-head review fixes for dynamic runner-state and test arguments."""

from __future__ import annotations

import re
from typing import Any, Mapping

import lotus_family_workflow_policy as execution
import lotus_family_workflow_policy_v2 as policy_v2
import lotus_family_workflow_policy_v3 as previous

_RUNNER_STATE_MUTATION = re.compile(
    r"(?:\bGITHUB_(?:PATH|ENV)\b|"
    r"^\s*(?:export\s+)?PATH\s*=|"
    r"^\s*alias\s+(?:python(?:3)?|mix)\s*=|"
    r"^\s*(?:function\s+)?(?:python(?:3)?|mix)\s*\(\s*\))",
    re.MULTILINE,
)
_SHELL_EXPANSION = re.compile(
    r"(?<!\\)(?:"
    r"\$(?:\{[^}\n]*\}|[A-Za-z_][A-Za-z0-9_]*|\([^\n]*\)|[0-9@*#?$!_-])|"
    r"`|<\(|>\()"
)


_RUNNER_RESOLUTION_ENV_NAMES = {
    "BASH_ENV",
    "ENV",
    "ERL_LIBS",
    "MIX_ARCHIVES",
    "MIX_HOME",
    "MIX_PATH",
    "PATH",
    "PYTHONHOME",
    "PYTHONPATH",
}


def _mutates_runner_state(script: str) -> bool:
    """Fail closed when setup can alter later command or environment meaning."""
    visible = "\n".join(
        execution.legacy.strip_comment(line) for line in script.splitlines()
    )
    return bool(_RUNNER_STATE_MUTATION.search(visible))


def _has_unproven_shell_expansion(command: str) -> bool:
    """Reject dynamic test arguments whose runtime value is not proven here."""
    visible = execution.legacy.strip_comment(command)
    return bool(_SHELL_EXPANSION.search(visible))


def _command_matches(
    discovery: Mapping[str, Any], command: str
) -> list[str]:
    """Match only static test commands with fully visible selection arguments."""
    if _has_unproven_shell_expansion(command):
        return []
    return execution._command_matches(discovery, command)


def _ci_discovery_one(
    discovery: Mapping[str, Any], workflow_text: str
) -> tuple[bool, list[str]]:
    """Find a gating test while failing closed on dynamic runner state."""
    if not policy_v2._workflow_execution_is_gating(workflow_text):
        return False, []
    if policy_v2._uses_pytest(discovery) and policy_v2._has_unproven_pytest_env(
        workflow_text
    ):
        return False, []

    groups = execution._github_run_step_groups(workflow_text)
    scripts = [script for group in groups for script, _ in group]
    yaml_env_names = execution.legacy.yaml_env_names(workflow_text)
    if any(name in _RUNNER_RESOLUTION_ENV_NAMES for name in yaml_env_names):
        return False, []
    if policy_v2._uses_pytest(discovery) and (
        any(name.startswith("PYTEST_") for name in yaml_env_names)
        or any(
            policy_v2._PYTEST_ENV_NAME.search(
                "\n".join(
                    execution.legacy.strip_comment(line)
                    for line in script.splitlines()
                )
            )
            for script in scripts
        )
    ):
        return False, []

    matches: list[str] = []
    for group in groups:
        for script, continue_on_error in group:
            if _mutates_runner_state(script):
                break
            kind, command = execution._analyze_script(script)
            if kind == "invalid":
                break
            if kind in {"empty", "prelude"}:
                continue
            if command is None:
                break

            current = _command_matches(discovery, command)
            if current:
                if continue_on_error is None:
                    break
                if continue_on_error is True:
                    continue
                for pattern in current:
                    if pattern not in matches:
                        matches.append(pattern)
                break

            if continue_on_error is None:
                break
            if continue_on_error is False and previous._proven_failure(command):
                break
            # Ordinary static setup may precede a later gate. Dynamic runner-state
            # changes, proven blockers, and unknown execution policy stop proof.
            continue
    return bool(matches), matches


def ci_discovery(
    discovery: Mapping[str, Any], workflow_texts: str | list[str]
) -> tuple[bool, list[str]]:
    """Evaluate workflow documents independently and union gating matches."""
    texts = workflow_texts if isinstance(workflow_texts, list) else [workflow_texts]
    matched: list[str] = []
    discovered = False
    for text in texts:
        current, patterns = _ci_discovery_one(discovery, text)
        discovered = discovered or current
        for pattern in patterns:
            if pattern not in matched:
                matched.append(pattern)
    return discovered, matched


github_run_scripts = previous.github_run_scripts
shell_commands = previous.shell_commands
pytest_command = previous.pytest_command
mix_command = previous.mix_command

__all__ = [
    "ci_discovery",
    "github_run_scripts",
    "shell_commands",
    "pytest_command",
    "mix_command",
]
