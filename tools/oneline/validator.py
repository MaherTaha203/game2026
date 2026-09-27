"""Structural and solvability validation for ONE LINE levels.

The validator is deliberately strict and returns a machine-readable result so it
can drive both the generation pipeline and CI (MASTER_PROMPT §7, §35).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .graph import Graph, Node, normalize_edge
from .solver import find_eulerian_trail


@dataclass
class ValidationResult:
    """Outcome of validating a single level."""

    level_id: Optional[int]
    ok: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    solution_length: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level_id": self.level_id,
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "solution_length": self.solution_length,
        }


def _validate_positions(nodes: List[Node]) -> List[str]:
    errors: List[str] = []
    for n in nodes:
        if not (0.0 <= n.x <= 1.0) or not (0.0 <= n.y <= 1.0):
            errors.append(
                f"node {n.id} position out of range: ({n.x:.3f}, {n.y:.3f})"
            )
    return errors


def validate_level_dict(data: Dict[str, Any], *, require_solution: bool = True) -> ValidationResult:
    """Validate a raw level dictionary (post-JSON-load).

    Detects, at minimum (MASTER_PROMPT §7): invalid node references, prohibited
    duplicate edges, self-loops, disconnected graphs, impossible/no-solution
    puzzles and malformed level data.
    """
    level_id = data.get("id")
    errors: List[str] = []
    warnings: List[str] = []

    # ---- shape checks ----------------------------------------------------
    if not isinstance(data.get("nodes"), list) or not isinstance(data.get("edges"), list):
        errors.append("malformed level data: 'nodes' and 'edges' must be lists")
        return ValidationResult(level_id, False, errors, warnings)

    raw_nodes = data["nodes"]
    raw_edges = data["edges"]

    if len(raw_nodes) < 2:
        errors.append("a level must have at least 2 nodes")
    if len(raw_edges) < 1:
        errors.append("a level must have at least 1 edge")

    # ---- build node objects ---------------------------------------------
    nodes: List[Node] = []
    seen_ids = set()
    for i, rn in enumerate(raw_nodes):
        try:
            nid = int(rn["id"])
            nx = float(rn["x"])
            ny = float(rn["y"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"malformed node at index {i}: {rn!r}")
            continue
        if nid in seen_ids:
            errors.append(f"duplicate node id: {nid}")
            continue
        seen_ids.add(nid)
        nodes.append(Node(nid, nx, ny))

    errors.extend(_validate_positions(nodes))

    # ---- build edges with reference / duplicate / self checks ------------
    edge_pairs: List[Tuple[int, int]] = []
    seen_edges = set()
    for i, re in enumerate(raw_edges):
        try:
            a = int(re["a"])
            b = int(re["b"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"malformed edge at index {i}: {re!r}")
            continue
        if a not in seen_ids or b not in seen_ids:
            errors.append(f"edge references unknown node: ({a}, {b})")
            continue
        if a == b:
            errors.append(f"self-loop not allowed: ({a}, {b})")
            continue
        key = normalize_edge(a, b)
        if key in seen_edges:
            errors.append(f"duplicate edge: {key}")
            continue
        seen_edges.add(key)
        edge_pairs.append(key)

    if errors:
        return ValidationResult(level_id, False, errors, warnings)

    # ---- build graph and run structural / solvability checks -------------
    try:
        graph = Graph(nodes, edge_pairs)
    except ValueError as exc:  # pragma: no cover - defensive; caught above normally
        errors.append(f"graph construction failed: {exc}")
        return ValidationResult(level_id, False, errors, warnings)

    if graph.isolated_nodes():
        errors.append(f"isolated (degree-0) nodes present: {graph.isolated_nodes()}")

    if not graph.is_connected_ignoring_isolated():
        errors.append("graph is disconnected")

    odd = graph.odd_degree_nodes()
    if len(odd) not in (0, 2):
        errors.append(
            f"no Eulerian trail: {len(odd)} odd-degree vertices (must be 0 or 2)"
        )

    solution_length: Optional[int] = None
    if not errors and require_solution:
        trail = find_eulerian_trail(graph)
        if trail is None:
            errors.append("solver could not find a valid solution")
        else:
            solution_length = graph.edge_count
            # cross-check any stored reference solution length
            stored = data.get("solution_length")
            if stored is not None and stored != solution_length:
                errors.append(
                    f"stored solution_length {stored} != actual {solution_length}"
                )

    return ValidationResult(
        level_id=level_id,
        ok=not errors,
        errors=errors,
        warnings=warnings,
        solution_length=solution_length,
    )


def graph_from_level_dict(data: Dict[str, Any]) -> Graph:
    """Build a :class:`Graph` from validated level data (raises on malformed)."""
    nodes = [Node(int(n["id"]), float(n["x"]), float(n["y"])) for n in data["nodes"]]
    edges = [normalize_edge(int(e["a"]), int(e["b"])) for e in data["edges"]]
    return Graph(nodes, edges)
