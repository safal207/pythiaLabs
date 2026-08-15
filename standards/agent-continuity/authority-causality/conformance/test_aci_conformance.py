from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from aci_reference import (
    MUTATION_SCHEMA,
    STATE_SCHEMA,
    TRANSITION_SCHEMA,
    apply_transition,
    authority_digest_ref,
    detect_split_authority,
    load_json,
    mutation_decision,
    schema_errors,
    sign_state,
    verify_state,
)


class AuthorityCausalityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.static = load_json(ROOT / "fixtures" / "accepted-static-owner.json")
        cls.transfer = load_json(ROOT / "fixtures" / "accepted-authority-transfer.json")
        cls.rejected = load_json(ROOT / "fixtures" / "rejected-authority-cases.json")

    def test_published_documents_are_schema_valid(self) -> None:
        self.assertEqual(schema_errors(self.static["authority_state"], STATE_SCHEMA), [])
        self.assertEqual(schema_errors(self.static["mutation"], MUTATION_SCHEMA), [])
        self.assertEqual(schema_errors(self.transfer["transition"], TRANSITION_SCHEMA), [])

    def test_static_owner_is_admissible_without_write_time_arbitration(self) -> None:
        self.assertEqual(
            mutation_decision(self.static["authority_state"], self.static["mutation"]),
            "ADMISSIBLE",
        )

    def test_authority_digest_is_tamper_evident(self) -> None:
        changed = copy.deepcopy(self.static["authority_state"])
        changed["owner_ref"] = "worker:mallory"
        self.assertFalse(verify_state(changed))
        self.assertEqual(mutation_decision(changed, self.static["mutation"]), "BLOCKED")

    def test_transfer_accepts_exact_authority_predecessor(self) -> None:
        status, new_state = apply_transition(
            self.transfer["previous_authority_state"],
            self.transfer["transition"],
        )
        self.assertEqual(status, "ACCEPTED")
        self.assertEqual(new_state, self.transfer["expected_new_authority_state"])

    def test_transfer_rejects_wrong_previous_digest(self) -> None:
        changed = copy.deepcopy(self.transfer["transition"])
        changed["expected_previous_authority_digest"] = "sha256:" + "0" * 64
        self.assertEqual(
            apply_transition(self.transfer["previous_authority_state"], changed)[0],
            "BLOCKED",
        )

    def test_transfer_rejects_stale_epoch(self) -> None:
        changed = copy.deepcopy(self.transfer["transition"])
        changed["expected_previous_epoch"] = 16
        self.assertEqual(
            apply_transition(self.transfer["previous_authority_state"], changed)[0],
            "BLOCKED",
        )

    def test_transfer_requires_exact_epoch_increment(self) -> None:
        changed = copy.deepcopy(self.transfer["transition"])
        changed["new_epoch"] = 19
        self.assertEqual(
            apply_transition(self.transfer["previous_authority_state"], changed)[0],
            "BLOCKED",
        )

    def test_stale_writer_after_handoff_is_blocked(self) -> None:
        case = self.rejected["stale_writer_after_handoff"]
        self.assertEqual(
            mutation_decision(case["current_authority_state"], case["stale_mutation"]),
            "BLOCKED",
        )

    def test_current_owner_after_handoff_is_admissible(self) -> None:
        case = self.rejected["stale_writer_after_handoff"]
        self.assertEqual(
            mutation_decision(case["current_authority_state"], case["current_mutation"]),
            "ADMISSIBLE",
        )

    def test_wrong_actor_is_blocked(self) -> None:
        changed = copy.deepcopy(self.static["mutation"])
        changed["actor_ref"] = "worker:B"
        self.assertEqual(mutation_decision(self.static["authority_state"], changed), "BLOCKED")

    def test_scope_violation_is_blocked(self) -> None:
        changed = copy.deepcopy(self.static["mutation"])
        changed["effect_ref"] = "effect:update:key:Y"
        self.assertEqual(mutation_decision(self.static["authority_state"], changed), "BLOCKED")

    def test_revocation_dominates_cached_context(self) -> None:
        state = copy.deepcopy(self.static["authority_state"])
        state["status"] = "revoked"
        sign_state(state)
        mutation = copy.deepcopy(self.static["mutation"])
        mutation["presented_authority_digest"] = authority_digest_ref(state)
        self.assertEqual(mutation_decision(state, mutation), "BLOCKED")

    def test_split_authority_is_detected(self) -> None:
        self.assertTrue(
            detect_split_authority(self.rejected["split_authority"]["authority_states"])
        )

    def test_state_cas_passes_only_with_current_authority_and_state(self) -> None:
        current_state = "sha256:" + "a" * 64
        mutation = copy.deepcopy(self.static["mutation"])
        mutation["expected_previous_state_digest"] = current_state
        mutation["new_state_digest"] = "sha256:" + "b" * 64
        self.assertEqual(
            mutation_decision(self.static["authority_state"], mutation, current_state),
            "ADMISSIBLE",
        )

    def test_state_cas_failure_blocks_even_with_current_authority(self) -> None:
        mutation = copy.deepcopy(self.static["mutation"])
        mutation["expected_previous_state_digest"] = "sha256:" + "a" * 64
        mutation["new_state_digest"] = "sha256:" + "b" * 64
        self.assertEqual(
            mutation_decision(
                self.static["authority_state"],
                mutation,
                "sha256:" + "c" * 64,
            ),
            "BLOCKED",
        )

    def test_authority_failure_blocks_even_with_current_state(self) -> None:
        mutation = copy.deepcopy(self.static["mutation"])
        mutation["presented_authority_epoch"] = 2
        mutation["expected_previous_state_digest"] = "sha256:" + "a" * 64
        mutation["new_state_digest"] = "sha256:" + "b" * 64
        self.assertEqual(
            mutation_decision(
                self.static["authority_state"],
                mutation,
                "sha256:" + "a" * 64,
            ),
            "BLOCKED",
        )


if __name__ == "__main__":
    unittest.main()
