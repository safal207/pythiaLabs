"""Fail-closed GitHub Actions discovery for Lotus regression tests."""

from __future__ import annotations

import re
import shlex
from pathlib import PurePosixPath
from typing import Any, Mapping

import lotus_family_workflow_legacy as legacy

_CONTROL = legacy.CONTROL_TOKENS | {"(", ")", "{", "}"}
_CONTROL_WORDS = legacy.CONTROL_WORDS
_TERMINATORS = {"exit", "exec", "return", "break", "continue"}
_POSIX_SHELLS = {"bash", "sh"}
_REPO_ROOT_EXPRESSIONS = {"${{ github.workspace }}"}


def _condition(value: str) -> str | None:
    """Normalize a static GitHub Actions condition."""
    scalar = legacy.inline_scalar(value)
    if scalar is None:
        return None
    text = re.sub(r"\s+", " ", scalar.strip()).lower()
    if text.startswith("${{") and text.endswith("}}"):
        text = text[3:-2].strip()
    return text


def _supported_shell(value: str) -> bool:
    """Accept only explicit POSIX shells whose script placeholder is executable."""
    scalar = legacy.inline_scalar(value)
    if scalar is None:
        return False
    try:
        parts = shlex.split(scalar)
    except ValueError:
        return False
    if not parts or PurePosixPath(parts[0]).name not in _POSIX_SHELLS:
        return False
    return len(parts) == 1 or (
        parts[-1] == "{0}" and all(part.startswith("-") for part in parts[1:-1])
    )


def _parse_needs(value: str) -> list[str] | None:
    """Parse a static scalar or inline-list needs declaration."""
    scalar = legacy.inline_scalar(value)
    if scalar is None:
        return None
    text = scalar.strip()
    if text.startswith("[") and text.endswith("]"):
        body = text[1:-1].strip()
        if not body:
            return []
        values = [legacy.decode_key(item.strip()) for item in body.split(",")]
        return None if any(value is None for value in values) else [str(value) for value in values]
    key = legacy.decode_key(text)
    return [key] if key else None


def _properties(
    lines: list[str],
    start: int,
    end: int,
    parent_indent: int,
    scalar_body: set[int],
) -> dict[str, tuple[int, tuple[int, bool, int, str, str]]]:
    """Return direct mapping children keyed by their decoded YAML key."""
    return {
        header[3]: (row, header)
        for row, header in legacy.direct_headers(
            lines, start, end, parent_indent, scalar_body
        )
    }


def _mapping_children(
    lines: list[str],
    entry: tuple[int, tuple[int, bool, int, str, str]],
    scalar_body: set[int],
) -> dict[str, tuple[int, tuple[int, bool, int, str, str]]] | None:
    """Read direct children of a mapping entry, rejecting scalar substitutions."""
    row, header = entry
    if (
        legacy.inline_scalar(header[4]) is not None
        or legacy.scalar_indicator(header[4]) is not None
    ):
        return None
    end = legacy.block_end(lines, row, header[2])
    return _properties(lines, row + 1, end, header[2], scalar_body)


def _run_defaults(
    lines: list[str],
    properties: dict[str, tuple[int, tuple[int, bool, int, str, str]]],
    scalar_body: set[int],
) -> dict[str, tuple[int, tuple[int, bool, int, str, str]]] | None:
    """Resolve the static defaults.run mapping for one workflow or job scope."""
    defaults = properties.get("defaults")
    if defaults is None:
        return {}
    default_properties = _mapping_children(lines, defaults, scalar_body)
    if default_properties is None:
        return None
    run = default_properties.get("run")
    if run is None:
        return {}
    return _mapping_children(lines, run, scalar_body)


def _effective_entry(
    step_properties: dict[str, tuple[int, tuple[int, bool, int, str, str]]],
    job_defaults: dict[str, tuple[int, tuple[int, bool, int, str, str]]],
    workflow_defaults: dict[str, tuple[int, tuple[int, bool, int, str, str]]],
    key: str,
) -> tuple[int, tuple[int, bool, int, str, str]] | None:
    """Apply step → job defaults.run → workflow defaults.run inheritance."""
    if key in step_properties:
        return step_properties[key]
    if key in job_defaults:
        return job_defaults[key]
    return workflow_defaults.get(key)


