"""Level quality scoring and duplicate / near-duplicate detection.

A level is not acceptable merely because it is solvable (MASTER_PROMPT §35).
This module scores candidate quality and detects layout-equivalent duplicates
(robust to relabeling, rotation, mirroring and translation) via a canonical
graph signature plus an exact isomorphism confirmation for signature collisions.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from .graph import Graph, normalize_edge
from .difficulty import DifficultyMetrics


@dataclass
class QualityResult:
    ok: bool
    score: float
    reasons: List[str]


# Quality tuning (documented in docs/LEVEL_QUALITY.md). Minimums match the lower
# edge bound of each tier in oneline.difficulty so tier and quality never conflict.
MIN_EDGES_BY_TIER = {
    "tutorial": 2,
    "easy": 4,
    "normal": 8,
    "advanced": 14,
    "hard": 21,
    "expert": 31,
}
# Tiers at/above this index must contain at least one decision point (branch).
_BRANCH_REQUIRED_FROM = 2  # "normal" and harder
QUALITY_THRESHOLD = 0.45

# Mobile geometry gates (normalized coordinates). These keep levels touch-friendly
# and on-screen on small phones (audit §9). Node radius is rendered adaptively at
# runtime (scripts/ui/puzzle_view.gd), but nodes must still be far enough apart to
# be individually tappable and edges long enough to trace on a ~320px screen.
MIN_NODE_DISTANCE = 0.09   # ~28px apart on a 320px play area
MIN_EDGE_LENGTH = 0.09
PLAY_MIN = 0.02            # bounding box must stay inside the playable area
PLAY_MAX = 0.98


def check_geometry(graph: Graph) -> Tuple[bool, List[str]]:
    """Return ``(ok, reasons)`` for the mobile-geometry gates.

    Checks minimum pairwise node distance, minimum edge length, and that the
    whole graph stays within the playable area.
    """
    reasons: List[str] = []
    nodes = graph.nodes
    # bounding box
    for n in nodes:
        if not (PLAY_MIN <= n.x <= PLAY_MAX) or not (PLAY_MIN <= n.y <= PLAY_MAX):
            reasons.append(f"node {n.id} outside playable area ({n.x:.3f},{n.y:.3f})")
            break
    # min pairwise node distance
    min_nd = 9.0
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            d = math.dist((nodes[i].x, nodes[i].y), (nodes[j].x, nodes[j].y))
            min_nd = min(min_nd, d)
    if nodes and min_nd < MIN_NODE_DISTANCE:
        reasons.append(f"nodes too close ({min_nd:.3f} < {MIN_NODE_DISTANCE})")
    # min edge length
    pos = {n.id: (n.x, n.y) for n in nodes}
    min_el = 9.0
    for a, b in graph.edges:
        min_el = min(min_el, math.dist(pos[a], pos[b]))
    if graph.edges and min_el < MIN_EDGE_LENGTH:
        reasons.append(f"edge too short ({min_el:.3f} < {MIN_EDGE_LENGTH})")
    return (len(reasons) == 0), reasons


def score_quality(graph: Graph, metrics: DifficultyMetrics) -> QualityResult:
    """Return a quality verdict in ``[0, 1]`` with human-readable reasons.

    Rejects levels that are too trivial for their tier, degenerate (a single
    path with no decisions when the tier expects some), or excessively complex
    to read.
    """
    reasons: List[str] = []
    hard_fail = False
    score = 1.0

    e = graph.edge_count
    v = graph.node_count

    min_edges = MIN_EDGES_BY_TIER.get(metrics.tier, 2)
    if e < min_edges:
        reasons.append(f"too few edges ({e}) for tier {metrics.tier} (min {min_edges})")
        score -= 0.5
        hard_fail = True

    # Triviality: at "normal" and harder, require at least one decision point.
    from .difficulty import tier_index

    if tier_index(metrics.tier) >= _BRANCH_REQUIRED_FROM and metrics.branch_nodes == 0:
        reasons.append("no decision points (pure path) at normal tier or harder")
        score -= 0.3
        hard_fail = True

    # Excessive complexity / readability: keep max degree sane for touch play.
    if metrics.max_degree > 6:
        reasons.append(f"max degree {metrics.max_degree} harms readability (>6)")
        score -= 0.25

    # Readability: too many nodes crammed relative to edges reads as noise.
    if v > 0 and e / v < 0.9:
        reasons.append(f"sparse graph (E/V={e / v:.2f}) reads as disconnected clutter")
        score -= 0.2

    # Mobile geometry gates (hard): spacing, edge length, on-screen bounds.
    geo_ok, geo_reasons = check_geometry(graph)
    if not geo_ok:
        reasons.extend(geo_reasons)
        score -= 0.4
        hard_fail = True

    score = max(0.0, min(1.0, round(score, 3)))
    ok = (score >= QUALITY_THRESHOLD) and not hard_fail
    return QualityResult(ok=ok, score=score, reasons=reasons)


# --------------------------------------------------------------------------
# Duplicate / near-duplicate detection
# --------------------------------------------------------------------------
class DuplicateIndex:
    """Detects layout-equivalent duplicates across a growing level collection.

    Two graphs are considered duplicates if they are isomorphic (same structure
    ignoring node ids and geometry). We bucket by a cheap canonical signature and
    only run the exact (exponential) isomorphism check within a bucket, which is
    tiny in practice.
    """

    def __init__(self) -> None:
        self._buckets: Dict[Tuple, List[Graph]] = {}

    def is_duplicate(self, graph: Graph) -> bool:
        sig = graph.canonical_signature()
        bucket = self._buckets.get(sig, [])
        for existing in bucket:
            if graphs_isomorphic(existing, graph):
                return True
        return False

    def add(self, graph: Graph) -> None:
        sig = graph.canonical_signature()
        self._buckets.setdefault(sig, []).append(graph)

    def add_if_new(self, graph: Graph) -> bool:
        """Add the graph unless a duplicate exists. Returns True if added."""
        if self.is_duplicate(graph):
            return False
        self.add(graph)
        return True

    def __len__(self) -> int:
        return sum(len(v) for v in self._buckets.values())


def graphs_isomorphic(g1: Graph, g2: Graph) -> bool:
    """Exact isomorphism test via degree-partition-guided backtracking.

    Adequate for ONE LINE's small graphs (well under ~20 nodes). Not a general
    high-performance isomorphism engine, but correct and bounded for this domain.
    """
    if g1.node_count != g2.node_count or g1.edge_count != g2.edge_count:
        return False
    if g1.degree_sequence() != g2.degree_sequence():
        return False

    ids1 = g1.node_ids
    ids2 = g2.node_ids

    # Group g2 candidates by degree to prune the search.
    by_degree: Dict[int, List[int]] = {}
    for nid in ids2:
        by_degree.setdefault(g2.degree(nid), []).append(nid)

    # Order g1 nodes by descending degree (most constrained first).
    order = sorted(ids1, key=lambda n: -g1.degree(n))
    mapping: Dict[int, int] = {}
    used2: Set[int] = set()

    def consistent(n1: int, n2: int) -> bool:
        # For every already-mapped neighbor relation, adjacency must match.
        for m1, m2 in mapping.items():
            if g1.has_edge(n1, m1) != g2.has_edge(n2, m2):
                return False
        return True

    def backtrack(idx: int) -> bool:
        if idx == len(order):
            return True
        n1 = order[idx]
        for n2 in by_degree.get(g1.degree(n1), []):
            if n2 in used2:
                continue
            if not consistent(n1, n2):
                continue
            mapping[n1] = n2
            used2.add(n2)
            if backtrack(idx + 1):
                return True
            del mapping[n1]
            used2.discard(n2)
        return False

    return backtrack(0)
