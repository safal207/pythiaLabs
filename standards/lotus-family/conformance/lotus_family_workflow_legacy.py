from __future__ import annotations

import fnmatch
import json
import re
import shlex
from pathlib import PurePosixPath
from typing import Any, Mapping

BARE_KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*\Z")
BLOCK_SCALAR = re.compile(r"([|>])(?:[1-9][+-]?|[+-][1-9]?)?\Z")
ENV_ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=.*\Z")
PYTEST_STARTS = (("python", "-m", "pytest"), ("pytest",))
SAFE_PYTEST_FLAGS = {"-q", "--quiet", "-v", "--verbose", "--strict-markers", "--strict-config", "--disable-warnings"}
SAFE_PYTEST_PREFIXES = ("--junitxml=", "--cov=", "--cov-report=", "--cov-fail-under=", "--color=", "--tb=", "--durations=", "--maxfail=")
FORBIDDEN_PYTEST_FLAGS = {"--collect-only", "--co", "--setup-only", "--pyargs", "-k", "--keyword", "-m", "--markers", "--deselect"}
SAFE_MIX_FLAGS = {"--trace", "--color"}
SAFE_MIX_PREFIXES = ("--seed=", "--max-failures=")
CONTROL_TOKENS = {"&&", "||", ";", "|", "&", "(", ")", "{", "}"}
CONTROL_WORDS = {"if", "then", "elif", "else", "fi", "for", "while", "until", "do", "done", "case", "esac", "select", "function"}
UNRESOLVED_ENV_MAPPING = "__LOTUS_UNRESOLVED_ENV_MAPPING__"
YAML_ANCHOR_ONLY = re.compile(r"&[A-Za-z_][A-Za-z0-9_-]*\Z")
YAML_ALIAS_ONLY = re.compile(r"\*[A-Za-z_][A-Za-z0-9_-]*\Z")
INLINE_ENV_KEY = re.compile(r"(?:^|[{,]\s*)['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?\s*:")


def strip_comment(line: str) -> str:
    single = double = escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
        elif char == "\\" and not single:
            escaped = True
        elif char == "'" and not double:
            single = not single
        elif char == '"' and not single:
            double = not double
        elif char == "#" and not single and not double:
            return line[:index]
    return line


def indent_of(line: str) -> int | None:
    prefix = line[: len(line) - len(line.lstrip(" \t"))]
    return None if "\t" in prefix else len(prefix)


def decode_key(text: str) -> str | None:
    key = text.strip()
    if BARE_KEY.fullmatch(key):
        return key
    if len(key) >= 2 and key[0] == key[-1] == "'":
        return key[1:-1].replace("''", "'") or None
    if len(key) >= 2 and key[0] == key[-1] == '"':
        try:
            decoded = json.loads(key)
        except json.JSONDecodeError:
            return None
        return decoded if isinstance(decoded, str) and decoded else None
    return None


def split_pair(text: str) -> tuple[str, str] | None:
    single = double = escaped = False
    for index, char in enumerate(text):
        if escaped:
            escaped = False
        elif char == "\\" and double:
            escaped = True
        elif char == "'" and not double:
            single = not single
        elif char == '"' and not single:
            double = not double
        elif char == ":" and not single and not double:
            return text[:index], text[index + 1 :]
    return None


def yaml_header(line: str) -> tuple[int, bool, int, str, str] | None:
    indent = indent_of(line)
    if indent is None:
        return None
    text = line[indent:]
    if not text or text.startswith("#"):
        return None
    is_list = False
    key_indent = indent
    if text.startswith("-"):
        match = re.match(r"-([ ]+)(.*)\Z", text)
        if not match:
            return None
        is_list = True
        key_indent = indent + 1 + len(match.group(1))
        text = match.group(2)
    pair = split_pair(text)
    if not pair:
        return None
    key = decode_key(pair[0])
    return None if key is None else (indent, is_list, key_indent, key, pair[1])


def scalar_indicator(value: str) -> str | None:
    match = BLOCK_SCALAR.fullmatch(strip_comment(value).strip())
    return match.group(1) if match else None


