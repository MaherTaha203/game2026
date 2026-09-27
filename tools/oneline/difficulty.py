"""Difficulty scoring and tier assignment for ONE LINE levels.

Difficulty must consider more than node count (docs/LEVEL_QUALITY.md,
MASTER_PROMPT §9/§36). The score blends graph size, branching, odd-degree
structure, solution length and (capped) trail multiplicity, then maps to a
human-facing tier.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from .graph import Graph
from .solver import count_eulerian_trails

# Ordered progression of tiers (docs/LEVEL_QUALITY.md §Difficulty Distribution).
TIERS: List[str] = ["tutorial", "easy", "normal", "advanced", "hard", "expert"]

# Tier is derived from edge count (inclusive upper bounds). Edge count is the
# clearest, most predictable primary driver of one-stroke difficulty and keeps
# tier assignment aligned with the quality gate's per-tier minimums.
_EDGE_TIER_BOUNDS = [
    ("tutorial", 3),
    ("easy", 7),
    ("normal", 13),
    ("advanced", 20),
    ("hard", 30),
    ("expert", math.inf),
]


def tier_from_edges(edge_count: int) -> str:
    for name, upper in _EDGE_TIER_BOUNDS:
        if edge_count <= upper:
            return name
    return "expert"


@dataclass
class DifficultyMetrics:
    """Raw signals feeding the difficulty score, kept for reporting."""

    node_count: int
    edge_count: int
    max_degree: int
    odd_count: int
    trail_count_capped: int
    branch_nodes: int  # nodes with degree >= 3 (real decision points)
    score: float
    tier: str


def _trail_factor(trail_count_capped: int) -> float:
    """Fewer distinct solutions => harder. Maps count to a [0, 1]-ish factor."""
    if trail_count_capped <= 0:
        return 1.0
    # 1 solution -> ~1.0 (hard), many solutions -> approaches 0 (forgiving).
    return 1.0 / (1.0 + math.log2(trail_count_capped))


def compute_difficulty(graph: Graph, *, trail_cap: int = 128) -> DifficultyMetrics:
    """Compute a deterministic difficulty score and tier for a graph."""
    v = graph.node_count
    e = graph.edge_count
    max_deg = graph.max_degree()
    odd = len(graph.odd_degree_nodes())
    branch_nodes = sum(1 for nid in graph.node_ids if graph.degree(nid) >= 3)
    trails = count_eulerian_trails(graph, cap=trail_cap)

    # Continuous score used only for fine-grained ordering *within* the campaign
    # (the tier itself comes from edge count). Edges dominate; branching, degree,
    # solution forcing (few trails) and open-trail structure refine it.
    score = (
        1.5 * e
        + 0.4 * v
        + 0.9 * branch_nodes
        + 0.8 * max(0, max_deg - 2)
        + 3.0 * _trail_factor(trails)
        + (1.0 if odd == 2 else 0.0)
    )
    score = round(score, 3)

    tier = tier_from_edges(e)

    return DifficultyMetrics(
        node_count=v,
        edge_count=e,
        max_degree=max_deg,
        odd_count=odd,
        trail_count_capped=trails,
        branch_nodes=branch_nodes,
        score=score,
        tier=tier,
    )


def tier_index(tier: str) -> int:
    return TIERS.index(tier)
