from __future__ import annotations

import unittest

from orc_reference import evaluate_revocation_quiescence, evaluate_side_effect


class ORCConformanceTests(unittest.TestCase):
    def state_a4(self):
        return {
            "lane_id": "lane-alpha",
            "owner_ref": "agent:A",
            "ownership_epoch": 4,
            "head_event_id": "E42",
        }

    def state_b5(self):
        return {
            "lane_id": "lane-alpha",
            "owner_ref": "agent:B",
            "ownership_epoch": 5,
            "head_event_id": "E43",
        }

    def root_a(self, process_state="RUNNING"):
        return {
            "execution_id": "exec:A-root",
            "actor_ref": "agent:A",
            "authority_lane_id": "lane-alpha",
            "authority_owner_ref": "agent:A",
            "authority_epoch": 4,
            "root_execution_id": "exec:A-root",
            "parent_execution_id": None,
            "process_group_ref": "pg:A",
            "process_state": process_state,
        }

    def child_c(self, process_state="RUNNING"):
        return {
            "execution_id": "exec:C-child",
            "actor_ref": "agent:C",
            "authority_lane_id": "lane-alpha",
            "authority_owner_ref": "agent:A",
            "authority_epoch": 4,
            "root_execution_id": "exec:A-root",
            "parent_execution_id": "exec:A-root",
            "process_group_ref": "pg:A",
            "process_state": process_state,
        }

    def grandchild_d(self, process_state="RUNNING"):
        return {
            "execution_id": "exec:D-grandchild",
            "actor_ref": "agent:D",
            "authority_lane_id": "lane-alpha",
            "authority_owner_ref": "agent:A",
            "authority_epoch": 4,
            "root_execution_id": "exec:A-root",
            "parent_execution_id": "exec:C-child",
            "process_group_ref": "pg:A",
            "process_state": process_state,
        }

    def root_b(self, process_state="RUNNING"):
        return {
            "execution_id": "exec:B-root",
            "actor_ref": "agent:B",
            "authority_lane_id": "lane-alpha",
            "authority_owner_ref": "agent:B",
            "authority_epoch": 5,
            "root_execution_id": "exec:B-root",
            "parent_execution_id": None,
            "process_group_ref": "pg:B",
            "process_state": process_state,
        }

    def test_01_current_root_is_admitted(self):
        status, _ = evaluate_side_effect(self.state_a4(), self.root_a())
        self.assertEqual(status, "SIDE_EFFECT_ALLOWED")

    def test_02_current_child_inherits_authority_and_is_admitted(self):
        status, _ = evaluate_side_effect(self.state_a4(), self.child_c(), self.root_a())
        self.assertEqual(status, "SIDE_EFFECT_ALLOWED")

    def test_03_handoff_immediately_revokes_old_root_even_if_running(self):
        status, detail = evaluate_side_effect(self.state_b5(), self.root_a())
        self.assertEqual(status, "BLOCKED_REVOKED_AUTHORITY_EPOCH")
        self.assertEqual(detail["bound_authority_epoch"], 4)
        self.assertEqual(detail["current_ownership_epoch"], 5)

    def test_04_handoff_immediately_revokes_running_child(self):
        status, _ = evaluate_side_effect(self.state_b5(), self.child_c(), self.root_a())
        self.assertEqual(status, "BLOCKED_REVOKED_AUTHORITY_EPOCH")

    def test_05_handoff_immediately_revokes_running_grandchild(self):
        status, _ = evaluate_side_effect(self.state_b5(), self.grandchild_d(), self.child_c())
        self.assertEqual(status, "BLOCKED_REVOKED_AUTHORITY_EPOCH")

    def test_06_child_cannot_self_refresh_to_new_epoch_inside_old_lineage(self):
        child = self.child_c()
        child["authority_owner_ref"] = "agent:B"
        child["authority_epoch"] = 5
        status, _ = evaluate_side_effect(self.state_b5(), child, self.root_a())
        self.assertEqual(status, "BLOCKED_AUTHORITY_LINEAGE_ESCAPE")

    def test_07_child_cannot_change_root_identity_to_escape_revocation(self):
        child = self.child_c()
        child["root_execution_id"] = "exec:B-root"
        status, _ = evaluate_side_effect(self.state_a4(), child, self.root_a())
        self.assertEqual(status, "BLOCKED_AUTHORITY_LINEAGE_ESCAPE")

    def test_08_wrong_parent_binding_is_blocked(self):
        child = self.child_c()
        child["parent_execution_id"] = "exec:other"
        status, _ = evaluate_side_effect(self.state_a4(), child, self.root_a())
        self.assertEqual(status, "BLOCKED_PARENT_EXECUTION_MISMATCH")

    def test_09_new_owner_new_lineage_is_admitted(self):
        status, _ = evaluate_side_effect(self.state_b5(), self.root_b())
        self.assertEqual(status, "SIDE_EFFECT_ALLOWED")

    def test_10_kill_requested_is_not_quiescent(self):
        root = self.root_a(process_state="KILL_REQUESTED")
        child = self.child_c(process_state="RUNNING")
        status, detail = evaluate_revocation_quiescence(self.state_b5(), [root, child])
        self.assertEqual(status, "REVOCATION_PENDING_LIVE_EXECUTIONS")
        self.assertCountEqual(detail["live_execution_ids"], ["exec:A-root", "exec:C-child"])

    def test_11_exited_root_but_live_orphan_child_is_not_quiescent(self):
        root = self.root_a(process_state="EXITED")
        child = self.child_c(process_state="RUNNING")
        status, detail = evaluate_revocation_quiescence(self.state_b5(), [root, child])
        self.assertEqual(status, "REVOCATION_PENDING_LIVE_EXECUTIONS")
        self.assertEqual(detail["live_execution_ids"], ["exec:C-child"])

    def test_12_all_revoked_descendants_observed_exited_is_quiescent(self):
        executions = [
            self.root_a(process_state="EXITED"),
            self.child_c(process_state="EXITED"),
            self.grandchild_d(process_state="EXITED"),
        ]
        status, detail = evaluate_revocation_quiescence(self.state_b5(), executions)
        self.assertEqual(status, "REVOCATION_QUIESCENT")
        self.assertEqual(detail["live_execution_ids"], [])
        self.assertCountEqual(
            detail["revoked_execution_ids"],
            ["exec:A-root", "exec:C-child", "exec:D-grandchild"],
        )

    def test_13_current_new_owner_does_not_count_as_revoked_for_quiescence(self):
        status, detail = evaluate_revocation_quiescence(self.state_b5(), [self.root_b()])
        self.assertEqual(status, "REVOCATION_QUIESCENT")
        self.assertEqual(detail["revoked_execution_ids"], [])

    def test_14_unknown_stale_process_state_fails_closed_for_quiescence(self):
        stale = self.child_c(process_state="UNKNOWN")
        status, detail = evaluate_revocation_quiescence(self.state_b5(), [stale])
        self.assertEqual(status, "REVOCATION_PENDING_LIVE_EXECUTIONS")
        self.assertEqual(detail["live_execution_ids"], ["exec:C-child"])

    def test_15_owner_mismatch_is_blocked_even_when_epoch_matches(self):
        state = self.state_a4()
        execution = self.root_a()
        execution["authority_owner_ref"] = "agent:X"
        status, _ = evaluate_side_effect(state, execution)
        self.assertEqual(status, "BLOCKED_REVOKED_AUTHORITY_OWNER")

    def test_16_lane_mismatch_is_blocked(self):
        execution = self.root_a()
        execution["authority_lane_id"] = "lane-other"
        status, _ = evaluate_side_effect(self.state_a4(), execution)
        self.assertEqual(status, "BLOCKED_LANE_MISMATCH")


if __name__ == "__main__":
    unittest.main()