def inline_scalar(value: str) -> str | None:
    text = strip_comment(value).strip()
    if not text or text in {"null", "Null", "NULL", "~"}:
        return None
    if text.startswith("'"):
        return text[1:-1].replace("''", "'") if text.endswith("'") else None
    if text.startswith('"'):
        if not text.endswith('"'):
            return None
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return None
        return value if isinstance(value, str) else None
    return text


def condition_true(value: str) -> bool:
    scalar = inline_scalar(value)
    return scalar is not None and re.sub(r"\s+", " ", scalar.strip()).lower() in {"true", "${{ true }}"}


def scalar_ranges(lines: list[str]) -> dict[int, tuple[int, str]]:
    result: dict[int, tuple[int, str]] = {}
    index = 0
    while index < len(lines):
        header = yaml_header(lines[index])
        style = scalar_indicator(header[4]) if header else None
        if not header or not style:
            index += 1
            continue
        end = index + 1
        while end < len(lines):
            if not lines[end].strip():
                end += 1
                continue
            indent = indent_of(lines[end])
            if indent is None or indent <= header[2]:
                break
            end += 1
        result[index] = (end, style)
        index = end
    return result


def scalar_text(lines: list[str], start: int, end: int, style: str) -> str:
    body = lines[start + 1 : end]
    indents = [indent for line in body if line.strip() and (indent := indent_of(line)) is not None]
    if not indents:
        return ""
    minimum = min(indents)
    body = [line[minimum:] if line.strip() else "" for line in body]
    if style == "|":
        return "\n".join(body) + "\n"
    paragraphs: list[str] = []
    current: list[str] = []
    for line in body:
        if line:
            current.append(line)
        elif current:
            paragraphs.append(" ".join(current)); current = []
        elif paragraphs:
            paragraphs.append("")
    if current:
        paragraphs.append(" ".join(current))
    return "\n".join(paragraphs) + ("\n" if paragraphs else "")


def block_end(lines: list[str], start: int, parent_indent: int) -> int:
    index = start + 1
    while index < len(lines):
        if not lines[index].strip() or lines[index].lstrip().startswith("#"):
            index += 1; continue
        indent = indent_of(lines[index])
        if indent is None or indent <= parent_indent:
            break
        index += 1
    return index


def direct_headers(lines: list[str], start: int, end: int, parent_indent: int, scalar_body: set[int]):
    found = []
    minimum = None
    for row in range(start, end):
        if row in scalar_body:
            continue
        header = yaml_header(lines[row])
        if not header or header[1] or header[2] <= parent_indent:
            continue
        if minimum is None or header[2] < minimum:
            minimum, found = header[2], [(row, header)]
        elif header[2] == minimum:
            found.append((row, header))
    return found


def item_starts(lines: list[str], start: int, end: int, scalar_body: set[int]) -> list[int]:
    items: list[int] = []
    minimum = None
    for row in range(start, end):
        if row in scalar_body:
            continue
        indent = indent_of(lines[row])
        text = lines[row][indent:] if indent is not None else ""
        if indent is not None and text.startswith("-"):
            minimum = indent if minimum is None else minimum
            if indent == minimum:
                items.append(row)
    return items


