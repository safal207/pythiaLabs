from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from acb_reference import (
    attempt_consume,
    compute_execution_scope_digest,
    resolve_occurrence,
    schema_errors,
    AUTH_SCHEMA,
    EXEC_SCHEMA,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIXTURES = ROOT / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ACBConformanceTests(unittest.TestCase):
    def setUp(self) -> None:
        accepted = load_fixture("accepted-consumption.json")
        self.authorization = accepted["authorization"]
        self.execution = accepted["execution"]

    def test_01_schemas_accept_reference_fixture(self) -> None:
        self.assertEqual([], schema_errors(self.authorization, AUTH_SCHEMA))
        self.assertEqual([], schema_errors(self.execution, EXEC_SCHEMA))

    def test_02_exact_scope_match_consumes(self) -> None:
        result, updated, receipt = attempt_consume(self.authorization, self.execution)
        self.assertEqual("CONSUMED", result)
        self.assertEqual("consumed", updated["status"])
        self.assertEqual(1, updated["use_count"])
        self.assertEqual([self.execution["execution_id"]], updated["consumed_by_execution_ids"])
        self.assertEqual(self.authorization["decision_event_id"], receipt["decision_event_id"])
        self.assertEqual(self.execution["execution_id"], receipt["execution_id"])

    def test_03_normalized_args_change_blocks(self) -> None:
        execution = copy.deepcopy(self.execution)
        execution["normalized_args"]["amount"] = 1000
        result, _, receipt = attempt_consume(self.authorization, execution)
        self.assertEqual("BLOCKED", result)
        self.assertEqual("execution_scope_mismatch", receipt["reason"])

    def test_04_actor_change_blocks(self) -> None:
        execution = copy.deepcopy(self.execution)
        execution["actor_ref"] = "agent:B"
        result, _, receipt = attempt_consume(self.authorization, execution)
        self.assertEqual("BLOCKED", result)
        self.assertEqual("execution_scope_mismatch", receipt["reason"])

    def test_05_authority_epoch_change_blocks(self) -> None:
        execution = copy.deepcopy(self.execution)
        execution["authority_epoch"] = 18
        execution["current_conditions"]["authority_epoch"] = 18
        result, _, receipt = attempt_consume(self.authorization, execution)
        self.assertEqual("BLOCKED", result)
        self.assertEqual("execution_scope_mismatch", receipt["reason"])

    def test_06_freshness_change_blocks(self) -> None:
        execution = copy.deepcopy(self.execution)
        execution["current_conditions"]["account_snapshot"] = "acct:v8"
        result, _, receipt = attempt_consume(self.authorization, execution)
        self.assertEqual("BLOCKED", result)
        self.assertEqual("freshness_changed:account_snapshot", receipt["reason"])

    def test_07_missing_current_condition_blocks(self) -> None:
        execution = copy.deepcopy(self.execution)
        del execution["current_conditions"]["recipient_binding"]
        result, _, receipt = attempt_consume(self.authorization, execution)
        self.assertEqual("BLOCKED", result)
        self.assertEqual("current_condition_missing:recipient_binding", receipt["reason"])

    def test_08_one_shot_retry_is_blocked(self) -> None:
        first_result, consumed, _ = attempt_consume(self.authorization, self.execution)
        self.assertEqual("CONSUMED", first_result)
        retry = copy.deepcopy(self.execution)
        retry["execution_id"] = "exec:X2"
        second_result, _, receipt = attempt_consume(consumed, retry)
        self.assertEqual("BLOCKED", second_result)
        self.assertEqual("authorization_status_consumed", receipt["reason"])

    def test_09_reusable_authorization_respects_use_limit(self) -> None:
        authorization = copy.deepcopy(self.authorization)
        authorization["usage_policy"] = {"mode": "reusable", "max_uses": 2}
        x1 = copy.deepcopy(self.execution)
        x2 = copy.deepcopy(self.execution)
        x2["execution_id"] = "exec:X2"
        x3 = copy.deepcopy(self.execution)
        x3["execution_id"] = "exec:X3"
        result1, a1, _ = attempt_consume(authorization, x1)
        result2, a2, _ = attempt_consume(a1, x2)
        result3, _, receipt3 = attempt_consume(a2, x3)
        self.assertEqual("CONSUMED", result1)
        self.assertEqual("CONSUMED", result2)
        self.assertEqual("consumed", a2["status"])
        self.assertEqual(2, a2["use_count"])
        self.assertEqual("BLOCKED", result3)
        self.assertEqual("authorization_status_consumed", receipt3["reason"])

    def test_10_cancelled_execution_blocks(self) -> None:
        execution = copy.deepcopy(self.execution)
        execution["cancelled"] = True
        result, _, receipt = attempt_consume(self.authorization, execution)
        self.assertEqual("BLOCKED", result)
        self.assertEqual("execution_cancelled", receipt["reason"])

    def test_11_superseded_execution_blocks(self) -> None:
        execution = copy.deepcopy(self.execution)
        execution["superseded"] = True
        result, _, receipt = attempt_consume(self.authorization, execution)
        self.assertEqual("BLOCKED", result)
        self.assertEqual("execution_superseded", receipt["reason"])

    def test_12_same_semantic_decision_distinct_occurrences(self) -> None:
        e1 = copy.deepcopy(self.authorization)
        e2 = copy.deepcopy(self.authorization)
        e2["decision_event_id"] = "event:E2"
        status1, found1 = resolve_occurrence(e1["decision_ref"], "event:E1", [e1, e2])
        status2, found2 = resolve_occurrence(e1["decision_ref"], "event:E2", [e1, e2])
        self.assertEqual("RESOLVED", status1)
        self.assertEqual("RESOLVED", status2)
        self.assertEqual("event:E1", found1["decision_event_id"])
        self.assertEqual("event:E2", found2["decision_event_id"])

    def test_13_semantic_only_resolution_is_ambiguous_on_collision(self) -> None:
        e1 = copy.deepcopy(self.authorization)
        e2 = copy.deepcopy(self.authorization)
        e2["decision_event_id"] = "event:E2"
        status, found = resolve_occurrence(e1["decision_ref"], None, [e1, e2])
        self.assertEqual("OCCURRENCE_AMBIGUOUS", status)
        self.assertIsNone(found)

    def test_14_wrong_event_ref_pairing_fails_closed(self) -> None:
        e1 = copy.deepcopy(self.authorization)
        e2 = copy.deepcopy(self.authorization)
        e2["decision_ref"] = "sha256:" + "b" * 64
        e2["decision_event_id"] = "event:E2"
        status, found = resolve_occurrence(e1["decision_ref"], "event:E2", [e1, e2])
        self.assertEqual("OCCURRENCE_REF_MISMATCH", status)
        self.assertIsNone(found)

    def test_15_non_active_authorization_blocks(self) -> None:
        for status in ["deferred", "denied", "expired", "stale", "revoked", "superseded", "cancelled", "consumed"]:
            with self.subTest(status=status):
                authorization = copy.deepcopy(self.authorization)
                authorization["status"] = status
                result, _, receipt = attempt_consume(authorization, self.execution)
                self.assertEqual("BLOCKED", result)
                self.assertEqual(f"authorization_status_{status}", receipt["reason"])

    def test_16_policy_version_change_blocks_explicitly(self) -> None:
        execution = copy.deepcopy(self.execution)
        execution["policy_version"] = "policy:v18"
        result, _, receipt = attempt_consume(self.authorization, execution)
        self.assertEqual("BLOCKED", result)
        self.assertEqual("policy_version_mismatch", receipt["reason"])

    def test_17_execution_id_is_not_in_scope_digest(self) -> None:
        retry = copy.deepcopy(self.execution)
        retry["execution_id"] = "exec:X2"
        self.assertEqual(compute_execution_scope_digest(self.execution), compute_execution_scope_digest(retry))

    def test_18_unique_semantic_ref_can_resolve_without_event_id(self) -> None:
        status, found = resolve_occurrence(self.authorization["decision_ref"], None, [self.authorization])
        self.assertEqual("RESOLVED", status)
        self.assertEqual("event:E1", found["decision_event_id"])


if __name__ == "__main__":
    unittest.main()
