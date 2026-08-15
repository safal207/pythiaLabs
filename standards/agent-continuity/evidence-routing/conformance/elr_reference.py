from __future__ import annotations

import hashlib
import heapq
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REQUEST_SCHEMA = ROOT / "schema" / "routing-request.schema.json"
GRAPH_SCHEMA = ROOT / "schema" / "proof-graph.schema.json"
RECEIPT_SCHEMA = ROOT / "schema" / "route-receipt.schema.json"

COST_KEYS = ("latency", "compute", "coordination", "monetary")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("document root must be object")
    return value


def schema_errors(document: Mapping[str, Any], schema_path: Path) -> list[str]:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    return [error.message for error in validator.iter_errors(dict(document))]


def canonical_bytes(document: Mapping[str, Any], excluded: str | None = None) -> bytes:
    body = {key: value for key, value in document.items() if key != excluded}
    return json.dumps(
        body,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def digest_ref(document: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(document)).hexdigest()


def receipt_digest(receipt: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(
        canonical_bytes(receipt, excluded="receipt_digest")
    ).hexdigest()


def sign_receipt(receipt: dict[str, Any]) -> None:
    receipt["receipt_digest"] = receipt_digest(receipt)


def structural_graph_error(graph: Mapping[str, Any]) -> str | None:
    nodes = graph["nodes"]
    if len(nodes) != len(set(nodes)):
        return "duplicate_node"
    edges = graph["edges"]
    if len(edges) != len({edge["edge_id"] for edge in edges}):
        return "duplicate_edge_id"
    node_set = set(nodes)
    for edge in edges:
        if edge["from"] not in node_set or edge["to"] not in node_set:
            return "unknown_edge_endpoint"
    return None


def edge_available(edge: Mapping[str, Any], context: Mapping[str, Any]) -> bool:
    bindings = edge.get("bindings", {})
    for name in ("action_scope_digest", "authority_epoch", "policy_version", "state_version"):
        if name in bindings and bindings[name] != context[name]:
            return False

    if "max_risk_tier" in bindings and context["risk_tier"] > bindings["max_risk_tier"]:
        return False
    if bindings.get("requires_reversible") is True and not context["reversible"]:
        return False
    if "valid_until_tick" in bindings and context["now_tick"] > bindings["valid_until_tick"]:
        return False

    if "evidence_observed_tick" in bindings:
        observed = bindings["evidence_observed_tick"]
        if observed > context["now_tick"]:
            return False
        max_age = bindings.get("max_evidence_age_ticks")
        if max_age is not None and context["now_tick"] - observed > max_age:
            return False

    return True


def weighted_edge_cost(edge: Mapping[str, Any], weights: Mapping[str, Any]) -> int:
    return sum(edge["cost"][key] * weights[key] for key in COST_KEYS)


def select_route(
    request: Mapping[str, Any],
    graph: Mapping[str, Any],
) -> tuple[str, dict[str, Any] | None]:
    if schema_errors(request, REQUEST_SCHEMA):
        return "BLOCKED_INVALID_REQUEST", None
    if schema_errors(graph, GRAPH_SCHEMA):
        return "BLOCKED_INVALID_GRAPH", None
    if structural_graph_error(graph) is not None:
        return "BLOCKED_INVALID_GRAPH", None
    if request["start_node"] not in graph["nodes"] or request["target_node"] not in graph["nodes"]:
        return "BLOCKED_INVALID_REQUEST", None

    required = frozenset(request["required_proofs"])
    adjacency: dict[str, list[Mapping[str, Any]]] = {
        node: [] for node in graph["nodes"]
    }
    for edge in graph["edges"]:
        if edge_available(edge, request["context"]):
            adjacency[edge["from"]].append(edge)
    for edges in adjacency.values():
        edges.sort(key=lambda edge: edge["edge_id"])

    # Dijkstra over (graph node, accumulated hard-proof set).
    # Inadmissible edges are removed before optimization. A cheap route can never
    # compensate for a missing proof obligation.
    start_state = (request["start_node"], frozenset())
    queue: list[tuple[int, tuple[str, ...], str, frozenset[str]]] = [
        (0, tuple(), request["start_node"], frozenset())
    ]
    best: dict[tuple[str, frozenset[str]], tuple[int, tuple[str, ...]]] = {
        start_state: (0, tuple())
    }

    while queue:
        total_cost, path, node, proofs = heapq.heappop(queue)
        state = (node, proofs)
        if best.get(state) != (total_cost, path):
            continue

        if node == request["target_node"] and required.issubset(proofs):
            receipt = {
                "schema_version": "elr-receipt/0.1",
                "request_id": request["request_id"],
                "request_digest": digest_ref(request),
                "graph_digest": digest_ref(graph),
                "selected_edge_ids": list(path),
                "accumulated_proofs": sorted(proofs),
                "required_proofs": sorted(required),
                "weighted_total_cost": total_cost,
                "evaluated_at_tick": request["context"]["now_tick"],
                "route_status": "ADMISSIBLE",
                "receipt_digest": "sha256:" + ("0" * 64),
            }
            sign_receipt(receipt)
            return "SELECTED", receipt

        for edge in adjacency[node]:
            next_proofs = frozenset(set(proofs).union(edge["provides"]))
            next_cost = total_cost + weighted_edge_cost(edge, request["cost_weights"])
            next_path = path + (edge["edge_id"],)
            next_state = (edge["to"], next_proofs)
            candidate = (next_cost, next_path)
            if next_state not in best or candidate < best[next_state]:
                best[next_state] = candidate
                heapq.heappush(
                    queue,
                    (next_cost, next_path, edge["to"], next_proofs),
                )

    return "BLOCKED_NO_ADMISSIBLE_ROUTE", None


def verify_receipt(
    receipt: Mapping[str, Any],
    request: Mapping[str, Any],
    graph: Mapping[str, Any],
) -> bool:
    """Verify historical selection integrity at the receipt's issuance tick.

    This intentionally does not answer whether the selected route remains
    admissible at a later consumption/use time. Use revalidate_receipt_for_use
    for that separate question.
    """
    if schema_errors(receipt, RECEIPT_SCHEMA):
        return False
    if receipt.get("request_id") != request.get("request_id"):
        return False
    if receipt.get("request_digest") != digest_ref(request):
        return False
    if receipt.get("graph_digest") != digest_ref(graph):
        return False
    if receipt.get("evaluated_at_tick") != request.get("context", {}).get("now_tick"):
        return False
    if receipt.get("receipt_digest") != receipt_digest(receipt):
        return False

    edge_by_id = {edge["edge_id"]: edge for edge in graph.get("edges", [])}
    node = request.get("start_node")
    proofs: set[str] = set()
    total = 0
    for edge_id in receipt.get("selected_edge_ids", []):
        edge = edge_by_id.get(edge_id)
        if edge is None or edge["from"] != node:
            return False
        if not edge_available(edge, request["context"]):
            return False
        proofs.update(edge["provides"])
        total += weighted_edge_cost(edge, request["cost_weights"])
        node = edge["to"]

    if node != request.get("target_node"):
        return False
    required = set(request.get("required_proofs", []))
    if not required.issubset(proofs):
        return False
    if receipt.get("weighted_total_cost") != total:
        return False
    if receipt.get("required_proofs") != sorted(required):
        return False
    if receipt.get("accumulated_proofs") != sorted(proofs):
        return False

    status, selected = select_route(request, graph)
    if status != "SELECTED" or selected is None:
        return False
    return (
        receipt.get("selected_edge_ids") == selected.get("selected_edge_ids")
        and receipt.get("weighted_total_cost") == selected.get("weighted_total_cost")
    )


def revalidate_receipt_for_use(
    receipt: Mapping[str, Any],
    request: Mapping[str, Any],
    graph: Mapping[str, Any],
    current_context: Mapping[str, Any],
) -> tuple[str, dict[str, Any] | None]:
    """Check whether a historically valid selected route is admissible now.

    Historical selection integrity and current applicability are separate facts:
    verify_receipt() proves the former at issuance time; this function first
    requires that proof, then replays only the selected route's edge bindings
    against a caller-supplied current context.

    The function does not re-optimize the route. A route may remain admissible
    even if a cheaper route exists now. If the selected route is no longer
    admissible, callers may issue a fresh routing request and call select_route().
    """
    if not verify_receipt(receipt, request, graph):
        return "INVALID_HISTORICAL_RECEIPT", None

    current_request = dict(request)
    current_request["context"] = dict(current_context)
    if schema_errors(current_request, REQUEST_SCHEMA):
        return "INVALID_CURRENT_CONTEXT", None

    evaluated_at = receipt.get("evaluated_at_tick")
    now_tick = current_context.get("now_tick")
    if not isinstance(evaluated_at, int) or not isinstance(now_tick, int) or now_tick < evaluated_at:
        return "INVALID_CURRENT_CONTEXT", {
            "evaluated_at_tick": evaluated_at,
            "checked_at_tick": now_tick,
            "reason": "current_time_precedes_receipt_evaluation",
        }

    edge_by_id = {edge["edge_id"]: edge for edge in graph.get("edges", [])}
    node = request.get("start_node")
    proofs: set[str] = set()

    for edge_id in receipt.get("selected_edge_ids", []):
        edge = edge_by_id.get(edge_id)
        if edge is None or edge["from"] != node:
            return "INVALID_HISTORICAL_RECEIPT", None
        if not edge_available(edge, current_context):
            return "BLOCKED_ROUTE_STALE_OR_DRIFTED", {
                "evaluated_at_tick": evaluated_at,
                "checked_at_tick": now_tick,
                "failed_edge_id": edge_id,
            }
        proofs.update(edge["provides"])
        node = edge["to"]

    required = set(request.get("required_proofs", []))
    if node != request.get("target_node") or not required.issubset(proofs):
        return "INVALID_HISTORICAL_RECEIPT", None

    return "CURRENTLY_ADMISSIBLE", {
        "evaluated_at_tick": evaluated_at,
        "checked_at_tick": now_tick,
        "selected_edge_ids": list(receipt.get("selected_edge_ids", [])),
        "accumulated_proofs": sorted(proofs),
    }
