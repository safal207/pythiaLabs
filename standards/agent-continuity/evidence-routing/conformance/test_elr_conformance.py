from __future__ import annotations

import copy
import unittest
from pathlib import Path

from elr_reference import (
    GRAPH_SCHEMA,
    RECEIPT_SCHEMA,
    REQUEST_SCHEMA,
    digest_ref,
    load_json,
    schema_errors,
    select_route,
    sign_receipt,
    verify_receipt,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIXTURES = ROOT / "fixtures"

GRAPH = FIXTURES / "reference-proof-graph.json"
LOW = FIXTURES / "low-risk-request.json"
HIGH = FIXTURES / "high-risk-request.json"


class ELRConformanceTests(unittest.TestCase):
    def graph(self):
        return load_json(GRAPH)

    def low(self):
        return load_json(LOW)

    def high(self):
        return load_json(HIGH)

    def test_01_published_schemas_accept_reference_fixtures(self):
        self.assertEqual(schema_errors(self.graph(), GRAPH_SCHEMA), [])
        self.assertEqual(schema_errors(self.low(), REQUEST_SCHEMA), [])
        self.assertEqual(schema_errors(self.high(), REQUEST_SCHEMA), [])

    def test_02_low_risk_selects_cheapest_sync_route(self):
        status, receipt = select_route(self.low(), self.graph())
        self.assertEqual(status, "SELECTED")
        self.assertEqual(receipt["selected_edge_ids"], ["sync-check", "sync-execute"])
        self.assertTrue(verify_receipt(receipt, self.low(), self.graph()))

    def test_03_high_risk_selects_independent_human_consumption_route(self):
        status, receipt = select_route(self.high(), self.graph())
        self.assertEqual(status, "SELECTED")
        self.assertEqual(
            receipt["selected_edge_ids"],
            ["independent-verifier", "human-defer-resolve", "consume-and-execute"],
        )
        self.assertTrue(verify_receipt(receipt, self.high(), self.graph()))

    def test_04_zero_cost_route_missing_hard_proof_cannot_win(self):
        graph = self.graph()
        graph["nodes"].append("CHEAP")
        graph["edges"].extend([
            {
                "edge_id": "free-shortcut",
                "from": "START",
                "to": "CHEAP",
                "provides": ["authority_current", "scope_bound"],
                "bindings": {},
                "cost": {"latency": 0, "compute": 0, "coordination": 0, "monetary": 0},
            },
            {
                "edge_id": "free-execute",
                "from": "CHEAP",
                "to": "EXECUTE",
                "provides": [],
                "bindings": {},
                "cost": {"latency": 0, "compute": 0, "coordination": 0, "monetary": 0},
            },
        ])
        status, receipt = select_route(self.high(), graph)
        self.assertEqual(status, "SELECTED")
        self.assertNotIn("free-shortcut", receipt["selected_edge_ids"])

    def test_05_target_reached_without_required_proofs_is_not_admissible(self):
        graph = {
            "schema_version": "elr-graph/0.1",
            "graph_id": "shortcut-only",
            "nodes": ["START", "EXECUTE"],
            "edges": [{
                "edge_id": "shortcut",
                "from": "START",
                "to": "EXECUTE",
                "provides": [],
                "bindings": {},
                "cost": {"latency": 0, "compute": 0, "coordination": 0, "monetary": 0},
            }],
        }
        status, receipt = select_route(self.low(), graph)
        self.assertEqual(status, "BLOCKED_NO_ADMISSIBLE_ROUTE")
        self.assertIsNone(receipt)

    def test_06_expired_cached_evidence_reroutes_to_fresh_verifier(self):
        request = self.low()
        request["context"]["risk_tier"] = 3
        request["context"]["now_tick"] = 106
        request["required_proofs"] = ["authority_current", "scope_bound", "fresh_evidence"]
        status, receipt = select_route(request, self.graph())
        self.assertEqual(status, "SELECTED")
        self.assertEqual(receipt["selected_edge_ids"], ["independent-verifier", "verified-execute"])

    def test_07_future_evidence_is_rejected(self):
        graph = self.graph()
        cached = next(edge for edge in graph["edges"] if edge["edge_id"] == "cached-evidence")
        cached["bindings"]["evidence_observed_tick"] = 101
        request = self.low()
        request["context"]["risk_tier"] = 3
        request["required_proofs"] = ["authority_current", "scope_bound", "fresh_evidence"]
        status, receipt = select_route(request, graph)
        self.assertEqual(status, "SELECTED")
        self.assertEqual(receipt["selected_edge_ids"], ["independent-verifier", "verified-execute"])

    def test_08_authority_epoch_drift_invalidates_bound_routes(self):
        request = self.high()
        request["context"]["authority_epoch"] = 5
        status, receipt = select_route(request, self.graph())
        self.assertEqual(status, "BLOCKED_NO_ADMISSIBLE_ROUTE")
        self.assertIsNone(receipt)

    def test_09_policy_version_drift_invalidates_bound_routes(self):
        request = self.high()
        request["context"]["policy_version"] = "policy:v2"
        status, _ = select_route(request, self.graph())
        self.assertEqual(status, "BLOCKED_NO_ADMISSIBLE_ROUTE")

    def test_10_state_version_drift_invalidates_bound_routes(self):
        request = self.high()
        request["context"]["state_version"] = "state:20"
        status, _ = select_route(request, self.graph())
        self.assertEqual(status, "BLOCKED_NO_ADMISSIBLE_ROUTE")

    def test_11_action_scope_drift_invalidates_bound_routes(self):
        request = self.high()
        request["context"]["action_scope_digest"] = "sha256:" + ("b" * 64)
        status, _ = select_route(request, self.graph())
        self.assertEqual(status, "BLOCKED_NO_ADMISSIBLE_ROUTE")

    def test_12_risk_ceiling_prevents_low_risk_sync_route_for_high_risk_action(self):
        request = self.low()
        request["context"]["risk_tier"] = 5
        status, receipt = select_route(request, self.graph())
        self.assertEqual(status, "SELECTED")
        self.assertNotIn("sync-check", receipt["selected_edge_ids"])

    def test_13_irreversible_action_rejects_reversible_only_shortcut(self):
        graph = self.graph()
        graph["nodes"].append("REV")
        graph["edges"].extend([
            {
                "edge_id": "reversible-only",
                "from": "START",
                "to": "REV",
                "provides": ["authority_current", "scope_bound"],
                "bindings": {"requires_reversible": True},
                "cost": {"latency": 0, "compute": 0, "coordination": 0, "monetary": 0},
            },
            {
                "edge_id": "rev-exec",
                "from": "REV",
                "to": "EXECUTE",
                "provides": [],
                "bindings": {},
                "cost": {"latency": 0, "compute": 0, "coordination": 0, "monetary": 0},
            },
        ])
        request = self.low()
        request["context"]["reversible"] = False
        status, receipt = select_route(request, graph)
        self.assertEqual(status, "SELECTED")
        self.assertNotIn("reversible-only", receipt["selected_edge_ids"])

    def test_14_proofs_accumulate_across_multiple_edges(self):
        status, receipt = select_route(self.high(), self.graph())
        self.assertEqual(status, "SELECTED")
        self.assertTrue(set(self.high()["required_proofs"]).issubset(receipt["accumulated_proofs"]))

    def test_15_cost_weights_choose_between_admissible_routes_only(self):
        graph = self.graph()
        graph["nodes"].append("ALT")
        graph["edges"].extend([
            {
                "edge_id": "alt-proof",
                "from": "START",
                "to": "ALT",
                "provides": ["authority_current", "scope_bound"],
                "bindings": {"max_risk_tier": 2},
                "cost": {"latency": 0, "compute": 10, "coordination": 0, "monetary": 0},
            },
            {
                "edge_id": "alt-exec",
                "from": "ALT",
                "to": "EXECUTE",
                "provides": [],
                "bindings": {},
                "cost": {"latency": 0, "compute": 0, "coordination": 0, "monetary": 0},
            },
        ])
        request = self.low()
        request["cost_weights"] = {"latency": 10, "compute": 0, "coordination": 1, "monetary": 1}
        status, receipt = select_route(request, graph)
        self.assertEqual(status, "SELECTED")
        self.assertEqual(receipt["selected_edge_ids"], ["alt-proof", "alt-exec"])

    def test_16_tie_break_is_deterministic_by_edge_path(self):
        graph = {
            "schema_version": "elr-graph/0.1",
            "graph_id": "tie",
            "nodes": ["START", "A", "B", "EXECUTE"],
            "edges": [
                {"edge_id": "b1", "from": "START", "to": "B", "provides": ["authority_current", "scope_bound"], "bindings": {}, "cost": {"latency": 1, "compute": 0, "coordination": 0, "monetary": 0}},
                {"edge_id": "b2", "from": "B", "to": "EXECUTE", "provides": [], "bindings": {}, "cost": {"latency": 1, "compute": 0, "coordination": 0, "monetary": 0}},
                {"edge_id": "a1", "from": "START", "to": "A", "provides": ["authority_current", "scope_bound"], "bindings": {}, "cost": {"latency": 1, "compute": 0, "coordination": 0, "monetary": 0}},
                {"edge_id": "a2", "from": "A", "to": "EXECUTE", "provides": [], "bindings": {}, "cost": {"latency": 1, "compute": 0, "coordination": 0, "monetary": 0}},
            ],
        }
        status, receipt = select_route(self.low(), graph)
        self.assertEqual(status, "SELECTED")
        self.assertEqual(receipt["selected_edge_ids"], ["a1", "a2"])

    def test_17_negative_cost_is_schema_invalid(self):
        graph = self.graph()
        graph["edges"][0]["cost"]["latency"] = -1
        status, _ = select_route(self.low(), graph)
        self.assertEqual(status, "BLOCKED_INVALID_GRAPH")

    def test_18_unknown_edge_endpoint_is_fail_closed(self):
        graph = self.graph()
        graph["edges"][0]["to"] = "MISSING"
        status, _ = select_route(self.low(), graph)
        self.assertEqual(status, "BLOCKED_INVALID_GRAPH")

    def test_19_duplicate_edge_id_is_fail_closed(self):
        graph = self.graph()
        duplicate = copy.deepcopy(graph["edges"][0])
        duplicate["from"] = "SYNC"
        graph["edges"].append(duplicate)
        status, _ = select_route(self.low(), graph)
        self.assertEqual(status, "BLOCKED_INVALID_GRAPH")

    def test_20_receipt_binds_request_and_graph_digests(self):
        request = self.low()
        graph = self.graph()
        status, receipt = select_route(request, graph)
        self.assertEqual(status, "SELECTED")
        self.assertEqual(receipt["request_digest"], digest_ref(request))
        self.assertEqual(receipt["graph_digest"], digest_ref(graph))
        self.assertEqual(schema_errors(receipt, RECEIPT_SCHEMA), [])

    def test_21_receipt_tamper_is_detected(self):
        request = self.low()
        graph = self.graph()
        _, receipt = select_route(request, graph)
        receipt["weighted_total_cost"] += 1
        self.assertFalse(verify_receipt(receipt, request, graph))

    def test_22_path_tamper_is_detected_even_if_receipt_digest_is_recomputed(self):
        request = self.low()
        graph = self.graph()
        _, receipt = select_route(request, graph)
        receipt["selected_edge_ids"] = ["cached-evidence", "cache-execute"]
        receipt["weighted_total_cost"] = 4
        receipt["accumulated_proofs"] = ["authority_current", "fresh_evidence", "scope_bound"]
        sign_receipt(receipt)
        self.assertFalse(verify_receipt(receipt, request, graph))

    def test_23_no_route_is_better_than_violating_a_hard_obligation(self):
        graph = self.graph()
        graph["edges"] = [
            edge for edge in graph["edges"]
            if edge["edge_id"] not in {"human-defer-resolve", "consume-and-execute"}
        ]
        status, receipt = select_route(self.high(), graph)
        self.assertEqual(status, "BLOCKED_NO_ADMISSIBLE_ROUTE")
        self.assertIsNone(receipt)

    def test_24_zero_cost_cycle_terminates_and_still_selects_valid_route(self):
        graph = self.graph()
        graph["nodes"].append("LOOP")
        graph["edges"].extend([
            {
                "edge_id": "loop-in",
                "from": "START",
                "to": "LOOP",
                "provides": [],
                "bindings": {},
                "cost": {"latency": 0, "compute": 0, "coordination": 0, "monetary": 0},
            },
            {
                "edge_id": "loop-back",
                "from": "LOOP",
                "to": "START",
                "provides": [],
                "bindings": {},
                "cost": {"latency": 0, "compute": 0, "coordination": 0, "monetary": 0},
            },
        ])
        status, receipt = select_route(self.low(), graph)
        self.assertEqual(status, "SELECTED")
        self.assertEqual(receipt["selected_edge_ids"], ["sync-check", "sync-execute"])


if __name__ == "__main__":
    unittest.main()
