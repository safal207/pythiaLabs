"""Pinned external test sources used by synthetic conformance snapshots."""

from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[2]

_EXTERNAL_FIXTURES = {
    "cml": HERE / "fixtures" / "cml_test_lotus_docs_contract.py.fixture",
    "ls": HERE / "fixtures" / "ls_test_lotus_docs_contract.py.fixture",
}


def pinned_test_source(
    repository_id: str,
    relative_path: str,
    expected_sha256: str,
) -> str:
    """Load one canonical source fixture and verify its manifest digest."""
    if repository_id == "pythia":
        path = REPOSITORY_ROOT / relative_path
    else:
        path = _EXTERNAL_FIXTURES[repository_id]
    data = path.read_bytes()
    actual_sha256 = hashlib.sha256(data).hexdigest()
    if actual_sha256 != expected_sha256:
        raise AssertionError(
            f"pinned source fixture drift: {repository_id}: "
            f"{actual_sha256} != {expected_sha256}"
        )
    return data.decode("utf-8")
