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


def _condition(value: str) -> str | None:
    scalar = legacy.inline_scalar(value)
    if scalar is None:
        return None
    text = re.sub(r"\s+", " ", scalar.strip()).lower()
    if text.startswith("${{") and text.endswith("}}"):
        text = text[3:-2].strip()
    return text


def _supported_shell(value: str) -> bool:
    scalar = legacy.inline_scalar(value)
    if scalar is None:
        return False
    try:
        parts = shlex.split(scalar)
    except ValueError:
        return False
    if not parts or PurePosixPath(parts[0]).name not in _POSIX_SHELLS:
        return False
    return len(parts) == 1 or (parts[-1] == "{0}" and all(p.startswith("-") for p in parts[1:-1]))


def _parse_needs(value: str) -> list[str] | None:
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


def github_run_scripts(text: str) -> list[str]:
    lines = text.splitlines()
    ranges = legacy.scalar_ranges(lines)
    scalar_body = {
        row for start, (end, _) in ranges.items() for row in range(start + 1, end)
    }
    scripts: list[str] = []
    jobs = [
        (row, header)
        for row, line in enumerate(lines)
        if row not in scalar_body
        and (header := legacy.yaml_header(line))
        and not header[1]
        and header[2] == 0
        and header[3] == "jobs"
        and legacy.inline_scalar(header[4]) is None
        and legacy.scalar_indicator(header[4]) is None
    ]
    for jobs_row, jobs_header in jobs:
        jobs_end = legacy.block_end(lines, jobs_row, jobs_header[2])
        job_headers = legacy.direct_headers(lines, jobs_row + 1, jobs_end, jobs_header[2], scalar_body)
        job_names = {header[3] for _, header in job_headers}
        for index, (job_row, job_header) in enumerate(job_headers):
            job_end = job_headers[index + 1][0] if index + 1 < len(job_headers) else jobs_end
            props = {
                header[3]: (row, header)
                for row, header in legacy.direct_headers(lines, job_row + 1, job_end, job_header[2], scalar_body)
            }
            runs_on = props.get("runs-on")
            if not runs_on or legacy.inline_scalar(runs_on[1][4]) is None:
                continue
            needs = props.get("needs")
            if needs:
                dependencies = _parse_needs(needs[1][4])
                if dependencies is None or not dependencies or any(dep not in job_names for dep in dependencies):
                    continue
                job_if = props.get("if")
                if not job_if or _condition(job_if[1][4]) != "always()":
                    continue
            else:
                job_if = props.get("if")
                if job_if and _condition(job_if[1][4]) != "true":
                    continue
            steps = props.get("steps")
            if not steps or legacy.inline_scalar(steps[1][4]) is not None or legacy.scalar_indicator(steps[1][4]) is not None:
                continue
            steps_end = legacy.block_end(lines, steps[0], steps[1][2])
            items = legacy.item_starts(lines, steps[0] + 1, steps_end, scalar_body)
            for step_index, item_row in enumerate(items):
                item_end = items[step_index + 1] if step_index + 1 < len(items) else steps_end
                first = legacy.yaml_header(lines[item_row])
                if not first or not first[1]:
                    continue
                step_props = {first[3]: (item_row, first)}
                for row in range(item_row + 1, item_end):
                    if row in scalar_body:
                        continue
                    header = legacy.yaml_header(lines[row])
                    if header and not header[1] and header[2] == first[2]:
                        step_props[header[3]] = (row, header)
                step_if = step_props.get("if")
                if step_if and _condition(step_if[1][4]) != "true":
                    continue
                shell = step_props.get("shell")
                if shell and not _supported_shell(shell[1][4]):
                    continue
                run = step_props.get("run")
                if not run:
                    continue
                if run[0] in ranges:
                    end, style = ranges[run[0]]
                    scripts.append(legacy.scalar_text(lines, run[0], end, style))
                elif (value := legacy.inline_scalar(run[1][4])) is not None:
                    scripts.append(value)
    return scripts


def shell_commands(text: str) -> list[str]:
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
        if parsed and (legacy.ENV_ASSIGNMENT.fullmatch(parsed[0]) or parsed[0] in _TERMINATORS):
            return []
        commands.append(command)
        index += 1
    return commands


def _tokens(command: str) -> list[str] | None:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        lexer.commenters = ""
        result = list(lexer)
    except ValueError:
        return None
    if not result or any(token in _CONTROL for token in result) or legacy.ENV_ASSIGNMENT.fullmatch(result[0]) or result[0] in _TERMINATORS:
        return None
    return result


def pytest_command(command: str, test_path: str, require_path: bool) -> bool:
    parts = _tokens(command)
    if not parts:
        return False
    for start in legacy.PYTEST_STARTS:
        if tuple(parts[: len(start)]) == start:
            arguments = parts[len(start):]
            if any("::" in arg for arg in arguments if not arg.startswith("-")):
                return False
            return legacy.pytest_safe(arguments, test_path, require_path)
    return False


def mix_command(command: str, test_path: str, require_path: bool = False) -> bool:
    parts = _tokens(command)
    if not parts or parts[:2] != ["mix", "test"]:
        return False
    positive: list[str] = []
    for arg in parts[2:]:
        if arg in legacy.SAFE_MIX_FLAGS or arg.startswith(legacy.SAFE_MIX_PREFIXES):
            continue
        if arg.startswith("-") or ":" in arg:
            return False
        positive.append(legacy.normalize(arg))
    expected = legacy.normalize(test_path)
    return expected in positive if require_path else (not positive or positive == [expected])


def ci_discovery(discovery: Mapping[str, Any], workflow_texts: str | list[str]) -> tuple[bool, list[str]]:
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
        matched = any(pytest_command(command, str(discovery["test_path"]), False) for command in commands)
        return matched, [str(discovery["command"])] if matched else []
    if strategy == "mix_default_discovery":
        matched = any(mix_command(command, str(discovery["test_path"])) for command in commands)
        return matched, [str(discovery["command"])] if matched else []
    matches: list[str] = []
    for value in discovery["contains_any"]:
        pattern = str(value)
        if pattern.endswith(".py") and any(pytest_command(command, pattern, True) for command in commands):
            matches.append(pattern)
        elif pattern.endswith(".exs") and any(mix_command(command, pattern, True) for command in commands):
            matches.append(pattern)
        elif not pattern.endswith((".py", ".exs")):
            try:
                required = shlex.split(pattern)
            except ValueError:
                continue
            if any((parts := _tokens(command)) and parts[: len(required)] == required for command in commands):
                matches.append(pattern)
    return bool(matches), matches


for _name in dir(legacy):
    if not _name.startswith("_") and _name not in globals():
        globals()[_name] = getattr(legacy, _name)
