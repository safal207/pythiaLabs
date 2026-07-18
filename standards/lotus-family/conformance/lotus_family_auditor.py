from __future__ import annotations

import json
import re
import shlex
from typing import Any, Mapping

import lotus_family_auditor_core as _core
from lotus_family_auditor_core import *  # noqa: F403

_YAML_KEY = re.compile(r"([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)\Z")
_BLOCK_SCALAR = re.compile(r"([|>])(?:[1-9][+-]?|[+-][1-9]?)?\Z")
_ENV_ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=.*\Z")
_SHELL_CONTROL = {"&&", "||", ";", "|", "&"}


def _strip_unquoted_comment(line: str) -> str:
    in_single = False
    in_double = False
    escaped = False
    for index, character in enumerate(line):
        if escaped:
            escaped = False
            continue
        if character == "\\" and not in_single:
            escaped = True
            continue
        if character == "'" and not in_double:
            in_single = not in_single
            continue
        if character == '"' and not in_single:
            in_double = not in_double
            continue
        if character == "#" and not in_single and not in_double:
            return line[:index]
    return line


def _indent_of(line: str) -> int | None:
    prefix = line[: len(line) - len(line.lstrip(" \t"))]
    if "\t" in prefix:
        return None
    return len(prefix)


def _yaml_header(line: str) -> tuple[int, bool, int, str, str] | None:
    indent = _indent_of(line)
    if indent is None:
        return None
    stripped = line[indent:]
    if not stripped or stripped.startswith("#"):
        return None

    is_list = False
    key_indent = indent
    if stripped.startswith("-"):
        match = re.match(r"-([ ]+)(.*)\Z", stripped)
        if match is None:
            return None
        is_list = True
        key_indent = indent + 1 + len(match.group(1))
        stripped = match.group(2)
    match = _YAML_KEY.fullmatch(stripped)
    if match is None:
        return None
    return indent, is_list, key_indent, match.group(1), match.group(2)


def _scalar_indicator(value: str) -> str | None:
    normalized = _strip_unquoted_comment(value).strip()
    match = _BLOCK_SCALAR.fullmatch(normalized)
    return match.group(1) if match is not None else None


def _block_scalar_end(lines: list[str], start: int, key_indent: int) -> int:
    index = start + 1
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        indent = _indent_of(line)
        if indent is None or indent <= key_indent:
            break
        index += 1
    return index


def _block_scalar_text(
    lines: list[str], start: int, end: int, style: str
) -> str:
    body = lines[start + 1 : end]
    indents = [
        indent
        for line in body
        if line.strip() and (indent := _indent_of(line)) is not None
    ]
    if not indents:
        return ""
    content_indent = min(indents)
    deindented = [line[content_indent:] if line.strip() else "" for line in body]
    if style == "|":
        return "\n".join(deindented) + "\n"

    paragraphs: list[str] = []
    current: list[str] = []
    for line in deindented:
        if line:
            current.append(line)
        elif current:
            paragraphs.append(" ".join(current))
            current = []
        elif paragraphs:
            paragraphs.append("")
    if current:
        paragraphs.append(" ".join(current))
    return "\n".join(paragraphs) + ("\n" if paragraphs else "")


def _inline_yaml_scalar(value: str) -> str | None:
    text = _strip_unquoted_comment(value).strip()
    if not text or text in {"null", "Null", "NULL", "~"}:
        return None
    if text.startswith("'"):
        if len(text) < 2 or not text.endswith("'"):
            return None
        return text[1:-1].replace("''", "'")
    if text.startswith('"'):
        if len(text) < 2 or not text.endswith('"'):
            return None
        try:
            decoded = json.loads(text)
        except json.JSONDecodeError:
            return None
        return decoded if isinstance(decoded, str) else None
    return text


def _scalar_ranges(lines: list[str]) -> dict[int, tuple[int, str]]:
    ranges: dict[int, tuple[int, str]] = {}
    index = 0
    while index < len(lines):
        header = _yaml_header(lines[index])
        if header is None:
            index += 1
            continue
        style = _scalar_indicator(header[4])
        if style is None:
            index += 1
            continue
        end = _block_scalar_end(lines, index, header[2])
        ranges[index] = (end, style)
        index = end
    return ranges