def _repo_root_working_directory(
    entry: tuple[int, tuple[int, bool, int, str, str]] | None,
) -> bool:
    """Prove that a run step executes at repository root.

    Non-root or dynamic working directories are rejected because relative pytest
    and Mix paths would otherwise refer to a different test scope.
    """
    if entry is None:
        return True
    scalar = legacy.inline_scalar(entry[1][4])
    if scalar is None:
        return False
    text = scalar.strip().replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text in {"", "."} or scalar.strip() in _REPO_ROOT_EXPRESSIONS


def github_run_scripts(text: str) -> list[str]:
    """Extract only provably executable, repo-root POSIX run scripts."""
    lines = text.splitlines()
    ranges = legacy.scalar_ranges(lines)
    scalar_body = {
        row
        for start, (end, _) in ranges.items()
        for row in range(start + 1, end)
    }
    top = _properties(lines, 0, len(lines), -1, scalar_body)
    jobs = top.get("jobs")
    if jobs is None:
        return []
    workflow_defaults = _run_defaults(lines, top, scalar_body)
    if workflow_defaults is None:
        return []
    jobs_children = _mapping_children(lines, jobs, scalar_body)
    if jobs_children is None:
        return []

    job_entries = list(jobs_children.values())
    job_names = set(jobs_children)
    scripts: list[str] = []

    for job_row, job_header in job_entries:
        job_end = legacy.block_end(lines, job_row, job_header[2])
        job_properties = _properties(
            lines, job_row + 1, job_end, job_header[2], scalar_body
        )
        runs_on = job_properties.get("runs-on")
        if runs_on is None or legacy.inline_scalar(runs_on[1][4]) is None:
            continue

        needs = job_properties.get("needs")
        if needs is not None:
            dependencies = _parse_needs(needs[1][4])
            if (
                dependencies is None
                or not dependencies
                or any(dependency not in job_names for dependency in dependencies)
            ):
                continue
            job_if = job_properties.get("if")
            if job_if is None or _condition(job_if[1][4]) != "always()":
                continue
        else:
            job_if = job_properties.get("if")
            if job_if is not None and _condition(job_if[1][4]) != "true":
                continue

        job_defaults = _run_defaults(lines, job_properties, scalar_body)
        if job_defaults is None:
            continue

        steps = job_properties.get("steps")
        if steps is None:
            continue
        if (
            legacy.inline_scalar(steps[1][4]) is not None
            or legacy.scalar_indicator(steps[1][4]) is not None
        ):
            continue
        steps_end = legacy.block_end(lines, steps[0], steps[1][2])
        items = legacy.item_starts(lines, steps[0] + 1, steps_end, scalar_body)

        for step_index, item_row in enumerate(items):
            item_end = items[step_index + 1] if step_index + 1 < len(items) else steps_end
            first = legacy.yaml_header(lines[item_row])
            if first is None or not first[1]:
                continue
            step_properties = {first[3]: (item_row, first)}
            for row in range(item_row + 1, item_end):
                if row in scalar_body:
                    continue
                header = legacy.yaml_header(lines[row])
                if header is not None and not header[1] and header[2] == first[2]:
                    step_properties[header[3]] = (row, header)

            step_if = step_properties.get("if")
            if step_if is not None and _condition(step_if[1][4]) != "true":
                continue

            run = step_properties.get("run")
            if run is None:
                continue

            shell = _effective_entry(
                step_properties, job_defaults, workflow_defaults, "shell"
            )
            if shell is not None and not _supported_shell(shell[1][4]):
                continue

            working_directory = _effective_entry(
                step_properties,
                job_defaults,
                workflow_defaults,
                "working-directory",
            )
            if not _repo_root_working_directory(working_directory):
                continue

            if run[0] in ranges:
                end, style = ranges[run[0]]
                scripts.append(legacy.scalar_text(lines, run[0], end, style))
            elif (value := legacy.inline_scalar(run[1][4])) is not None:
                scripts.append(value)
    return scripts


