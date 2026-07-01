from __future__ import annotations

import json
import unittest
from pathlib import Path

from action_envelope_reference import (
    ALLOW,
    ALLOW_OK,
    AUTHORIZATION_EXPIRED,
    AUTHORIZATION_MISMATCH,
    BLOCK,
    DIGEST_MISMATCH,
    EVIDENCE_ACTION_MISMATCH,
    EVIDENCE_STALE,
    ESCALATE,
    PRECONDITION_FAILED,
    PRECONDITION_UNRESOLVED,
    RECOVERY_NOT_READY,
    REPLAY_DETECTED,
    SCHEMA_INVALID,
    UNSUPPORTED_SCHEMA_VERSION,
    UNKNOWN_EVIDENCE_REF,
    evaluate_action,
    load_schema,
    schema_errors,
    with_computed_digest,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EXAMPLE_PATH = ROOT / "examples" / "action-envelope-v1.example.json"


def load_example():
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


def redigest(value):
    return with_computed_digest(value)


class ActionEnvelopeConformanceTest(unittest.TestCase):
    def test_schema_is_valid_draft_2020_12(self):
        self.assertEqual(
            load_schema()["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )

    def test_example_matches_published_schema(self):
        self.assertEqual(schema_errors(load_example()), [])

    def test_valid_envelope_allows(self):
        result = evaluate_action(load_example())
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            (ALLOW, ALLOW_OK),
        )

    def test_unsupported_version_fails_closed(self):
        value = load_example()
        value["schema_version"] = "2.0"
        value = redigest(value)
        result = evaluate_action(value)
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            (BLOCK, UNSUPPORTED_SCHEMA_VERSION),
        )

    def test_malformed_shape_fails_closed(self):
        value = load_example()
        del value["request"]["target"]
        value = redigest(value)
        result = evaluate_action(value)
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            (BLOCK, SCHEMA_INVALID),
        )

    def test_tampered_envelope_digest_fails_closed(self):
        value = load_example()
        value["request"]["operation"] = "delete_service"
        result = evaluate_action(value)
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            (BLOCK, DIGEST_MISMATCH),
        )

    def test_authorization_is_bound_to_agent_and_action(self):
        value = load_example()
        value["authorization"]["granted_to"] = "agent-other"
        value = redigest(value)
        result = evaluate_action(value)
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            (BLOCK, AUTHORIZATION_MISMATCH),
        )

    def test_expired_authorization_is_blocked(self):
        value = load_example()
        value["authorization"]["valid_until"] = "2026-07-01T19:04:59Z"
        value = redigest(value)
        result = evaluate_action(value)
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            (BLOCK, AUTHORIZATION_EXPIRED),
        )

    def test_evidence_must_be_bound_to_action(self):
        value = load_example()
        value["evidence"][0]["action_id"] = "action-other"
        value = redigest(value)
        result = evaluate_action(value)
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            (BLOCK, EVIDENCE_ACTION_MISMATCH),
        )

    def test_stale_evidence_is_blocked(self):
        value = load_example()
        value["evidence"][0]["expires_at"] = "2026-07-01T19:04:59Z"
        value = redigest(value)
        result = evaluate_action(value)
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            (BLOCK, EVIDENCE_STALE),
        )

    def test_unknown_evidence_reference_is_blocked(self):
        value = load_example()
        value["preconditions"][0]["evidence_refs"] = ["ev-missing"]
        value = redigest(value)
        result = evaluate_action(value)
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            (BLOCK, UNKNOWN_EVIDENCE_REF),
        )

    def test_failed_precondition_is_blocked(self):
        value = load_example()
        value["preconditions"][0]["status"] = "failed"
        value = redigest(value)
        result = evaluate_action(value)
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            (BLOCK, PRECONDITION_FAILED),
        )

    def test_unknown_precondition_escalates(self):
        value = load_example()
        value["preconditions"][0]["status"] = "unknown"
        value = redigest(value)
        result = evaluate_action(value)
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            (ESCALATE, PRECONDITION_UNRESOLVED),
        )

    def test_duplicate_idempotency_key_is_blocked(self):
        value = load_example()
        result = evaluate_action(
            value,
            seen_idempotency_keys={value["idempotency"]["key"]},
        )
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            (BLOCK, REPLAY_DETECTED),
        )

    def test_required_but_missing_rollback_escalates(self):
        value = load_example()
        value["recovery"]["rollback_available"] = False
        value["recovery"]["rollback_ref"] = None
        value = redigest(value)
        result = evaluate_action(value)
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            (ESCALATE, RECOVERY_NOT_READY),
        )

    def test_decision_reason_codes_are_stable_strings(self):
        result = evaluate_action(load_example())
        self.assertRegex(result["decision"], r"^(ALLOW|BLOCK|ESCALATE)$")
        self.assertRegex(result["reason_code"], r"^[A-Z][A-Z0-9_]+$")


if __name__ == "__main__":
    unittest.main()
