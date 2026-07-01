from __future__ import annotations

import json
import unittest
from pathlib import Path

from action_envelope_reference import (
    ALLOW,
    ALLOW_OK,
    AUTHORIZATION_EXPIRED,
    AUTHORIZATION_MISMATCH,
    AUTHORIZATION_NOT_YET_VALID,
    BLOCK,
    DIGEST_MISMATCH,
    EVIDENCE_ACTION_MISMATCH,
    EVIDENCE_NOT_YET_VALID,
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
    def assert_decision(self, value, expected_decision, expected_reason, **kwargs):
        result = evaluate_action(value, **kwargs)
        self.assertEqual(
            (result["decision"], result["reason_code"]),
            (expected_decision, expected_reason),
        )

    def test_schema_is_valid_draft_2020_12(self):
        self.assertEqual(
            load_schema()["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )

    def test_example_matches_published_schema(self):
        self.assertEqual(schema_errors(load_example()), [])

    def test_valid_envelope_allows(self):
        self.assert_decision(load_example(), ALLOW, ALLOW_OK)

    def test_lowercase_utc_suffix_is_accepted_deterministically(self):
        value = load_example()
        value["created_at"] = "2026-07-01T19:00:00z"
        value["decision_time"] = "2026-07-01T19:05:00z"
        value["authorization"]["valid_from"] = "2026-07-01T18:00:00z"
        value["authorization"]["valid_until"] = "2026-07-01T20:00:00z"
        for row in value["evidence"]:
            row["observed_at"] = row["observed_at"][:-1] + "z"
            row["expires_at"] = row["expires_at"][:-1] + "z"
        self.assert_decision(redigest(value), ALLOW, ALLOW_OK)

    def test_unsupported_string_version_fails_closed(self):
        value = load_example()
        value["schema_version"] = "2.0"
        self.assert_decision(redigest(value), BLOCK, UNSUPPORTED_SCHEMA_VERSION)

    def test_missing_version_is_schema_invalid(self):
        value = load_example()
        del value["schema_version"]
        self.assert_decision(redigest(value), BLOCK, SCHEMA_INVALID)

    def test_wrong_type_version_is_schema_invalid(self):
        value = load_example()
        value["schema_version"] = 1
        self.assert_decision(redigest(value), BLOCK, SCHEMA_INVALID)

    def test_missing_required_field_fails_closed(self):
        value = load_example()
        del value["request"]["target"]
        self.assert_decision(redigest(value), BLOCK, SCHEMA_INVALID)

    def test_unknown_top_level_field_fails_closed(self):
        value = load_example()
        value["unexpected"] = True
        self.assert_decision(redigest(value), BLOCK, SCHEMA_INVALID)

    def test_unknown_nested_field_fails_closed(self):
        value = load_example()
        value["authorization"]["unexpected"] = True
        self.assert_decision(redigest(value), BLOCK, SCHEMA_INVALID)

    def test_tampered_envelope_digest_fails_closed(self):
        value = load_example()
        value["request"]["operation"] = "delete_service"
        self.assert_decision(value, BLOCK, DIGEST_MISMATCH)

    def test_authorization_is_bound_to_full_action_identity(self):
        cases = {
            "actor_id": "user-other",
            "granted_to": "agent-other",
            "capability": "production.delete",
            "operation": "delete_service",
            "target": "service/other",
            "environment": "staging",
        }
        for field, replacement in cases.items():
            with self.subTest(field=field):
                value = load_example()
                value["authorization"][field] = replacement
                self.assert_decision(redigest(value), BLOCK, AUTHORIZATION_MISMATCH)

    def test_authorization_not_yet_valid_is_blocked(self):
        value = load_example()
        value["authorization"]["valid_from"] = "2026-07-01T19:05:01Z"
        self.assert_decision(redigest(value), BLOCK, AUTHORIZATION_NOT_YET_VALID)

    def test_expired_authorization_is_blocked(self):
        value = load_example()
        value["authorization"]["valid_until"] = "2026-07-01T19:04:59Z"
        self.assert_decision(redigest(value), BLOCK, AUTHORIZATION_EXPIRED)

    def test_evidence_must_be_bound_to_action(self):
        value = load_example()
        value["evidence"][0]["action_id"] = "action-other"
        self.assert_decision(redigest(value), BLOCK, EVIDENCE_ACTION_MISMATCH)

    def test_evidence_observed_after_decision_time_is_blocked(self):
        value = load_example()
        value["evidence"][0]["observed_at"] = "2026-07-01T19:05:01Z"
        self.assert_decision(redigest(value), BLOCK, EVIDENCE_NOT_YET_VALID)

    def test_stale_evidence_is_blocked(self):
        value = load_example()
        value["evidence"][0]["expires_at"] = "2026-07-01T19:04:59Z"
        self.assert_decision(redigest(value), BLOCK, EVIDENCE_STALE)

    def test_duplicate_evidence_id_is_schema_invalid(self):
        value = load_example()
        value["evidence"][1]["evidence_id"] = value["evidence"][0]["evidence_id"]
        self.assert_decision(redigest(value), BLOCK, SCHEMA_INVALID)

    def test_unknown_evidence_reference_is_blocked(self):
        value = load_example()
        value["preconditions"][0]["evidence_refs"] = ["ev-missing"]
        self.assert_decision(redigest(value), BLOCK, UNKNOWN_EVIDENCE_REF)

    def test_failed_precondition_is_blocked(self):
        value = load_example()
        value["preconditions"][0]["status"] = "failed"
        self.assert_decision(redigest(value), BLOCK, PRECONDITION_FAILED)

    def test_unknown_precondition_escalates(self):
        value = load_example()
        value["preconditions"][0]["status"] = "unknown"
        self.assert_decision(redigest(value), ESCALATE, PRECONDITION_UNRESOLVED)

    def test_duplicate_idempotency_key_is_blocked(self):
        value = load_example()
        self.assert_decision(
            value,
            BLOCK,
            REPLAY_DETECTED,
            seen_idempotency_keys={value["idempotency"]["key"]},
        )

    def test_required_but_missing_rollback_escalates(self):
        value = load_example()
        value["recovery"]["rollback_available"] = False
        value["recovery"]["rollback_ref"] = None
        self.assert_decision(redigest(value), ESCALATE, RECOVERY_NOT_READY)

    def test_decision_reason_codes_are_stable_strings(self):
        result = evaluate_action(load_example())
        self.assertRegex(result["decision"], r"^(ALLOW|BLOCK|ESCALATE)$")
        self.assertRegex(result["reason_code"], r"^[A-Z][A-Z0-9_]+$")


if __name__ == "__main__":
    unittest.main()