def github_run_scripts(text: str) -> list[str]:
    lines = text.splitlines()
    ranges = scalar_ranges(lines)
    scalar_body = {row for start, (end, _) in ranges.items() for row in range(start + 1, end)}
    scripts: list[str] = []
    jobs = [(row, h) for row, line in enumerate(lines) if row not in scalar_body and (h := yaml_header(line)) and not h[1] and h[2] == 0 and h[3] == "jobs" and inline_scalar(h[4]) is None and scalar_indicator(h[4]) is None]
    for jobs_row, jobs_header in jobs:
        jobs_end = block_end(lines, jobs_row, jobs_header[2])
        job_headers = direct_headers(lines, jobs_row + 1, jobs_end, jobs_header[2], scalar_body)
        for ji, (job_row, job_header) in enumerate(job_headers):
            job_end = job_headers[ji + 1][0] if ji + 1 < len(job_headers) else jobs_end
            props = {h[3]: (row, h) for row, h in direct_headers(lines, job_row + 1, job_end, job_header[2], scalar_body)}
            runs_on = props.get("runs-on")
            if not runs_on or inline_scalar(runs_on[1][4]) is None:
                continue
            job_if = props.get("if")
            if job_if and not condition_true(job_if[1][4]):
                continue
            steps = props.get("steps")
            if not steps or inline_scalar(steps[1][4]) is not None or scalar_indicator(steps[1][4]) is not None:
                continue
            steps_end = block_end(lines, steps[0], steps[1][2])
            items = item_starts(lines, steps[0] + 1, steps_end, scalar_body)
            for si, item_row in enumerate(items):
                item_end = items[si + 1] if si + 1 < len(items) else steps_end
                first = yaml_header(lines[item_row])
                if not first or not first[1]:
                    continue
                props = {first[3]: (item_row, first)}
                for row in range(item_row + 1, item_end):
                    if row in scalar_body:
                        continue
                    header = yaml_header(lines[row])
                    if header and not header[1] and header[2] == first[2]:
                        props[header[3]] = (row, header)
                step_if = props.get("if")
                if step_if and not condition_true(step_if[1][4]):
                    continue
                run = props.get("run")
                if not run:
                    continue
                if run[0] in ranges:
                    end, style = ranges[run[0]]
                    scripts.append(scalar_text(lines, run[0], end, style))
                elif (value := inline_scalar(run[1][4])) is not None:
                    scripts.append(value)
    return scripts


def yaml_env_names(text: str) -> set[str]:
    lines = text.splitlines(); ranges = scalar_ranges(lines)
    body = {row for start, (end, _) in ranges.items() for row in range(start + 1, end)}
    names: set[str] = set()
    for index, line in enumerate(lines):
        if index in body:
            continue
        header = yaml_header(line)
        if not header or header[3] != "env":
            continue
        inline = strip_comment(header[4]).strip()
        if YAML_ALIAS_ONLY.fullmatch(inline):
            names.add(UNRESOLVED_ENV_MAPPING)
            continue
        if YAML_ANCHOR_ONLY.fullmatch(inline):
            inline = ""
        if inline:
            inline_names = set(INLINE_ENV_KEY.findall(inline))
            if not inline_names and inline != "{}":
                names.add(UNRESOLVED_ENV_MAPPING)
            names.update(inline_names)
            continue
        for row in range(index + 1, len(lines)):
            if row in body:
                continue
            if not lines[row].strip() or lines[row].lstrip().startswith("#"):
                continue
            indent = indent_of(lines[row])
            if indent is None or indent <= header[2]:
                break
            child = yaml_header(lines[row])
            if child and not child[1] and child[2] > header[2]:
                names.add(child[3])
    return names


def shell_commands(text: str) -> list[str]:
    stripped = "\n".join(strip_comment(line) for line in text.splitlines())
    try:
        lexer = shlex.shlex(stripped, posix=True, punctuation_chars=";&|(){}")
        lexer.whitespace_split = True; lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        return []
    if any(token in CONTROL_TOKENS or token in CONTROL_WORDS for token in tokens):
        return []
    lines = text.splitlines(); commands = []; index = 0
    while index < len(lines):
        first = strip_comment(lines[index]).strip()
        if not first:
            index += 1; continue
        parts = [first]
        while parts[-1].rstrip().endswith("\\") and index + 1 < len(lines):
            parts[-1] = parts[-1].rstrip()[:-1]; index += 1
            if continuation := strip_comment(lines[index]).strip():
                parts.append(continuation)
        commands.append(" ".join(parts)); index += 1
    return commands


def tokens(command: str) -> list[str] | None:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True; lexer.commenters = ""
        result = list(lexer)
    except ValueError:
        return None
    if not result or any(token in CONTROL_TOKENS for token in result) or ENV_ASSIGNMENT.fullmatch(result[0]):
        return None
    return result


