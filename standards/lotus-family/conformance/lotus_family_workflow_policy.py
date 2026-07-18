"""Final fail-closed execution policy for Lotus GitHub Actions discovery."""

from __future__ import annotations

import re
import shlex
from pathlib import PurePosixPath
from typing import Any, Mapping

import lotus_family_workflow_hardened as base
import lotus_family_workflow_legacy as legacy

_POSIX_SHELLS = {"bash", "sh"}
_SHELL_WRAPPERS = {"command", "builtin", "eval"}
_TERMINATORS = {"exit", "exec", "return", "break", "continue"}
_CONTROL = legacy.CONTROL_TOKENS | {"(", ")", "{", "}"}


def _supported_shell(value: str) -> bool:
    """Accept only shell forms that provably execute the generated script."""
    scalar = legacy.inline_scalar(value)
    if scalar is None:
        return False
    try:
        parts = shlex.split(scalar)
    except ValueError:
        return False
    if not parts:
        return False
    shell = PurePosixPath(parts[0]).name
    if shell not in _POSIX_SHELLS:
        return False
    if len(parts) == 1:
        return True
    allowed = {
        ("bash", "{0}"),
        ("bash", "-e", "{0}"),
        ("bash", "--noprofile", "--norc", "-e", "-o", "pipefail", "{0}"),
        ("sh", "{0}"),
        ("sh", "-e", "{0}"),
    }
    return tuple([shell, *parts[1:]]) in allowed


def _dependencies_proven(
    job_name: str, dependency_graph: Mapping[str, list[str] | None]
) -> bool:
    """Reject missing, self-referential, or cyclic needs topologies."""
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(name: str) -> bool:
        if name in visiting:
            return False
        if name in visited:
            return True
        dependencies = dependency_graph.get(name)
        if dependencies is None:
            return False
        visiting.add(name)
        for dependency in dependencies:
            if dependency not in dependency_graph or not visit(dependency):
                return False
        visiting.remove(name)
        visited.add(name)
        return True

    return visit(job_name)


def github_run_scripts(text: str) -> list[str]:
    """Extract only reachable, repo-root scripts under the final shell policy."""
    lines = text.splitlines()
    ranges = legacy.scalar_ranges(lines)
    scalar_body = {
        row
        for start, (end, _) in ranges.items()
        for row in range(start + 1, end)
    }
    top = base._properties(lines, 0, len(lines), -1, scalar_body)
    jobs = top.get("jobs")
    if jobs is None:
        return []
    workflow_defaults = base._run_defaults(lines, top, scalar_body)
    jobs_children = base._mapping_children(lines, jobs, scalar_body)
    if workflow_defaults is None or jobs_children is None:
        return []

    records = {}
    dependency_graph: dict[str, list[str] | None] = {}
    for job_name, (job_row, job_header) in jobs_children.items():
        job_end = legacy.block_end(lines, job_row, job_header[2])
        properties = base._properties(
            lines, job_row + 1, job_end, job_header[2], scalar_body
        )
        records[job_name] = (job_row, job_header, job_end, properties)
        needs = properties.get("needs")
        dependency_graph[job_name] = (
            [] if needs is None else base._parse_needs(needs[1][4])
        )

    scripts: list[str] = []
    for job_name, (_, _, job_end, properties) in records.items():
        runs_on = properties.get("runs-on")
        if runs_on is None or legacy.inline_scalar(runs_on[1][4]) is None:
            continue
        needs = properties.get("needs")
        dependencies = dependency_graph[job_name]
        if not _dependencies_proven(job_name, dependency_graph):
            continue
        job_if = properties.get("if")
        if needs is not None:
            if not dependencies or job_if is None or base._condition(job_if[1][4]) != "always()":
                continue
        elif job_if is not None and base._condition(job_if[1][4]) != "true":
            continue

        job_defaults = base._run_defaults(lines, properties, scalar_body)
        steps = properties.get("steps")
        if job_defaults is None or steps is None:
            continue
        if legacy.inline_scalar(steps[1][4]) is not None or legacy.scalar_indicator(steps[1][4]) is not None:
            continue
        steps_end = legacy.block_end(lines, steps[0], steps[1][2])
        items = legacy.item_starts(lines, steps[0] + 1, steps_end, scalar_body)

        for index, item_row in enumerate(items):
            item_end = items[index + 1] if index + 1 < len(items) else steps_end
            first = legacy.yaml_header(lines[item_row])
            if first is None or not first[1]:
                continue
            step = {first[3]: (item_row, first)}
            for row in range(item_row + 1, item_end):
                if row in scalar_body:
                    continue
                header = legacy.yaml_header(lines[row])
                if header is not None and not header[1] and header[2] == first[2]:
                    step[header[3]] = (row, header)
            step_if = step.get("if")
            if step_if is not None and base._condition(step_if[1][4]) != "true":
                continue
            run = step.get("run")
            if run is None:
                continue
            shell = base._effective_entry(step, job_defaults, workflow_defaults, "shell")
            if shell is not None and not _supported_shell(shell[1][4]):
                continue
            working_directory = base._effective_entry(
                step, job_defaults, workflow_defaults, "working-directory"
            )
            if not base._repo_root_working_directory(working_directory):
                continue
            if run[0] in ranges:
                end, style = ranges[run[0]]
                scripts.append(legacy.scalar_text(lines, run[0], end, style))
            elif (value := legacy.inline_scalar(run[1][4])) is not None:
                scripts.append(value)
    return scripts


