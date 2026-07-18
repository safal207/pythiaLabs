"""Validation and derived views for the Lotus system graph."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

GRAPH_ID = "lotus-family-system-v0.1.json"
NODE_COLS = ["id", "type", "space", "time", "hierarchy", "centrality_role"]
EDGE_COLS = ["id", "source", "target", "relation", "dimension"]
ROUTE_COLS = ["id", "repo", "scenario", "path", "trajectory", "outcome", "reason"]


def load(path: Path) -> dict[str, Any]:
    """Load one compact graph or route model object."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("model root must be an object")
    return value


def rows(
    model: dict[str, Any], key: str, columns: list[str]
) -> list[dict[str, Any]]:
    """Expand compact positional rows after checking their declared columns."""
    declared = model.get(f"{key[:-1]}_columns") if key.endswith("s") else None
    if declared != columns:
        raise ValueError(f"unexpected {key} columns")
    result = []
    for raw in model.get(key, []):
        if not isinstance(raw, list) or len(raw) != len(columns):
            raise ValueError(f"invalid {key} row")
        result.append(dict(zip(columns, raw)))
    return result


def validate_graph(graph: dict[str, Any]) -> dict[str, Any]:
    """Validate graph identity, topology, dimensions, centers, and trajectories."""
    if graph.get("schema_version") != "pythia.lotus_system_graph.compact.v0.1":
        raise ValueError("unsupported system graph schema")
    if graph.get("graph_id") != GRAPH_ID:
        raise ValueError("unexpected system graph identifier")
    if graph.get("authority") != "audit_only":
        raise ValueError("system graph must remain audit_only")
    required_dimensions = {
        "causal",
        "spatial",
        "temporal",
        "hierarchy",
        "trajectory",
    }
    if set(graph.get("dimensions", [])) != required_dimensions:
        raise ValueError("all five graph dimensions are required")

    nodes = rows(graph, "nodes", NODE_COLS)
    edges = rows(graph, "edges", EDGE_COLS)
    node_ids = [node["id"] for node in nodes]
    edge_ids = [edge["id"] for edge in edges]
    if len(node_ids) != len(set(node_ids)) or len(edge_ids) != len(set(edge_ids)):
        raise ValueError("node and edge ids must be unique")

    known = set(node_ids)
    phases = graph.get("temporal_phases", [])
    phase_index = {phase: index for index, phase in enumerate(phases)}
    for node in nodes:
        if not all(node[field] for field in ("space", "time", "hierarchy")):
            raise ValueError(f"node lacks spacetime hierarchy: {node['id']}")
        if node["time"] not in phase_index and node["time"] != "anchor":
            raise ValueError(f"unknown temporal phase: {node['id']}")

    adjacency: dict[str, list[str]] = {}
    edge_pairs: set[tuple[str, str]] = set()
    for edge in edges:
        if edge["source"] not in known or edge["target"] not in known:
            raise ValueError(f"dangling edge: {edge['id']}")
        pair = (edge["source"], edge["target"])
        if pair in edge_pairs:
            raise ValueError(f"duplicate edge pair: {pair}")
        edge_pairs.add(pair)
        adjacency.setdefault(edge["source"], []).append(edge["target"])

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        """Depth-first cycle check."""
        if node in visiting:
            raise ValueError(f"cycle at {node}")
        if node in visited:
            return
        visiting.add(node)
        for target in adjacency.get(node, []):
            visit(target)
        visiting.remove(node)
        visited.add(node)

    for node in known:
        visit(node)

    centers = graph.get("centers", [])
    center_ids = {row[0] for row in centers}
    if not center_ids or not center_ids <= known:
        raise ValueError("centers must reference graph nodes")

    trajectories = graph.get("trajectories", [])
    for trajectory_id, path, _ in trajectories:
        if len(path) < 2 or any(node not in known for node in path):
            raise ValueError(f"invalid trajectory: {trajectory_id}")
        for pair in zip(path, path[1:]):
            if pair not in edge_pairs:
                raise ValueError(f"trajectory gap {trajectory_id}: {pair}")

    return {
        "nodes": nodes,
        "edges": edges,
        "edge_pairs": edge_pairs,
        "centers": center_ids,
    }


def validate_routes(
    graph: dict[str, Any], route_model: dict[str, Any]
) -> list[dict[str, Any]]:
    """Validate route binding and every connected route path."""
    if (
        route_model.get("schema_version")
        != "pythia.lotus_system_routes.compact.v0.1"
    ):
        raise ValueError("unsupported route schema")
    expected_graph = graph.get("graph_id")
    if expected_graph != GRAPH_ID or route_model.get("graph") != expected_graph:
        raise ValueError("route model is bound to a different system graph")

    view = validate_graph(graph)
    routes = rows(route_model, "routes", ROUTE_COLS)
    route_ids: set[str] = set()
    for route in routes:
        if route["id"] in route_ids:
            raise ValueError(f"duplicate route: {route['id']}")
        route_ids.add(route["id"])
        path = route["path"]
        if len(path) < 2:
            raise ValueError(f"route too short: {route['id']}")
        for pair in zip(path, path[1:]):
            if pair not in view["edge_pairs"]:
                raise ValueError(f"route gap {route['id']}: {pair}")
    return routes


def centrality_report(
    graph: dict[str, Any], routes: list[dict[str, Any]]
) -> dict[str, Any]:
    """Compute review-priority centrality without assigning authority."""
    view = validate_graph(graph)
    degree: Counter[str] = Counter()
    for edge in view["edges"]:
        degree[edge["source"]] += 1
        degree[edge["target"]] += 1
    route_hits: Counter[str] = Counter(
        node for route in routes for node in route["path"]
    )
    maximum = max(route_hits.values(), default=1)
    nodes = []
    for node in view["nodes"]:
        node_id = node["id"]
        nodes.append(
            {
                "id": node_id,
                "degree": degree[node_id],
                "route_hits": route_hits[node_id],
                "blast_radius": round(route_hits[node_id] / maximum, 3),
                "is_center": node_id in view["centers"],
            }
        )
    nodes.sort(
        key=lambda row: (-row["route_hits"], -row["degree"], row["id"])
    )
    return {
        "schema_version": "pythia.lotus_centrality_report.v0.1",
        "meaning": (
            "review priority and blast radius only; "
            "never ownership or authority"
        ),
        "nodes": nodes,
    }


def traceability(routes: list[dict[str, Any]]) -> str:
    """Render a human-readable ledger derived from executable routes."""
    lines = [
        "# Lotus system route ledger",
        "",
        "| Route | Repository | Scenario | Trajectory | Expected |",
        "|---|---|---|---|---|",
    ]
    for route in routes:
        lines.append(
            f"| `{route['id']}` | `{route['repo']}` | "
            f"`{route['scenario']}` | "
            f"`{route['trajectory'] or 'runtime'}` | "
            f"`{route['outcome']} / {route['reason']}` |"
        )
    return "\n".join(lines) + "\n"
