from __future__ import annotations

import copy
import unittest
from pathlib import Path

from elr_reference import (
    load_json,
    revalidate_receipt_for_use,
    select_route,
    verify_receipt,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIXTURES = ROOT / "fixtures"

GRAPH = FIXTURES / "reference-proof-graph.json"
LOW = FIXTURES / "low-risk-request.json"


class ELRUseTimeRevalidationTests(unittest.TestCase):
    def graph(self):
        return load_json(GRAPH)

    def low(self):
        return load_json(LOW)

    def test_25_historical_verifier_remains_bound_to_issuance_tick(self):
        request = self.low()
        graph = self.graph()
        status, receipt = select_route(request, graph)
        self.assertEqual(status, "SELECTED")
        self.assertTrue(verify_receipt(receipt, request, graph))

        restamped = copy.deepcopy(request)
        restamped["context"]["now_tick"] = request["context"]["now_tick"] + 10
        self.assertFalse(verify_receipt(receipt, restamped, graph))

    def test_26_use_time_revalidation_accepts_route_before_expiry(self):
        request = self.low()
        graph = self.graph()
        sync = next(edge for edge in graph["edges"] if edge["edge_id"] == "sync-check")
        sync["bindings"]["valid_until_tick"] = request["context"]["now_tick"] + 5

        status, receipt = select_route(request, graph)
        self.assertEqual(status, "SELECTED")

        current = copy.deepcopy(request["context"])
        current["now_tick"] += 4
        validity, detail = revalidate_receipt_for_use(receipt, request, graph, current)
        self.assertEqual(validity, "CURRENTLY_ADMISSIBLE")
        self.assertEqual(detail["checked_at_tick"], request["context"]["now_tick"] + 4)

    def test_27_use_time_revalidation_rejects_expired_selected_edge(self):
        request = self.low()
        graph = self.graph()
        sync = next(edge for edge in graph["edges"] if edge["edge_id"] == "sync-check")
        sync["bindings"]["valid_until_tick"] = request["context"]["now_tick"] + 5

        status, receipt = select_route(request, graph)
        self.assertEqual(status, "SELECTED")
        self.assertTrue(verify_receipt(receipt, request, graph))

        current = copy.deepcopy(request["context"])
        current["now_tick"] += 10
        validity, detail = revalidate_receipt_for_use(receipt, request, graph, current)
        self.assertEqual(validity, "BLOCKED_ROUTE_STALE_OR_DRIFTED")
        self.assertEqual(detail["failed_edge_id"], "sync-check")

    def test_28_use_time_revalidation_rejects_evidence_age_expiry(self):
        request = self.low()
        request["context"]["risk_tier"] = 3
        request["required_proofs"] = ["authority_current", "scope_bound", "fresh_evidence"]
        graph = self.graph()

        status, receipt = select_route(request, graph)
        self.assertEqual(status, "SELECTED")
        self.assertEqual(receipt["selected_edge_ids"], ["cached-evidence", "cache-execute"])

        current = copy.deepcopy(request["context"])
        current["now_tick"] = 106
        validity, detail = revalidate_receipt_for_use(receipt, request, graph, current)
        self.assertEqual(validity, "BLOCKED_ROUTE_STALE_OR_DRIFTED")
        self.assertEqual(detail["failed_edge_id"], "cached-evidence")

    def test_29_use_time_revalidation_rejects_authority_drift(self):
        request = self.low()
        graph = self.graph()
        status, receipt = select_route(request, graph)
        self.assertEqual(status, "SELECTED")

        current = copy.deepcopy(request["context"])
        current["now_tick"] += 1
        current["authority_epoch"] += 1
        validity, detail = revalidate_receipt_for_use(receipt, request, graph, current)
        self.assertEqual(validity, "BLOCKED_ROUTE_STALE_OR_DRIFTED")
        self.assertEqual(detail["failed_edge_id"], "sync-check")

    def test_30_use_time_revalidation_rejects_time_before_issuance(self):
        request = self.low()
        graph = self.graph()
        status, receipt = select_route(request, graph)
        self.assertEqual(status, "SELECTED")

        current = copy.deepcopy(request["context"])
        current["now_tick"] -= 1
        validity, detail = revalidate_receipt_for_use(receipt, request, graph, current)
        self.assertEqual(validity, "INVALID_CURRENT_CONTEXT")
        self.assertEqual(detail["reason"], "current_time_precedes_receipt_evaluation")


if __name__ == "__main__":
    unittest.main()