def _terminates(parts: list[str]) -> bool:
    if not parts:
        return False
    if parts[0] in _TERMINATORS:
        return True
    return parts[0] in _SHELL_WRAPPERS and any(
        token in _TERMINATORS for token in parts[1:]
    )


def shell_commands(text: str) -> list[str]:
    """Reject control flow and direct or wrapper-invoked terminators."""
    stripped = "\n".join(legacy.strip_comment(line) for line in text.splitlines())
    try:
        lexer = shlex.shlex(stripped, posix=True, punctuation_chars=";&|(){}")
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        return []
    if any(token in _CONTROL or token in legacy.CONTROL_WORDS for token in tokens):
        return []

    commands: list[str] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        first = legacy.strip_comment(lines[index]).strip()
        if not first:
            index += 1
            continue
        parts = [first]
        while parts[-1].rstrip().endswith("\\") and index + 1 < len(lines):
            parts[-1] = parts[-1].rstrip()[:-1]
            index += 1
            continuation = legacy.strip_comment(lines[index]).strip()
            if continuation:
                parts.append(continuation)
        command = " ".join(parts)
        try:
            parsed = shlex.split(command)
        except ValueError:
            return []
        if parsed and (
            legacy.ENV_ASSIGNMENT.fullmatch(parsed[0]) or _terminates(parsed)
        ):
            return []
        commands.append(command)
        index += 1
    return commands


def ci_discovery(
    discovery: Mapping[str, Any], workflow_texts: str | list[str]
) -> tuple[bool, list[str]]:
    """Apply the final extraction policy before matching configured tests."""
    text = "\n".join(workflow_texts) if isinstance(workflow_texts, list) else workflow_texts
    scripts = github_run_scripts(text)
    commands = [command for script in scripts for command in shell_commands(script)]
    strategy = discovery["strategy"]
    uses_pytest = strategy == "pytest_default_discovery" or any(
        str(pattern).endswith(".py") for pattern in discovery.get("contains_any", [])
    )
    if uses_pytest and (
        any(name.startswith("PYTEST_") for name in legacy.yaml_env_names(text))
        or any(
            re.search(
                r"\bPYTEST_[A-Za-z0-9_]*\b",
                "\n".join(legacy.strip_comment(line) for line in script.splitlines()),
            )
            for script in scripts
        )
    ):
        return False, []
    if strategy == "pytest_default_discovery":
        matched = any(
            base.pytest_command(command, str(discovery["test_path"]), False)
            for command in commands
        )
        return matched, [str(discovery["command"])] if matched else []
    if strategy == "mix_default_discovery":
        matched = any(
            base.mix_command(command, str(discovery["test_path"]))
            for command in commands
        )
        return matched, [str(discovery["command"])] if matched else []

    matches: list[str] = []
    for value in discovery["contains_any"]:
        pattern = str(value)
        if pattern.endswith(".py") and any(
            base.pytest_command(command, pattern, True) for command in commands
        ):
            matches.append(pattern)
        elif pattern.endswith(".exs") and any(
            base.mix_command(command, pattern, True) for command in commands
        ):
            matches.append(pattern)
        elif not pattern.endswith((".py", ".exs")):
            try:
                required = shlex.split(pattern)
            except ValueError:
                continue
            if any(
                (parts := base._tokens(command))
                and parts[: len(required)] == required
                for command in commands
            ):
                matches.append(pattern)
    return bool(matches), matches


pytest_command = base.pytest_command
mix_command = base.mix_command
__all__ = [
    "ci_discovery",
    "github_run_scripts",
    "shell_commands",
    "pytest_command",
    "mix_command",
]
