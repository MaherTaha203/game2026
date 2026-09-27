"""Eulerian-trail solver and trail counting for ONE LINE.

The solver produces an actual covering trail using **Hierholzer's algorithm**
and then re-validates it through the runtime rules (:func:`rules.trail_is_valid_solution`)
so that "solvable" always means "accepted by the same rules the player uses".
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from .graph import Graph, normalize_edge
from .rules import trail_is_valid_solution


def _hierholzer(graph: Graph, start: int, used: Set[Tuple[int, int]]) -> List[int]:
    """Stack-based Hierholzer from ``start`` over edges not in ``used`` (mutated).

    Returns the node sequence of the trail it can build from ``start``. It covers
    every not-yet-used edge iff an Eulerian trail with ``start`` as an endpoint
    exists in the remaining graph; otherwise it returns a shorter walk (the caller
    detects incomplete coverage). Deterministic: neighbors explored ascending.
    """
    stack = [start]
    circuit: List[int] = []
    while stack:
        v = stack[-1]
        advanced = False
        for w in sorted(graph.neighbors(v)):
            key = normalize_edge(v, w)
            if key not in used:
                used.add(key)
                stack.append(w)
                advanced = True
                break
        if not advanced:
            circuit.append(stack.pop())
    circuit.reverse()
    return circuit


def find_eulerian_trail(graph: Graph) -> Optional[List[int]]:
    """Return an Eulerian trail (node sequence) or ``None`` if none exists.

    Uses Hierholzer's algorithm (O(E)). Deterministic: the start vertex and
    neighbor order are fixed, so the same graph yields the same trail.
    """
    if not graph.has_eulerian_trail():
        return None
    odd = graph.odd_degree_nodes()
    start = odd[0] if odd else min(graph.node_ids)
    circuit = _hierholzer(graph, start, set())
    if len(circuit) != graph.edge_count + 1:
        return None  # should not happen once has_eulerian_trail() passed
    if not trail_is_valid_solution(graph, circuit):
        return None
    return circuit


def find_completion(
    graph: Graph, used_edges: Set[Tuple[int, int]], current: Optional[int]
) -> List[int]:
    """Return the remaining node sequence that completes the puzzle from the
    current partial trail, or ``[]`` if the current state is a dead end.

    O(E) Hierholzer over the unused edges starting at ``current``. Powers hints:
    the first returned node is always a genuinely valid next move that keeps the
    puzzle completable (docs/GAME_RULES.md §10). No search budget, so it cannot
    time out on dense/expert levels.
    """
    if current is None:
        odd = graph.odd_degree_nodes()
        return [odd[0] if odd else min(graph.node_ids)]
    remaining = graph.edge_count - len(used_edges)
    if remaining <= 0:
        return []
    trail = _hierholzer(graph, current, set(used_edges))
    if len(trail) != remaining + 1:
        return []  # cannot cover all remaining edges from here -> dead end
    return trail[1:]


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