def _github_actions_run_scripts(text: str) -> list[str]:
    lines = text.splitlines()
    scalar_ranges = _scalar_ranges(lines)
    scalar_body_lines = {
        line_index
        for start, (end, _) in scalar_ranges.items()
        for line_index in range(start + 1, end)
    }
    scripts: list[str] = []
    index = 0

    while index < len(lines):
        if index in scalar_body_lines:
            index += 1
            continue
        header = _yaml_header(lines[index])
        if (
            header is None
            or header[3] != "steps"
            or _inline_yaml_scalar(header[4]) is not None
        ):
            index += 1
            continue

        steps_indent = header[2]
        block_end = index + 1
        while block_end < len(lines):
            line = lines[block_end]
            if not line.strip() or line.lstrip().startswith("#"):
                block_end += 1
                continue
            indent = _indent_of(line)
            if indent is None or indent <= steps_indent:
                break
            block_end += 1

        item_indices: list[int] = []
        item_indent: int | None = None
        for cursor in range(index + 1, block_end):
            if cursor in scalar_body_lines:
                continue
            indent = _indent_of(lines[cursor])
            stripped = lines[cursor][indent:] if indent is not None else ""
            if indent is not None and stripped.startswith("-"):
                if item_indent is None:
                    item_indent = indent
                if indent == item_indent:
                    item_indices.append(cursor)

        for position, item_start in enumerate(item_indices):
            item_end = (
                item_indices[position + 1]
                if position + 1 < len(item_indices)
                else block_end
            )
            item_header = _yaml_header(lines[item_start])
            if item_header is not None and item_header[1]:
                direct_indent = item_header[2]
            else:
                candidates = [
                    candidate[2]
                    for row in range(item_start + 1, item_end)
                    if row not in scalar_body_lines
                    and (candidate := _yaml_header(lines[row])) is not None
                    and not candidate[1]
                ]
                if not candidates:
                    continue
                direct_indent = min(candidates)

            for row in range(item_start, item_end):
                if row in scalar_body_lines:
                    continue
                row_header = _yaml_header(lines[row])
                if row_header is None:
                    continue
                _, is_list, key_indent, key, value = row_header
                if key != "run" or key_indent != direct_indent:
                    continue
                if row != item_start and is_list:
                    continue
                scalar = scalar_ranges.get(row)
                if scalar is not None:
                    end, style = scalar
                    scripts.append(_block_scalar_text(lines, row, end, style))
                else:
                    inline = _inline_yaml_scalar(value)
                    if inline is not None:
                        scripts.append(inline)
                break
        index = block_end
    return scripts


def _yaml_env_names(text: str) -> set[str]:
    lines = text.splitlines()
    scalar_ranges = _scalar_ranges(lines)
    scalar_body_lines = {
        line_index
        for start, (end, _) in scalar_ranges.items()
        for line_index in range(start + 1, end)
    }
    names: set[str] = set()
    for index, line in enumerate(lines):
        if index in scalar_body_lines:
            continue
        header = _yaml_header(line)
        if header is None or header[3] != "env":
            continue
        env_indent = header[2]
        inline = _strip_unquoted_comment(header[4]).strip()
        if inline:
            names.update(re.findall(r"\bPYTEST_[A-Za-z0-9_]*\b", inline))
            continue
        for cursor in range(index + 1, len(lines)):
            if cursor in scalar_body_lines:
                continue
            candidate = lines[cursor]
            if not candidate.strip() or candidate.lstrip().startswith("#"):
                continue
            candidate_indent = _indent_of(candidate)
            if candidate_indent is None or candidate_indent <= env_indent:
                break
            child = _yaml_header(candidate)
            if child is not None and not child[1] and child[2] > env_indent:
                names.add(child[3])
    return names


def _has_forbidden_pytest_environment(text: str, scripts: list[str]) -> bool:
    if any(name.startswith("PYTEST_") for name in _yaml_env_names(text)):
        return True
    for script in scripts:
        executable = "\n".join(
            _strip_unquoted_comment(line) for line in script.splitlines()
        )
        if re.search(r"\bPYTEST_[A-Za-z0-9_]*\b", executable):
            return True
    return False


def _tokenize_executed_command(command: str) -> list[str] | None:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        return None
    if not tokens or any(token in _SHELL_CONTROL for token in tokens):
        return None
    if _ENV_ASSIGNMENT.fullmatch(tokens[0]):
        return None
    return tokens


def _ci_discovery(
    discovery: Mapping[str, Any], workflow_text: str | list[str]
) -> tuple[bool, list[str]]:
    if isinstance(workflow_text, list):
        workflow_text = "\n".join(workflow_text)
    scripts = _github_actions_run_scripts(workflow_text)
    commands = [
        command for script in scripts for command in _core._shell_commands(script)
    ]
    strategy = discovery["strategy"]
    uses_pytest = strategy == "pytest_default_discovery" or any(
        str(pattern).endswith(".py") for pattern in discovery.get("contains_any", [])
    )
    if uses_pytest and _has_forbidden_pytest_environment(workflow_text, scripts):
        return False, []

    if strategy == "pytest_default_discovery":
        test_path = str(discovery["test_path"])
        matched = any(
            _core._is_pytest_default_discovery(command, test_path)
            for command in commands
        )
        return matched, [str(discovery["command"])] if matched else []

    matches: list[str] = []
    for pattern_value in discovery["contains_any"]:
        pattern = str(pattern_value)
        if pattern.endswith(".py"):
            if any(
                _core._is_explicit_pytest_test_command(command, pattern)
                for command in commands
            ):
                matches.append(pattern)
        elif any(_core._is_command_prefix(command, pattern) for command in commands):
            matches.append(pattern)
    return bool(matches), matches


_core._tokenize_executed_command = _tokenize_executed_command
_core._ci_discovery = _ci_discovery
if "--cov-fail-under=" not in _core._SAFE_PYTEST_PREFIXES:
    _core._SAFE_PYTEST_PREFIXES += ("--cov-fail-under=",)


if __name__ == "__main__":
    raise SystemExit(_core.main())
