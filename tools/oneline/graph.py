"""Immutable graph model for ONE LINE puzzles.

A :class:`Graph` is an undirected simple graph: nodes carry a normalized 2D
position and edges are unordered pairs of distinct node ids with no duplicates
and no self-loops (schema version 1). All structural queries needed by the
validator, solver, difficulty model and generator live here so there is exactly
one implementation of each graph primitive.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, List, Sequence, Set, Tuple


@dataclass(frozen=True)
class Node:
    """A puzzle node with a resolution-independent position in ``[0, 1]``."""

    id: int
    x: float
    y: float


def normalize_edge(a: int, b: int) -> Tuple[int, int]:
    """Return an edge as an ordered tuple ``(min, max)`` for canonical storage."""
    if a == b:
        raise ValueError(f"self-loops are not allowed (node {a})")
    return (a, b) if a < b else (b, a)


class Graph:
    """An undirected simple graph.

    The constructor validates only the invariants required to *build* a graph
    (well-formed references, no duplicate/self edges). Higher-level playability
    checks (connectivity, Eulerian property) live in :mod:`oneline.validator`.
    """

    __slots__ = ("_nodes", "_edges", "_adj")

    def __init__(self, nodes: Iterable[Node], edges: Iterable[Tuple[int, int]]):
        node_list = list(nodes)
        self._nodes: Dict[int, Node] = {}
        for n in node_list:
            if n.id in self._nodes:
                raise ValueError(f"duplicate node id: {n.id}")
            self._nodes[n.id] = n

        self._edges: List[Tuple[int, int]] = []
        seen: Set[Tuple[int, int]] = set()
        self._adj: Dict[int, Set[int]] = {nid: set() for nid in self._nodes}
        for a, b in edges:
            if a not in self._nodes or b not in self._nodes:
                raise ValueError(f"edge references unknown node: ({a}, {b})")
            key = normalize_edge(a, b)
            if key in seen:
                raise ValueError(f"duplicate edge: {key}")
            seen.add(key)
            self._edges.append(key)
            self._adj[key[0]].add(key[1])
            self._adj[key[1]].add(key[0])

    # ---- basic accessors -------------------------------------------------
    @property
    def nodes(self) -> List[Node]:
        return list(self._nodes.values())

    @property
    def node_ids(self) -> List[int]:
        return list(self._nodes.keys())

    @property
    def edges(self) -> List[Tuple[int, int]]:
        return list(self._edges)

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return len(self._edges)

    def has_node(self, nid: int) -> bool:
        return nid in self._nodes

    def has_edge(self, a: int, b: int) -> bool:
        if a not in self._adj:
            return False
        return b in self._adj[a]

    def neighbors(self, nid: int) -> Set[int]:
        return set(self._adj.get(nid, set()))

    def degree(self, nid: int) -> int:
        return len(self._adj.get(nid, set()))

    def edge_key(self, a: int, b: int) -> Tuple[int, int]:
        return normalize_edge(a, b)

    # ---- structural queries ---------------------------------------------
    def isolated_nodes(self) -> List[int]:
        """Node ids with degree 0."""
        return [nid for nid in self._nodes if self.degree(nid) == 0]

    def odd_degree_nodes(self) -> List[int]:
        """Node ids with odd degree (sorted for determinism)."""
        return sorted(nid for nid in self._nodes if self.degree(nid) % 2 == 1)

    def max_degree(self) -> int:
        if not self._nodes:
            return 0
        return max(self.degree(nid) for nid in self._nodes)

    def is_connected_ignoring_isolated(self) -> bool:
        """True if all non-isolated nodes form a single connected component.

        Isolated nodes (degree 0) are ignored. An empty or edge-less graph is
        treated as *not* connected for puzzle purposes (there is nothing to draw).
        """
        if self.edge_count == 0:
            return False
        start = self._edges[0][0]
        reachable = self._bfs(start)
        non_isolated = {nid for nid in self._nodes if self.degree(nid) > 0}
        return reachable == non_isolated

    def _bfs(self, start: int) -> Set[int]:
        seen: Set[int] = {start}
        stack = [start]
        while stack:
            cur = stack.pop()
            for nxt in self._adj[cur]:
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return seen

    def has_eulerian_trail(self) -> bool:
        """Authoritative solvability test (see docs/GAME_RULES.md §6)."""
        if not self.is_connected_ignoring_isolated():
            return False
        return len(self.odd_degree_nodes()) in (0, 2)

    # ---- canonical form (for duplicate detection) -----------------------
    def degree_sequence(self) -> Tuple[int, ...]:
        """Sorted degree sequence — a cheap graph invariant."""
        return tuple(sorted(self.degree(nid) for nid in self._nodes))

    def canonical_signature(self) -> Tuple:
        """A position-independent signature robust to node relabeling.

        This is a strong (not perfect) graph invariant used as the first-pass
        key for duplicate detection. It combines the sorted degree sequence with
        a sorted multiset of each edge's endpoint-degree pair, which is invariant
        under relabeling, rotation, mirroring and translation of the layout.
        Exact isomorphism confirmation for collisions is handled in
        :mod:`oneline.quality`.
        """
        edge_degree_pairs = sorted(
            tuple(sorted((self.degree(a), self.degree(b)))) for a, b in self._edges
        )
        return (
            self.node_count,
            self.edge_count,
            self.degree_sequence(),
            tuple(edge_degree_pairs),
        )

    # ---- construction helpers -------------------------------------------
    @classmethod
    def from_positions(
        cls,
        positions: Sequence[Tuple[float, float]],
        edges: Iterable[Tuple[int, int]],
    ) -> "Graph":
        nodes = [Node(i, float(x), float(y)) for i, (x, y) in enumerate(positions)]
        return cls(nodes, edges)

    def edge_set(self) -> FrozenSet[Tuple[int, int]]:
        return frozenset(self._edges)
