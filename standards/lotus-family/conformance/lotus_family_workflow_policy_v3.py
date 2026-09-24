"""Exact-head review fixes for Lotus workflow discovery reachability."""

from __future__ import annotations

import re
from typing import Any, Mapping

import lotus_family_workflow_hardened as base
import lotus_family_workflow_policy as execution
import lotus_family_workflow_policy_v2 as previous

_PROVEN_FAILURE_COMMANDS = {"false"}
_SHELL_WRAPPERS = {"command", "builtin"}
_COMMAND_RESOLUTION_MUTATION = re.compile(
    r"(?:\bGITHUB_PATH\b|"
    r"^\s*(?:export\s+)?PATH\s*=|"
    r"^\s*alias\s+(?:python(?:3)?|mix)\s*=|"
    r"^\s*(?:function\s+)?(?:python(?:3)?|mix)\s*\(\s*\))",
    re.MULTILINE,
)


def _proven_failure(command: str) -> bool:
    """Recognize literal or shell-builtin-wrapped deterministic failures."""
    parts = base._tokens(command)
    if not parts:
        return False
    if parts[0] in _PROVEN_FAILURE_COMMANDS:
        return True
    if parts[0] not in _SHELL_WRAPPERS:
        return False

    index = 1
    while index < len(parts) and parts[index].startswith("-"):
        index += 1
    return index < len(parts) and parts[index] in _PROVEN_FAILURE_COMMANDS


def _mutates_command_resolution(script: str) -> bool:
    """Fail closed when setup can replace the later Python or Mix executable."""
    visible = "\n".join(
        execution.legacy.strip_comment(line) for line in script.splitlines()
    )
    return bool(_COMMAND_RESOLUTION_MUTATION.search(visible))


def _ci_discovery_one(
    discovery: Mapping[str, Any], workflow_text: str
) -> tuple[bool, list[str]]:
    """Find a gating test while failing closed on unknown step policy."""
    if not previous._workflow_execution_is_gating(workflow_text):
        return False, []
    if previous._uses_pytest(discovery) and previous._has_unproven_pytest_env(
        workflow_text
    ):
        return False, []

    groups = execution._github_run_step_groups(workflow_text)
    scripts = [script for group in groups for script, _ in group]
    if previous._uses_pytest(discovery) and (
        any(
            name.startswith("PYTEST_")
            for name in execution.legacy.yaml_env_names(workflow_text)
        )
        or any(
            previous._PYTEST_ENV_NAME.search(
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
            if _mutates_command_resolution(script):
                break
            kind, command = execution._analyze_script(script)
            if kind == "invalid":
                break
            if kind in {"empty", "prelude"}:
                continue
            if command is None:
                break

            current = execution._command_matches(discovery, command)
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
            if continue_on_error is False and _proven_failure(command):
                break
            # Ordinary setup steps may precede a later gating test. Only a
            # proven blocker, command-resolution mutation, or unknown execution
            # policy stops reachability.
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