def shell_commands(text: str) -> list[str]:
    """Split straight-line scripts and reject control flow or terminators."""
    stripped = "\n".join(legacy.strip_comment(line) for line in text.splitlines())
    try:
        lexer = shlex.shlex(stripped, posix=True, punctuation_chars=";&|(){}")
        lexer.whitespace_split = True
        lexer.commenters = ""
        script_tokens = list(lexer)
    except ValueError:
        return []
    if any(token in _CONTROL or token in _CONTROL_WORDS for token in script_tokens):
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
            legacy.ENV_ASSIGNMENT.fullmatch(parsed[0])
            or parsed[0] in _TERMINATORS
        ):
            return []
        commands.append(command)
        index += 1
    return commands


def _tokens(command: str) -> list[str] | None:
    """Tokenize one direct command under the fail-closed shell policy."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        lexer.commenters = ""
        result = list(lexer)
    except ValueError:
        return None
    if (
        not result
        or any(token in _CONTROL for token in result)
        or legacy.ENV_ASSIGNMENT.fullmatch(result[0])
        or result[0] in _TERMINATORS
    ):
        return None
    return result


def pytest_command(command: str, test_path: str, require_path: bool) -> bool:
    """Validate full pytest discovery or an explicit full-file selection."""
    parts = _tokens(command)
    if not parts:
        return False
    for start in legacy.PYTEST_STARTS:
        if tuple(parts[: len(start)]) == start:
            arguments = parts[len(start) :]
            if any("::" in argument for argument in arguments if not argument.startswith("-")):
                return False
            return legacy.pytest_safe(arguments, test_path, require_path)
    return False


def mix_command(command: str, test_path: str, require_path: bool = False) -> bool:
    """Validate Mix discovery while rejecting file-line subsets."""
    parts = _tokens(command)
    if not parts or parts[:2] != ["mix", "test"]:
        return False
    positive: list[str] = []
    for argument in parts[2:]:
        if argument in legacy.SAFE_MIX_FLAGS or argument.startswith(
            legacy.SAFE_MIX_PREFIXES
        ):
            continue
        if argument.startswith("-") or ":" in argument:
            return False
        positive.append(legacy.normalize(argument))
    expected = legacy.normalize(test_path)
    return expected in positive if require_path else (
        not positive or positive == [expected]
    )


def ci_discovery(
    discovery: Mapping[str, Any], workflow_texts: str | list[str]
) -> tuple[bool, list[str]]:
    """Match configured Lotus tests only inside hardened executable contexts."""
    text = "\n".join(workflow_texts) if isinstance(workflow_texts, list) else workflow_texts
    scripts = github_run_scripts(text)
    commands = [
        command for script in scripts for command in shell_commands(script)
    ]
    strategy = discovery["strategy"]
    uses_pytest = strategy == "pytest_default_discovery" or any(
        str(pattern).endswith(".py")
        for pattern in discovery.get("contains_any", [])
    )
    if uses_pytest and (
        any(name.startswith("PYTEST_") for name in legacy.yaml_env_names(text))
        or any(
            re.search(
                r"\bPYTEST_[A-Za-z0-9_]*\b",
                "\n".join(
                    legacy.strip_comment(line) for line in script.splitlines()
                ),
            )
            for script in scripts
        )
    ):
        return False, []

    if strategy == "pytest_default_discovery":
        matched = any(
            pytest_command(command, str(discovery["test_path"]), False)
            for command in commands
        )
        return matched, [str(discovery["command"])] if matched else []
    if strategy == "mix_default_discovery":
        matched = any(
            mix_command(command, str(discovery["test_path"]))
            for command in commands
        )
        return matched, [str(discovery["command"])] if matched else []

    matches: list[str] = []
    for value in discovery["contains_any"]:
        pattern = str(value)
        if pattern.endswith(".py") and any(
            pytest_command(command, pattern, True) for command in commands
        ):
            matches.append(pattern)
        elif pattern.endswith(".exs") and any(
            mix_command(command, pattern, True) for command in commands
        ):
            matches.append(pattern)
        elif not pattern.endswith((".py", ".exs")):
            try:
                required = shlex.split(pattern)
            except ValueError:
                continue
            if any(
                (parts := _tokens(command))
                and parts[: len(required)] == required
                for command in commands
            ):
                matches.append(pattern)
    return bool(matches), matches


for _name in dir(legacy):
    if not _name.startswith("_") and _name not in globals():
        globals()[_name] = getattr(legacy, _name)