def normalize(value: str) -> str:
    value = value.strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value.rstrip("/")


def ignore_covers(value: str, test_path: str, glob: bool = False) -> bool:
    value = normalize(value)
    if not value:
        return True
    test = PurePosixPath(test_path)
    if glob:
        candidates = [test.as_posix(), test.name] + [p.as_posix() for p in test.parents if p != PurePosixPath(".")]
        return any(fnmatch.fnmatchcase(candidate, value) for candidate in candidates)
    ignored = PurePosixPath(value)
    return ignored.is_absolute() or ".." in ignored.parts or ignored == test or ignored in test.parents


def pytest_safe(arguments: list[str], test_path: str, require_path: bool) -> bool:
    positive = []; index = 0
    while index < len(arguments):
        arg = arguments[index]
        if arg in FORBIDDEN_PYTEST_FLAGS or arg.startswith(("-k=", "--keyword=", "-m=", "--markers=", "--deselect=")):
            return False
        if arg.startswith("--ignore=") and ignore_covers(arg.split("=", 1)[1], test_path):
            return False
        if arg == "--ignore":
            if index + 1 >= len(arguments) or ignore_covers(arguments[index + 1], test_path):
                return False
            index += 1
        elif arg.startswith("--ignore-glob=") and ignore_covers(arg.split("=", 1)[1], test_path, True):
            return False
        elif arg == "--ignore-glob":
            if index + 1 >= len(arguments) or ignore_covers(arguments[index + 1], test_path, True):
                return False
            index += 1
        elif arg in SAFE_PYTEST_FLAGS or arg.startswith(SAFE_PYTEST_PREFIXES):
            pass
        elif arg.startswith("-"):
            return False
        else:
            positive.append(normalize(arg.split("::", 1)[0]))
        index += 1
    expected = normalize(test_path)
    return expected in positive if require_path else not positive


def pytest_command(command: str, test_path: str, require_path: bool) -> bool:
    parts = tokens(command)
    if not parts:
        return False
    for start in PYTEST_STARTS:
        if tuple(parts[: len(start)]) == start:
            return pytest_safe(parts[len(start):], test_path, require_path)
    return False


def mix_command(command: str, test_path: str, require_path: bool = False) -> bool:
    parts = tokens(command)
    if not parts or parts[:2] != ["mix", "test"]:
        return False
    positive = []
    for arg in parts[2:]:
        if arg in SAFE_MIX_FLAGS or arg.startswith(SAFE_MIX_PREFIXES):
            continue
        if arg.startswith("-"):
            return False
        positive.append(normalize(arg.split(":", 1)[0]))
    expected = normalize(test_path)
    return (expected in positive) if require_path else (not positive or positive == [expected])


def ci_discovery(discovery: Mapping[str, Any], workflow_texts: str | list[str]) -> tuple[bool, list[str]]:
    text = "\n".join(workflow_texts) if isinstance(workflow_texts, list) else workflow_texts
    scripts = github_run_scripts(text)
    commands = [command for script in scripts for command in shell_commands(script)]
    strategy = discovery["strategy"]
    uses_pytest = strategy == "pytest_default_discovery" or any(str(p).endswith(".py") for p in discovery.get("contains_any", []))
    if uses_pytest and (any(name.startswith("PYTEST_") for name in yaml_env_names(text)) or any(re.search(r"\bPYTEST_[A-Za-z0-9_]*\b", "\n".join(strip_comment(line) for line in script.splitlines())) for script in scripts)):
        return False, []
    if strategy == "pytest_default_discovery":
        matched = any(pytest_command(command, str(discovery["test_path"]), False) for command in commands)
        return matched, [str(discovery["command"])] if matched else []
    if strategy == "mix_default_discovery":
        matched = any(mix_command(command, str(discovery["test_path"])) for command in commands)
        return matched, [str(discovery["command"])] if matched else []
    matches = []
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
            if any((parts := tokens(command)) and parts[: len(required)] == required for command in commands):
                matches.append(pattern)
    return bool(matches), matches
