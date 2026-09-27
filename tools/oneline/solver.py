"""Eulerian-trail solver and trail counting for ONE LINE.

The solver produces an actual covering trail using **Hierholzer's algorithm**
and then re-validates it through the runtime rules (:func:`rules.trail_is_valid_solution`)
so that "solvable" always means "accepted by the same rules the player uses".
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from .graph import Graph, normalize_edge
from .rules import trail_is_valid_solution


def find_eulerian_trail(graph: Graph) -> Optional[List[int]]:
    """Return an Eulerian trail (node sequence) or ``None`` if none exists.

    Deterministic: neighbors are always explored in ascending id order and the
    start vertex is chosen deterministically, so the same graph yields the same
    trail (supports reproducible reference solutions).
    """
    if not graph.has_eulerian_trail():
        return None

    odd = graph.odd_degree_nodes()
    start = odd[0] if odd else min(graph.node_ids)

    # Mutable adjacency as sorted lists we consume from.
    adj: Dict[int, List[int]] = {
        nid: sorted(graph.neighbors(nid)) for nid in graph.node_ids
    }
    used: Set[Tuple[int, int]] = set()

    stack = [start]
    circuit: List[int] = []
    while stack:
        v = stack[-1]
        advanced = False
        for w in adj[v]:
            key = normalize_edge(v, w)
            if key not in used:
                used.add(key)
                stack.append(w)
                advanced = True
                break
        if not advanced:
            circuit.append(stack.pop())

    circuit.reverse()
    if len(circuit) != graph.edge_count + 1:
        return None  # graph not fully covered (should not happen if precheck passed)
    if not trail_is_valid_solution(graph, circuit):
        return None
    return circuit


def count_eulerian_trails(graph: Graph, cap: int = 512, max_steps: int = 60000) -> int:
    """Count distinct Eulerian trails, bounded for tractability.

    The count is a relative difficulty/uniqueness signal: a puzzle with exactly
    one trail (up to reversal) forces the player; a puzzle with many trails is
    more forgiving. Trails are counted as directed sequences (this double-counts
    by reversal), and the search is bounded two ways so it never blows up on
    dense graphs:

    * ``cap``       — stop once this many trails are found.
    * ``max_steps`` — stop after this many DFS expansions regardless.

    When the step budget is exhausted the function returns at least ``cap`` (a
    conservative "many trails" signal), because a search that cannot finish
    quickly is, for difficulty purposes, a highly-connected/forgiving puzzle.
    """
    if not graph.has_eulerian_trail():
        return 0

    edge_count = graph.edge_count
    found = 0
    steps = 0
    budget_exhausted = False
    node_ids = graph.node_ids

    # Precompute sorted neighbor lists once.
    neigh = {nid: sorted(graph.neighbors(nid)) for nid in node_ids}

    odd = graph.odd_degree_nodes()
    starts = odd if odd else list(node_ids)

    def dfs(v: int, used: Set[Tuple[int, int]], depth: int) -> None:
        nonlocal found, steps, budget_exhausted
        if found >= cap or budget_exhausted:
            return
        if depth == edge_count:
            found += 1
            return
        for w in neigh[v]:
            key = normalize_edge(v, w)
            if key not in used:
                steps += 1
                if steps > max_steps:
                    budget_exhausted = True
                    return
                used.add(key)
                dfs(w, used, depth + 1)
                used.discard(key)
                if found >= cap or budget_exhausted:
                    return

    for s in starts:
        dfs(s, set(), 0)
        if found >= cap or budget_exhausted:
            break

    if budget_exhausted and found < cap:
        return cap
    return found
