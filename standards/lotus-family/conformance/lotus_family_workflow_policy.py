"""Final fail-closed execution policy for Lotus GitHub Actions discovery."""

from __future__ import annotations

import re
import shlex
from typing import Any, Mapping

import lotus_family_workflow_hardened as base
import lotus_family_workflow_legacy as legacy

_POSIX_SHELLS = {"bash", "sh"}
_SHELL_WRAPPERS = {"command", "builtin"}
_TERMINATORS = {"exit", "exec", "return", "break", "continue"}
_DIRECTORY_MUTATORS = {"cd", "pushd", "popd", "source", "."}
_CONTROL = legacy.CONTROL_TOKENS | {"(", ")", "{", "}"}


def _supported_shell(value: str) -> bool:
    """Accept only exact shell forms that provably execute the generated script."""
    scalar = legacy.inline_scalar(value)
    if scalar is None:
        return False
    try:
        parts = shlex.split(scalar)
    except ValueError:
        return False
    if not parts or parts[0] not in _POSIX_SHELLS:
        return False
    if len(parts) == 1:
        return True
    allowed = {
        ("bash", "-e", "{0}"),
        ("bash", "--noprofile", "--norc", "-e", "-o", "pipefail", "{0}"),
        ("sh", "-e", "{0}"),
    }
    return tuple(parts) in allowed


def _default_shell_is_posix(runs_on_value: str) -> bool:
    """Accept an implicit shell only when the literal runner is POSIX-based."""
    scalar = legacy.inline_scalar(runs_on_value)
    if scalar is None or "${{" in scalar:
        return False
    normalized = scalar.lower()
    if "windows" in normalized:
        return False
    return any(label in normalized for label in ("ubuntu", "macos", "linux"))


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


def _boolean_entry(
    entry: tuple[int, tuple[int, bool, int, str, str]] | None,
    *,
    default: bool,
) -> bool | None:
    """Resolve a literal GitHub Actions boolean and preserve unknown expressions."""
    if entry is None:
        return default
    condition = base._condition(entry[1][4])
    if condition == "true":
        return True
    if condition == "false":
        return False
    return None


def _github_run_step_groups(text: str) -> list[list[tuple[str, bool | None]]]:
    """Extract ordered run-step groups from provably runnable jobs."""
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

    groups: list[list[tuple[str, bool | None]]] = []
    for job_name, (_, _, job_end, properties) in records.items():
        runs_on = properties.get("runs-on")
        if runs_on is None or legacy.inline_scalar(runs_on[1][4]) is None:
            continue
        job_continue_on_error = _boolean_entry(
            properties.get("continue-on-error"), default=False
        )
        if job_continue_on_error is not False:
            continue
        needs = properties.get("needs")
        dependencies = dependency_graph[job_name]
        if not _dependencies_proven(job_name, dependency_graph):
            continue
        job_if = properties.get("if")
        if needs is not None:
            if (
                not dependencies
                or job_if is None
                or base._condition(job_if[1][4]) != "always()"
            ):
                continue
        elif job_if is not None and base._condition(job_if[1][4]) != "true":
            continue

        job_defaults = base._run_defaults(lines, properties, scalar_body)
        steps = properties.get("steps")
        if job_defaults is None or steps is None:
            continue
        if (
            legacy.inline_scalar(steps[1][4]) is not None
            or legacy.scalar_indicator(steps[1][4]) is not None
        ):
            continue
        steps_end = legacy.block_end(lines, steps[0], steps[1][2])
        items = legacy.item_starts(lines, steps[0] + 1, steps_end, scalar_body)

        group: list[tuple[str, bool | None]] = []
        blocked = False
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
                if (
                    header is not None
                    and not header[1]
                    and header[2] == first[2]
                ):
                    step[header[3]] = (row, header)

            step_if = _boolean_entry(step.get("if"), default=True)
            if step_if is False:
                continue
            if step_if is not True:
                blocked = True
                break

            run = step.get("run")
            if run is None:
                continue
            if "uses" in step:
                blocked = True
                break
            shell = base._effective_entry(
                step, job_defaults, workflow_defaults, "shell"
            )
            if shell is None:
                if not _default_shell_is_posix(runs_on[1][4]):
                    blocked = True
                    break
            elif not _supported_shell(shell[1][4]):
                blocked = True
                break
            working_directory = base._effective_entry(
                step, job_defaults, workflow_defaults, "working-directory"
            )
            if not base._repo_root_working_directory(working_directory):
                blocked = True
                break

            continue_on_error = _boolean_entry(
                step.get("continue-on-error"), default=False
            )
            if run[0] in ranges:
                end, style = ranges[run[0]]
                script = legacy.scalar_text(lines, run[0], end, style)
            else:
                script = legacy.inline_scalar(run[1][4])
                if script is None:
                    blocked = True
                    break
            group.append((script, continue_on_error))

        if group and not blocked:
            groups.append(group)
    return groups


def github_run_scripts(text: str) -> list[str]:
    """Return extracted scripts while preserving the public compatibility API."""
    return [
        script
        for group in _github_run_step_groups(text)
        for script, _ in group
    ]


