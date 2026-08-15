from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = (
    ROOT
    / "examples"
    / "lotus-cases"
    / "tradernet-product-funnel-judgment-v1.json"
)
DOC_PATH = (
    ROOT
    / "docs"
    / "lotus-cases"
    / "TRADERNET_PRODUCT_FUNNEL_JUDGMENT.md"
)


def _packet() -> dict:
    return json.loads(PACKET_PATH.read_text(encoding="utf-8"))


def test_judgment_is_advisory_and_non_executing() -> None:
    packet = _packet()
    authority = packet["authority"]

    assert packet["verdict"] == "ESCALATE"
    assert authority["mode"] == "audit_only"
    assert authority["ownership"] is False
    assert authority["approval"] is False
    assert authority["execution"] is False
    assert authority["account_access"] is False
    assert authority["order_execution"] is False
    assert authority["external_submission"] is False
    assert authority["experiment_launch"] is False
    assert authority["deployment"] is False
    assert authority["merge"] is False


def test_only_source_confirmed_findings_are_confirmed() -> None:
    packet = _packet()
    confirmed = packet["confirmed_for_human_reporting"]
    recommendations = packet["recommendations_allowed"]

    assert len(confirmed) == 4
    assert all(item["status"] == "CONFIRMED" for item in confirmed)
    assert all(
        item["source_status"] in {"HYPOTHESIS", "NEEDS_AUTHENTICATED_EVIDENCE"}
        for item in recommendations
    )


def test_authenticated_product_claims_remain_blocked() -> None:
    packet = _packet()
    blocked = "\n".join(packet["blocked_claims"])

    assert "authenticated Tradernet order form" in blocked
    assert "Stop Loss or Take Profit" in blocked
    assert "mobile web" in blocked
    assert "increase conversion" in blocked
    assert "security vulnerability" in blocked


def test_clickfunnels_is_not_subject_evidence_or_pressure_authority() -> None:
    boundary = _packet()["clickfunnels_boundary"]

    assert boundary["role"] == "pattern_reference_only"
    assert boundary["vendor_claims_are_tradernet_evidence"] is False
    assert boundary["false_urgency_allowed"] is False
    assert boundary["pressure_to_trade_allowed"] is False
    assert boundary["preselected_paid_or_risk_increasing_option_allowed"] is False


def test_judgment_references_exact_source_head() -> None:
    packet = _packet()

    assert packet["source"]["repository"] == "safal207/LiminalQAengineer"
    assert packet["source"]["pull_request"] == 102
    assert (
        packet["source"]["exact_head"]
        == "d14d0e0cf434000c10609dc8627c288df5306df6"
    )


def test_human_document_preserves_needs_evidence_language() -> None:
    document = DOC_PATH.read_text(encoding="utf-8")

    assert "NEEDS_AUTHENTICATED_EVIDENCE" in document
    assert "ClickFunnels and SamCart are pattern references" in document
    assert "does not mean approve" in document
    assert "exact-build evidence" in document
