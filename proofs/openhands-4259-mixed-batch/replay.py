#!/usr/bin/env python3
"""Measure one native test's sensitivity to two controlled event-map mutations.

Requires git, uv, a prepared frozen native development environment and POSIX.
The input checkout's production and test bytes are restored even on a failed run.
This is a test-adequacy experiment, not evidence of a production defect.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET


HEAD = "4cc058275c5a08d845bd846576aafc80e5dd7d0d"
TEST = "tests/sdk/agent/test_security_analysis_event.py"
PRODUCTION = "openhands-sdk/openhands/sdk/agent/agent.py"
TARGET = "test_one_event_per_batch_keyed_by_action_id"
BASE_TEST_SHA = "7d9649a3135988545c77084f21dad4d957c80cdd67ece6aa3ca3c25a52605cda"
PATCHED_TEST_SHA = "d065099dcf1def8acbcd5294ad694826c285e11d4c09ad559cbff138eb0e5375"
PRODUCTION_SHA = "0fe8c703580ae6a6ae2dba97a0bc1966811950d224b4672a3d6af33001d30c92"
LOCK_SHA = "38e1d063a2d6580e6d23afbbcb64ddadb85feeab3a669486ddf3435cfe17d196"
PATCH_SHA = "95cd9f3f02183964ff8cabbd939f8d0d23c1c3c78bf2588cd63f61193d41efcf"
SUITE = [TEST, "tests/sdk/agent/test_async_secret_masking.py", "tests/sdk/security"]
CLASSNAME = "tests.sdk.agent.test_security_analysis_event"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def git(source: Path, *args: str, index: Path | None = None) -> bytes:
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    if index is not None:
        env["GIT_INDEX_FILE"] = str(index)
    return subprocess.check_output(["git", *args], cwd=source, env=env)


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def controlled_mutation(original: bytes, field: str) -> bytes:
    # Rotate only one emitted event map. The analyzer's list and policy return
    # remain unchanged; len == 1 is an identity mapping.
    require(field in {"risks", "details"}, "unknown mutation")
    if field == "risks":
        old = b"            risks={action.id: analysis.risk for action, analysis in analyses},\n"
        new = (
            b"            risks={\n"
            b"                action.id: analyses[(index + 1) % len(analyses)][1].risk\n"
            b"                for index, (action, _) in enumerate(analyses)\n"
            b"            },\n"
        )
    else:
        old = (
            b"            details={\n"
            b"                action.id: analysis.details\n"
            b"                for action, analysis in analyses\n"
            b"                if analysis.details is not None\n"
            b"            },\n"
        )
        new = (
            b"            details={\n"
            b"                action.id: analyses[(index + 1) % len(analyses)][1].details\n"
            b"                for index, (action, _) in enumerate(analyses)\n"
            b"                if analyses[(index + 1) % len(analyses)][1].details is not None\n"
            b"            },\n"
        )
    require(original.count(old) == 1, "mutation anchor must occur exactly once")
    return original.replace(old, new)


def run_logged(command: list[str], source: Path, env: dict[str, str], log: Path) -> int:
    with log.open("xb") as stream:
        process = subprocess.Popen(
            command,
            cwd=source,
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            return process.wait(timeout=180)
        except BaseException:
            # Stop the child process group before restoring files it may import.
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=5)
            except ProcessLookupError:
                pass
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            raise


def summarize_junit(path: Path) -> dict:
    counts = dict(collected=0, passed=0, failures=0, errors=0, skipped=0, xfailed=0)
    failures = []
    identities = []
    for case in ET.parse(path).findall(".//testcase"):
        counts["collected"] += 1
        identity = {"classname": case.get("classname"), "name": case.get("name")}
        identities.append(identity)
        failed, error, skipped = (
            case.find("failure"),
            case.find("error"),
            case.find("skipped"),
        )
        if failed is not None:
            counts["failures"] += 1
            message = failed.get("message", "")
            failures.append(
                {
                    **identity,
                    "message": message,
                    "assertion_failure": "AssertionError" in (failed.text or "")
                    or message.startswith("assert "),
                }
            )
        elif error is not None:
            counts["errors"] += 1
        elif skipped is not None:
            key = "xfailed" if skipped.get("type") == "pytest.xfail" else "skipped"
            counts[key] += 1
        else:
            counts["passed"] += 1
    return {"counts": counts, "failures": failures, "identities": identities}


def assert_result(result: dict, *, expected_failure: bool, broad: bool) -> None:
    expected = dict(
        collected=508 if broad else 11,
        passed=491 if broad else 10 if expected_failure else 11,
        failures=int(expected_failure),
        errors=0,
        skipped=7 if broad else 0,
        xfailed=10 if broad else 0,
    )
    require(result["counts"] == expected, f"unexpected counts: {result['counts']}")
    require(
        result["returncode"] == int(expected_failure), "unexpected pytest exit code"
    )
    if expected_failure:
        require(
            [(f["classname"], f["name"]) for f in result["failures"]]
            == [(CLASSNAME, TARGET)],
            "failure is not exactly the mixed-batch test",
        )
        require(
            result["failures"][0]["assertion_failure"], "failure is not an assertion"
        )
    if not broad:
        require(
            all(i["classname"] == CLASSNAME for i in result["identities"]),
            "unexpected target-file test identity",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument(
        "--output", type=Path, required=True, help="new evidence directory"
    )
    args = parser.parse_args()
    require(os.name == "posix", "POSIX required for controlled child-process cleanup")
    source, output = args.source.resolve(), args.output.resolve()
    require(
        not output.is_relative_to(source), "output must be outside the native checkout"
    )
    require(not output.exists(), "output must not already exist")
    require(
        git(source, "rev-parse", "HEAD").decode().strip() == HEAD, "wrong source HEAD"
    )
    require(
        git(source, "diff", "--cached", "--name-only") == b"",
        "staged changes are not allowed",
    )
    changed = git(source, "diff", "--name-only", "HEAD").decode().splitlines()
    require(set(changed) <= {TEST}, "only the supplied target test patch is allowed")
    require(
        not git(source, "ls-files", "--others", "--exclude-standard"),
        "untracked source files are not allowed",
    )
    for relative in [TEST, PRODUCTION, "uv.lock"]:
        path = source / relative
        require(
            not any(p.is_symlink() for p in [path, *path.parents] if p != source),
            f"symlinked source path: {relative}",
        )
    original = {
        name: (source / name).read_bytes() for name in [TEST, PRODUCTION, "uv.lock"]
    }
    require(
        sha(original[PRODUCTION]) == PRODUCTION_SHA,
        "production bytes differ from pinned source",
    )
    require(sha(original["uv.lock"]) == LOCK_SHA, "uv.lock differs from pinned source")
    require(
        sha(original[TEST]) in {BASE_TEST_SHA, PATCHED_TEST_SHA},
        "unknown target test bytes",
    )
    baseline = git(source, "show", f"{HEAD}:{TEST}")
    require(sha(baseline) == BASE_TEST_SHA, "baseline test identity mismatch")
    packet = Path(__file__).resolve().parent
    patch = packet / "mixed-batch.patch"
    require(sha(patch.read_bytes()) == PATCH_SHA, "native patch identity mismatch")
    uv = shutil.which("uv")
    require(
        uv is not None,
        "uv must be on PATH; prepare the pinned native dev environment first",
    )
    output.mkdir(parents=True)
    report = {
        "schema": "openhands-4259-mixed-batch-v1",
        "status": "INCOMPLETE",
        "claim": "Controlled test sensitivity only; no observed production defect.",
        "source_head": HEAD,
        "source": str(source),
        "output": str(output),
        "input_test_variant": "baseline"
        if sha(original[TEST]) == BASE_TEST_SHA
        else "strengthened",
        "final_suite_test_variant": "strengthened",
        "hashes": {
            "baseline_test": BASE_TEST_SHA,
            "strengthened_test": PATCHED_TEST_SHA,
            "production": PRODUCTION_SHA,
            "uv_lock": LOCK_SHA,
            "native_patch": PATCH_SHA,
            "driver": sha(Path(__file__).read_bytes()),
        },
        "uv_version": subprocess.check_output([uv, "--version"], text=True).strip(),
        "runs": [],
        "restoration": {},
    }
    env = os.environ.copy()
    for name in [
        "PYTHONPATH",
        "PYTHONHOME",
        "VIRTUAL_ENV",
        "PYTEST_ADDOPTS",
        "UV_PROJECT_ENVIRONMENT",
        "UV_NO_SYNC",
        "UV_NO_FROZEN",
    ]:
        env.pop(name, None)
    env.update(
        PYTHONNOUSERSITE="1",
        PYTHONDONTWRITEBYTECODE="1",
        OPENHANDS_SUPPRESS_BANNER="1",
        LITELLM_LOCAL_MODEL_COST_MAP="true",
    )
    report["environment_overrides"] = {
        name: env[name]
        for name in [
            "PYTHONNOUSERSITE",
            "PYTHONDONTWRITEBYTECODE",
            "OPENHANDS_SUPPRESS_BANNER",
            "LITELLM_LOCAL_MODEL_COST_MAP",
        ]
    }
    lock = Path(
        git(source, "rev-parse", "--git-path", "mixed-batch-proof.lock")
        .decode()
        .strip()
    )
    if not lock.is_absolute():
        lock = source / lock
    lock_owned = False
    exit_code = 1

    def terminate(_signum, _frame):
        raise InterruptedError("replay interrupted")

    prior_sigterm = signal.signal(signal.SIGTERM, terminate)
    try:
        with lock.open("x", encoding="utf-8") as stream:
            stream.write(str(os.getpid()) + "\n")
        lock_owned = True
        with tempfile.TemporaryDirectory(prefix="openhands-mixed-batch-") as temp:
            temp_root = Path(temp)
            index = temp_root / "index"
            git(source, "read-tree", HEAD, index=index)
            git(
                source,
                "apply",
                "--cached",
                "--whitespace=error",
                str(patch),
                index=index,
            )
            require(
                git(source, "diff", "--cached", "--name-only", index=index)
                .decode()
                .splitlines()
                == [TEST],
                "patch changes unexpected paths",
            )
            strengthened = git(source, "show", f":{TEST}", index=index)
            require(
                sha(strengthened) == PATCHED_TEST_SHA, "applied patch bytes mismatch"
            )
            probe_code = (
                "import json,sys,importlib.metadata; import openhands.sdk.agent.agent as m; "
                "print(json.dumps({'python':sys.version,'executable':sys.executable,"
                "'agent_module':m.__file__,'pytest':importlib.metadata.version('pytest')}))"
            )
            probe_command = [uv, "run", "--frozen", "python", "-B", "-c", probe_code]
            probe_env = env | {"PYTHONPYCACHEPREFIX": str(temp_root / "probe-cache")}
            code = run_logged(
                probe_command, source, probe_env, output / "environment.txt"
            )
            require(code == 0, "environment probe failed")
            probe = json.loads(
                (output / "environment.txt").read_text().splitlines()[-1]
            )
            require(
                Path(probe["agent_module"]).resolve() == source / PRODUCTION,
                "SDK was not imported from pinned native source",
            )
            require(
                probe["python"].startswith("3.13."), "native proof requires Python 3.13"
            )
            report["environment"] = probe
            report["environment_command"] = probe_command

            def pytest_run(
                label: str,
                production: bytes,
                tests: bytes,
                *,
                fail: bool = False,
                broad: bool = False,
            ):
                (source / PRODUCTION).write_bytes(production)
                (source / TEST).write_bytes(tests)
                xml, log = output / f"{label}.xml", output / f"{label}.txt"
                command = [
                    uv,
                    "run",
                    "--frozen",
                    "python",
                    "-B",
                    "-m",
                    "pytest",
                    *(SUITE if broad else [TEST]),
                    f"--junitxml={xml}",
                    "-p",
                    "no:cacheprovider",
                    "-o",
                    "addopts=-q --tb=short",
                ]
                started = time.monotonic()
                code = run_logged(
                    command,
                    source,
                    env | {"PYTHONPYCACHEPREFIX": str(temp_root / label)},
                    log,
                )
                result = {
                    "label": label,
                    "command": command,
                    "returncode": code,
                    "duration_seconds": round(time.monotonic() - started, 3),
                    "test_sha256": sha(tests),
                    "production_sha256": sha(production),
                    "xml": xml.name,
                    "log": log.name,
                    **summarize_junit(xml),
                }
                report["runs"].append(result)
                assert_result(result, expected_failure=fail, broad=broad)
                require(
                    (source / PRODUCTION).read_bytes() == production
                    and (source / TEST).read_bytes() == tests,
                    "native files changed during pytest",
                )
                require(
                    (source / "uv.lock").read_bytes() == original["uv.lock"],
                    "frozen uv lock changed",
                )
                print(f"{label}: {result['counts']}", flush=True)

            try:
                pytest_run("baseline-control", original[PRODUCTION], baseline)
                pytest_run("strengthened-control", original[PRODUCTION], strengthened)
                for field in ["risks", "details"]:
                    mutant = controlled_mutation(original[PRODUCTION], field)
                    diff = "".join(
                        difflib.unified_diff(
                            original[PRODUCTION].decode().splitlines(keepends=True),
                            mutant.decode().splitlines(keepends=True),
                            fromfile=f"a/{PRODUCTION}",
                            tofile=f"b/{PRODUCTION}",
                        )
                    )
                    (output / f"{field}-rotation.patch").write_text(
                        diff, encoding="utf-8"
                    )
                    pytest_run(f"{field}-rotation-baseline", mutant, baseline)
                    pytest_run(
                        f"{field}-rotation-strengthened",
                        mutant,
                        strengthened,
                        fail=True,
                    )
                pytest_run(
                    "restored-production-strengthened-suite",
                    original[PRODUCTION],
                    strengthened,
                    broad=True,
                )
            finally:
                (source / PRODUCTION).write_bytes(original[PRODUCTION])
                (source / TEST).write_bytes(original[TEST])
                report["restoration"] = {
                    name: (source / name).read_bytes() == data
                    for name, data in original.items()
                }
                require(
                    all(report["restoration"].values()), "source restoration failed"
                )
            require(len(report["runs"]) == 7, "incomplete run matrix")
            report["status"] = "PASS"
            exit_code = 0
    except BaseException as error:
        report["status"] = "ERROR"
        report["error"] = f"{type(error).__name__}: {error}"
        print(report["error"], file=sys.stderr)
    finally:
        if lock_owned:
            (source / PRODUCTION).write_bytes(original[PRODUCTION])
            (source / TEST).write_bytes(original[TEST])
            report["restoration"] = {
                name: (source / name).read_bytes() == data
                for name, data in original.items()
            }
            if not all(report["restoration"].values()):
                report["status"] = "ERROR"
                report["restoration_error"] = (
                    "input source bytes differ after restoration"
                )
                exit_code = 1
            lock.unlink()
        signal.signal(signal.SIGTERM, prior_sigterm)
        write_json(output / "report.json", report)
        files = {
            p.name: {"sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}
            for p in sorted(output.iterdir())
            if p.is_file()
        }
        write_json(
            output / "manifest.json",
            {
                "schema": "sha256-closed-files-v1",
                "files": files,
                "excludes": ["manifest.json"],
            },
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