def _unsafe_state_change(parts: list[str]) -> bool:
    """Reject commands that can end execution or change later command meaning."""
    if not parts:
        return False
    command = parts[0]
    if command == "eval":
        return True
    if command in _TERMINATORS or command in _DIRECTORY_MUTATORS:
        return True
    if command in _SHELL_WRAPPERS and len(parts) > 1:
        wrapped = parts[1]
        return (
            wrapped == "eval"
            or wrapped in _TERMINATORS
            or wrapped in _DIRECTORY_MUTATORS
        )
    return False


def _safe_prelude(parts: list[str]) -> bool:
    """Return true only for shell setup commands that cannot hide a test."""
    return parts in (
        ["set", "-e"],
        ["set", "-eu"],
        ["set", "-euo", "pipefail"],
        ["set", "-o", "pipefail"],
        [":"],
    )


def _analyze_script(text: str) -> tuple[str, str | None]:
    """Classify a script as invalid, prelude-only, or one reachable command."""
    stripped = "\n".join(
        legacy.strip_comment(line) for line in text.splitlines()
    )
    if "<<" in stripped:
        return "invalid", None
    try:
        lexer = shlex.shlex(
            stripped, posix=True, punctuation_chars=";&|(){}"
        )
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        return "invalid", None
    if any(
        token in _CONTROL or token in legacy.CONTROL_WORDS
        for token in tokens
    ):
        return "invalid", None

    lines = text.splitlines()
    index = 0
    saw_prelude = False
    while index < len(lines):
        first = legacy.strip_comment(lines[index]).strip()
        if not first:
            index += 1
            continue
        parts = [first]
        while (
            parts[-1].rstrip().endswith("\\")
            and index + 1 < len(lines)
        ):
            parts[-1] = parts[-1].rstrip()[:-1]
            index += 1
            continuation = legacy.strip_comment(lines[index]).strip()
            if continuation:
                parts.append(continuation)
        command = " ".join(parts)
        try:
            parsed = shlex.split(command)
        except ValueError:
            return "invalid", None
        if parsed and (
            legacy.ENV_ASSIGNMENT.fullmatch(parsed[0])
            or _unsafe_state_change(parsed)
        ):
            return "invalid", None
        if parsed and _safe_prelude(parsed):
            saw_prelude = True
            index += 1
            continue
        return ("command", command) if parsed else ("invalid", None)
    return ("prelude", None) if saw_prelude else ("empty", None)


def shell_commands(text: str) -> list[str]:
    """Return only a first provably reachable substantive command."""
    kind, command = _analyze_script(text)
    return [command] if kind == "command" and command is not None else []


def _command_matches(
    discovery: Mapping[str, Any], command: str
) -> list[str]:
    """Return configured patterns satisfied by one executable command."""
    strategy = discovery["strategy"]
    if strategy == "pytest_default_discovery":
        if base.pytest_command(
            command, str(discovery["test_path"]), False
        ):
            return [str(discovery["command"])]
        return []
    if strategy == "mix_default_discovery":
        if base.mix_command(command, str(discovery["test_path"])):
            return [str(discovery["command"])]
        return []

    matches: list[str] = []
    for value in discovery["contains_any"]:
        pattern = str(value)
        if pattern.endswith(".py") and base.pytest_command(
            command, pattern, True
        ):
            matches.append(pattern)
        elif pattern.endswith(".exs") and base.mix_command(
            command, pattern, True
        ):
            matches.append(pattern)
        elif not pattern.endswith((".py", ".exs")):
            try:
                required = shlex.split(pattern)
            except ValueError:
                continue
            parts = base._tokens(command)
            if parts and parts[: len(required)] == required:
                matches.append(pattern)
    return matches


def _ci_discovery_one(
    discovery: Mapping[str, Any], workflow_text: str
) -> tuple[bool, list[str]]:
    """Evaluate one workflow document without cross-file state leakage."""
    groups = _github_run_step_groups(workflow_text)
    scripts = [
        script for group in groups for script, _ in group
    ]
    strategy = discovery["strategy"]
    uses_pytest = strategy == "pytest_default_discovery" or any(
        str(pattern).endswith(".py")
        for pattern in discovery.get("contains_any", [])
    )
    if uses_pytest and (
        any(
            name.startswith("PYTEST_")
            for name in legacy.yaml_env_names(workflow_text)
        )
        or any(
            re.search(
                r"\bPYTEST_[A-Za-z0-9_]*\b",
                "\n".join(
                    legacy.strip_comment(line)
                    for line in script.splitlines()
                ),
            )
            for script in scripts
        )
    ):
        return False, []

    matches: list[str] = []
    for group in groups:
        for script, continue_on_error in group:
            kind, command = _analyze_script(script)
            if kind == "invalid":
                break
            if kind in {"empty", "prelude"}:
                continue
            if command is None:
                break

            current = _command_matches(discovery, command)
            if current and continue_on_error is False:
                for pattern in current:
                    if pattern not in matches:
                        matches.append(pattern)
                break

            if continue_on_error is True:
                continue
            # Unknown or disabled failure propagation means a later run step
            # is not provably reachable under GitHub's fail-fast semantics.
            break
    return bool(matches), matches


def ci_discovery(
    discovery: Mapping[str, Any], workflow_texts: str | list[str]
) -> tuple[bool, list[str]]:
    """Evaluate workflow documents independently and union safe matches."""
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


pytest_command = base.pytest_command
mix_command = base.mix_command
__all__ = [
    "ci_discovery",
    "github_run_scripts",
    "shell_commands",
    "pytest_command",
    "mix_command",
]
