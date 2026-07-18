"""Final review hardening overlay for Lotus workflow discovery."""

from __future__ import annotations

import re
import shlex
from typing import Any, Mapping

import lotus_family_workflow_policy as previous


_NON_FAIL_FAST_CUSTOM_SHELLS = {
    ("bash", "{0}"),
    ("sh", "{0}"),
}
_PYTEST_ENV_NAME = re.compile(r"\bPYTEST_[A-Za-z0-9_]*\b")
_YAML_ANCHOR_ONLY = re.compile(r"&\S+\Z")
_YAML_ALIAS_ONLY = re.compile(r"\*\S+\Z")


def _shell_parts(value: str) -> tuple[str, ...] | None:
    """Parse one literal shell value without accepting expressions."""
    scalar = previous.legacy.inline_scalar(value)
    if scalar is None:
        return None
    try:
        parts = tuple(shlex.split(scalar))
    except ValueError:
        return None
    return parts or None


def _uses_non_fail_fast_custom_shell(text: str) -> bool:
    """Reject custom bash/sh templates that can mask a failed test command."""
    lines = text.splitlines()
    ranges = previous.legacy.scalar_ranges(lines)
    scalar_body = {
        row
        for start, (end, _) in ranges.items()
        for row in range(start + 1, end)
    }
    for row, line in enumerate(lines):
        if row in scalar_body:
            continue
        header = previous.legacy.yaml_header(line)
        if header is None or header[3] != "shell":
            continue
        if _shell_parts(header[4]) in _NON_FAIL_FAST_CUSTOM_SHELLS:
            return True
    return False


def _has_non_gating_job(text: str) -> bool:
    """Reject jobs whose failure is ignored or controlled by an expression."""
    lines = text.splitlines()
    ranges = previous.legacy.scalar_ranges(lines)
    scalar_body = {
        row
        for start, (end, _) in ranges.items()
        for row in range(start + 1, end)
    }
    top = previous.base._properties(lines, 0, len(lines), -1, scalar_body)
    jobs = top.get("jobs")
    if jobs is None:
        return False
    children = previous.base._mapping_children(lines, jobs, scalar_body)
    if children is None:
        return True
    for _, (job_row, job_header) in children.items():
        job_end = previous.legacy.block_end(lines, job_row, job_header[2])
        properties = previous.base._properties(
            lines,
            job_row + 1,
            job_end,
            job_header[2],
            scalar_body,
        )
        value = previous._boolean_entry(
            properties.get("continue-on-error"),
            default=False,
        )
        if value is not False:
            return True
    return False


def _uses_pytest(discovery: Mapping[str, Any]) -> bool:
    """Return true when repository configuration can affect discovery."""
    if discovery.get("strategy") == "pytest_default_discovery":
        return True
    values = discovery.get("contains_any", [])
    return isinstance(values, list) and any(
        isinstance(value, str) and value.split("::", 1)[0].endswith(".py")
        for value in values
    )


def _has_unproven_pytest_env(text: str) -> bool:
    """Reject pytest env hidden behind aliases or anchored mapping syntax."""
    lines = text.splitlines()
    ranges = previous.legacy.scalar_ranges(lines)
    scalar_body = {
        row
        for start, (end, _) in ranges.items()
        for row in range(start + 1, end)
    }
    for index, line in enumerate(lines):
        if index in scalar_body:
            continue
        header = previous.legacy.yaml_header(line)
        if header is None or header[3] != "env":
            continue

        inline = previous.legacy.strip_comment(header[4]).strip()
        if _YAML_ALIAS_ONLY.fullmatch(inline):
            return True
        if inline.startswith("&") and not _YAML_ANCHOR_ONLY.fullmatch(inline):
            return True
        if inline and not _YAML_ANCHOR_ONLY.fullmatch(inline):
            if _PYTEST_ENV_NAME.search(inline):
                return True
            continue

        for row in range(index + 1, len(lines)):
            if row in scalar_body:
                continue
            if not lines[row].strip() or lines[row].lstrip().startswith("#"):
                continue
            indent = previous.legacy.indent_of(lines[row])
            if indent is None or indent <= header[2]:
                break
            child = previous.legacy.yaml_header(lines[row])
            if (
                child is not None
                and not child[1]
                and child[2] > header[2]
                and child[3].startswith("PYTEST_")
            ):
                return True
    return False


def _workflow_execution_is_gating(text: str) -> bool:
    """Require fail-fast shells and jobs whose failure gates the workflow."""
    return not (
        _uses_non_fail_fast_custom_shell(text)
        or _has_non_gating_job(text)
    )


def github_run_scripts(text: str) -> list[str]:
    """Expose scripts only from workflows with a gating execution context."""
    if not _workflow_execution_is_gating(text):
        return []
    return previous.github_run_scripts(text)


def _ci_discovery_one(
    discovery: Mapping[str, Any], workflow_text: str
) -> tuple[bool, list[str]]:
    """Evaluate one workflow only after proving its execution remains gating."""
    if not _workflow_execution_is_gating(workflow_text):
        return False, []
    if _uses_pytest(discovery) and _has_unproven_pytest_env(workflow_text):
        return False, []
    return previous._ci_discovery_one(discovery, workflow_text)


def ci_discovery(
    discovery: Mapping[str, Any], workflow_texts: str | list[str]
) -> tuple[bool, list[str]]:
    """Evaluate documents independently and union only gating matches."""
    texts = (
        workflow_texts
        if isinstance(workflow_texts, list)
        else [workflow_texts]
    )
    matched: list[str] = []
    discovered = False
    for text in texts:
        current, patterns = _ci_discovery_one(discovery, text)
        discovered = discovered or current
        for pattern in patterns:
            if pattern not in matched:
                matched.append(pattern)
    return discovered, matched


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
