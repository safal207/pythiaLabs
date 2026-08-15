from __future__ import annotations

import copy
import unittest

from hrc_reference import evaluate_handoff, evaluate_handoff_commit, evaluate_transition


class HRCConformanceTests(unittest.TestCase):
    def state(self):
        return {
            "schema_version": "hrc-state/0.1",
            "lane_id": "lane-alpha",
            "owner_ref": "agent:A",
            "ownership_epoch": 4,
            "head_event_id": "E42",
            "status": "ACTIVE",
        }

    def status_proposal(self):
        return {
            "schema_version": "hrc-proposal/0.1",
            "proposal_id": "P-status-1",
            "lane_id": "lane-alpha",
            "transition_kind": "STATUS",
            "writer_ref": "agent:A",
            "writer_ownership_epoch": 4,
            "observed_through_event_id": "E42",
            "expected_predecessor_id": "E42",
            "next_event_id": "E43",
            "next_status": "DONE",
        }

    def handoff_proposal(self):
        return {
            "schema_version": "hrc-proposal/0.1",
            "proposal_id": "P-handoff-1",
            "lane_id": "lane-alpha",
            "transition_kind": "HANDOFF",
            "writer_ref": "agent:A",
            "writer_ownership_epoch": 4,
            "observed_through_event_id": "E42",
            "expected_predecessor_id": "E42",
            "next_event_id": "E43",
            "target_owner_ref": "agent:B",
            "target_ownership_epoch": 5,
            "reachability_surface_ref": "watcher-inventory:v1",
        }

    def reachability(self):
        return {
            "schema_version": "hrc-reachability/0.1",
            "signal_id": "R-B-100",
            "participant_ref": "agent:B",
            "surface_ref": "watcher-inventory:v1",
            "status": "READY",
            "observed_at_tick": 100,
            "valid_until_tick": 110,
        }

    def ack(self):
        return {
            "schema_version": "hrc-ack/0.1",
            "ack_id": "ACK-B-E43",
            "lane_id": "lane-alpha",
            "recipient_ref": "agent:B",
            "accepted_handoff_event_id": "E43",
            "accepted_ownership_epoch": 5,
            "observed_predecessor_id": "E42",
        }

    def test_01_current_owner_with_current_basis_may_transition(self):
        status, _ = evaluate_transition(self.state(), self.status_proposal())
        self.assertEqual(status, "STATUS_TRANSITION_ALLOWED")

    def test_02_non_owner_writer_is_blocked(self):
        p = self.status_proposal()
        p["writer_ref"] = "agent:B"
        status, _ = evaluate_transition(self.state(), p)
        self.assertEqual(status, "BLOCKED_WRITER_NOT_OWNER")

    def test_03_stale_ownership_epoch_is_blocked(self):
        p = self.status_proposal()
        p["writer_ownership_epoch"] = 3
        status, _ = evaluate_transition(self.state(), p)
        self.assertEqual(status, "BLOCKED_OWNERSHIP_EPOCH_MISMATCH")

    def test_04_unread_predecessor_is_not_misclassified_as_cas(self):
        p = self.status_proposal()
        p["observed_through_event_id"] = "E40"
        status, _ = evaluate_transition(self.state(), p)
        self.assertEqual(status, "BLOCKED_UNREAD_PREDECESSOR")

    def test_05_true_cas_conflict_requires_coherent_prior_read_basis(self):
        p = self.status_proposal()
        p["observed_through_event_id"] = "E41"
        p["expected_predecessor_id"] = "E41"
        status, detail = evaluate_transition(self.state(), p)
        self.assertEqual(status, "BLOCKED_CAS_CONFLICT")
        self.assertEqual(detail["current_head_event_id"], "E42")

    def test_06_lane_mismatch_is_blocked(self):
        p = self.status_proposal()
        p["lane_id"] = "lane-other"
        status, _ = evaluate_transition(self.state(), p)
        self.assertEqual(status, "BLOCKED_LANE_MISMATCH")

    def test_07_handoff_without_reachability_is_pending_not_complete(self):
        status, _ = evaluate_handoff(self.state(), self.handoff_proposal(), None, 100)
        self.assertEqual(status, "PENDING_REACHABILITY_UNCHECKED")

    def test_08_wrong_participant_reachability_cannot_satisfy_handoff(self):
        r = self.reachability()
        r["participant_ref"] = "agent:C"
        status, _ = evaluate_handoff(self.state(), self.handoff_proposal(), r, 100)
        self.assertEqual(status, "BLOCKED_REACHABILITY_PARTICIPANT_MISMATCH")

    def test_09_unsurfaced_diagnostic_is_not_operational_signal(self):
        r = self.reachability()
        r["surface_ref"] = "hidden-process-table:v1"
        status, _ = evaluate_handoff(self.state(), self.handoff_proposal(), r, 100)
        self.assertEqual(status, "BLOCKED_REACHABILITY_NOT_SURFACED")

    def test_10_future_reachability_signal_is_blocked(self):
        r = self.reachability()
        r["observed_at_tick"] = 101
        status, _ = evaluate_handoff(self.state(), self.handoff_proposal(), r, 100)
        self.assertEqual(status, "BLOCKED_FUTURE_REACHABILITY_SIGNAL")

    def test_11_expired_reachability_is_pending_unreachable(self):
        status, detail = evaluate_handoff(self.state(), self.handoff_proposal(), self.reachability(), 111)
        self.assertEqual(status, "PENDING_UNREACHABLE")
        self.assertEqual(detail["reason"], "reachability_signal_expired")

    def test_12_known_unavailable_recipient_is_pending_unreachable(self):
        r = self.reachability()
        r["status"] = "UNAVAILABLE"
        status, _ = evaluate_handoff(self.state(), self.handoff_proposal(), r, 105)
        self.assertEqual(status, "PENDING_UNREACHABLE")

    def test_13_current_reachable_target_makes_handoff_deliverable(self):
        status, detail = evaluate_handoff(self.state(), self.handoff_proposal(), self.reachability(), 105)
        self.assertEqual(status, "HANDOFF_DELIVERABLE")
        self.assertEqual(detail["target_owner_ref"], "agent:B")

    def test_14_handoff_epoch_must_increment_exactly_once(self):
        p = self.handoff_proposal()
        p["target_ownership_epoch"] = 7
        status, _ = evaluate_handoff(self.state(), p, self.reachability(), 105)
        self.assertEqual(status, "BLOCKED_INVALID_HANDOFF_EPOCH")

    def test_15_deliverable_handoff_without_ack_is_not_committed(self):
        status, _ = evaluate_handoff_commit(self.state(), self.handoff_proposal(), self.reachability(), None, 105)
        self.assertEqual(status, "PENDING_RECIPIENT_ACK")

    def test_16_wrong_recipient_ack_is_blocked(self):
        ack = self.ack()
        ack["recipient_ref"] = "agent:C"
        status, _ = evaluate_handoff_commit(self.state(), self.handoff_proposal(), self.reachability(), ack, 105)
        self.assertEqual(status, "BLOCKED_ACK_RECIPIENT_MISMATCH")

    def test_17_ack_must_bind_exact_handoff_event(self):
        ack = self.ack()
        ack["accepted_handoff_event_id"] = "E99"
        status, _ = evaluate_handoff_commit(self.state(), self.handoff_proposal(), self.reachability(), ack, 105)
        self.assertEqual(status, "BLOCKED_ACK_EVENT_MISMATCH")

    def test_18_ack_must_bind_target_ownership_epoch(self):
        ack = self.ack()
        ack["accepted_ownership_epoch"] = 6
        status, _ = evaluate_handoff_commit(self.state(), self.handoff_proposal(), self.reachability(), ack, 105)
        self.assertEqual(status, "BLOCKED_ACK_EPOCH_MISMATCH")

    def test_19_ack_with_stale_predecessor_is_blocked(self):
        ack = self.ack()
        ack["observed_predecessor_id"] = "E41"
        status, _ = evaluate_handoff_commit(self.state(), self.handoff_proposal(), self.reachability(), ack, 105)
        self.assertEqual(status, "BLOCKED_ACK_STALE_PREDECESSOR")

    def test_20_exact_reachable_acknowledged_handoff_may_commit(self):
        status, detail = evaluate_handoff_commit(
            self.state(), self.handoff_proposal(), self.reachability(), self.ack(), 105
        )
        self.assertEqual(status, "HANDOFF_COMMIT_ALLOWED")
        self.assertEqual(detail["new_owner_ref"], "agent:B")
        self.assertEqual(detail["new_ownership_epoch"], 5)


if __name__ == "__main__":
    unittest.main()
