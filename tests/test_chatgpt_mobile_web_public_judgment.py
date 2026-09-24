from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = (
    ROOT
    / "examples"
    / "lotus-cases"
    / "chatgpt-mobile-web-public-judgment-v1.json"
)
DOC_PATH = (
    ROOT
    / "docs"
    / "lotus-cases"
    / "CHATGPT_MOBILE_WEB_PUBLIC_JUDGMENT.md"
)


def _packet() -> dict:
    return json.loads(PACKET_PATH.read_text(encoding="utf-8"))


def test_judgment_is_bounded_and_non_executing() -> None:
    packet = _packet()
    authority = packet["authority"]

    assert packet["verdict"] == "ALLOW_BOUNDED_DIAGNOSTIC"
    assert authority["mode"] == "audit_only"
    for field in (
        "ownership",
        "approval",
        "execution",
        "account_access",
        "prompt_submission",
        "login_submission",
        "private_conversation_access",
        "external_submission",
        "security_claim",
        "deployment",
        "delivery",
        "merge",
    ):
        assert authority[field] is False


def test_only_one_user_impact_unknown_diagnostic_is_allowed() -> None:
    packet = _packet()
    observations = {item["id"]: item for item in packet["allowed_observations"]}

    assert observations["mobile-user-agent-variant"]["judgment"] == (
        "CONFIRMED_ARCHITECTURE_NOT_DEFECT"
    )
    assert observations["mobile-user-agent-variant"]["user_impact_established"] is False

    diagnostic = observations["mobile-login-console-error"]
    assert diagnostic["judgment"] == "P3_DIAGNOSTIC"
    assert diagnostic["user_impact_established"] is False
    assert diagnostic["security_impact_established"] is False
    assert diagnostic["visible_login_failure"] is False
    assert diagnostic["next_test"].strip()


def test_false_positive_signals_remain_rejected() -> None:
    packet = _packet()
    rejected = {item["id"]: item for item in packet["rejected_signals"]}

    assert rejected["mobile-event-post-aborts"]["judgment"] == (
        "REJECTED_FALSE_NETWORK_FAILURE"
    )
    assert rejected["composer-overlap-detector"]["judgment"] == (
        "REJECTED_FALSE_POSITIVE"
    )
    assert rejected["public-text-duplicate-heading-hypothesis"]["judgment"] == (
        "REJECTED_BY_BROWSER_MATRIX"
    )
    assert rejected["small-target-detector"]["judgment"] == (
        "INSUFFICIENT_FOR_ACCESSIBILITY_DEFECT"
    )


def test_authenticated_native_and_security_claims_are_blocked() -> None:
    blocked = "\n".join(_packet()["blocked_claims"])

    assert "login flow is broken" in blocked
    assert "event requests failed" in blocked
    assert "security vulnerability" in blocked
    assert "native Android or iOS" in blocked
    assert "Authenticated long-chat" in blocked


def test_exact_source_and_artifact_digests_are_preserved() -> None:
    source = _packet()["source"]

    assert source["repository"] == "safal207/LiminalQAengineer"
    assert source["pull_request"] == 106
    assert source["exact_head"] == "2407be212e19a393fcd0d8dd33d9fe444aea663b"
    assert source["baseline_run_id"] == 29783360123
    assert source["diagnostic_run_id"] == 29783766882
    assert len(source["baseline_artifact_sha256"]) == 64
    assert len(source["diagnostic_artifact_sha256"]) == 64


def test_human_document_preserves_scoped_pass_and_unknowns() -> None:
    document = DOC_PATH.read_text(encoding="utf-8")

    for required in (
        "ALLOW_BOUNDED_DIAGNOSTIC",
        "P3 diagnostic",
        "not a defect",
        "no visible login failure",
        "authenticated",
        "does not log in",
    ):
        assert required in document
