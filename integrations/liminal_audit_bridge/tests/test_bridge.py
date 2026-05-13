from pathlib import Path

from liminal_audit_bridge.bridge import final_decision, load_transcript, run_checks, transcript_to_ttrace


def test_sample_transcript_produces_hold_decision() -> None:
    root = Path(__file__).resolve().parents[1]
    transcript = load_transcript(root / "examples" / "petri_like_transcript.json")

    records = transcript_to_ttrace(transcript)
    decisions = run_checks(records)

    assert len(records) == 5
    assert final_decision(decisions) == "HOLD"
    assert any(decision.reason_code == "EVAL_AWARENESS_SIGNAL" for decision in decisions)
    assert any(decision.reason_code == "ACTION_BEFORE_EXPLICIT_COMMIT" for decision in decisions)


def test_trace_records_have_hash_chain() -> None:
    root = Path(__file__).resolve().parents[1]
    transcript = load_transcript(root / "examples" / "petri_like_transcript.json")

    records = transcript_to_ttrace(transcript)

    assert records[0]["seal"]["prev_hash"] is None
    for previous, current in zip(records, records[1:]):
        assert current["seal"]["prev_hash"] == previous["seal"]["record_hash"]
