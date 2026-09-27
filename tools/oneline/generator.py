"""Deterministic, seeded level generation for ONE LINE.

Given the same ``(generator_version, seed, config)`` the generator produces the
identical level (MASTER_PROMPT §67). Every generated level is guaranteed to have
an Eulerian trail: we build a connected graph, then repair vertex parity so that
the number of odd-degree vertices is exactly 0 or 2.

Layout uses a randomized connected grid region so edges are short and readable;
parity repair may add a small number of longer connectors, which is normal for
one-stroke puzzles.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from .graph import Graph, Node, normalize_edge
from .difficulty import compute_difficulty
from .rules import default_thresholds
from .solver import find_eulerian_trail
from .validator import validate_level_dict
from .levelio import Level
from .version import GENERATOR_VERSION


@dataclass
class GenConfig:
    """Size/shape controls for a single generation attempt."""

    n_cells: int
    extra_edge_ratio: float = 0.35
    allow_diagonal: bool = False
    target_odd: int = 0  # 0 -> circuit, 2 -> open trail


Cell = Tuple[int, int]


def _grow_region(rng: random.Random, n_cells: int, cols: int, rows: int) -> List[Cell]:
    """Grow a randomized connected orthogonal polyomino of ``n_cells`` cells."""
    start = (rng.randrange(cols), rng.randrange(rows))
    chosen: Set[Cell] = {start}
    frontier: List[Cell] = _ortho_neighbors(start, cols, rows)
    while len(chosen) < n_cells and frontier:
        idx = rng.randrange(len(frontier))
        cell = frontier.pop(idx)
        if cell in chosen:
            continue
        chosen.add(cell)
        for nb in _ortho_neighbors(cell, cols, rows):
            if nb not in chosen:
                frontier.append(nb)
    return sorted(chosen)


def _ortho_neighbors(cell: Cell, cols: int, rows: int) -> List[Cell]:
    x, y = cell
    result = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < cols and 0 <= ny < rows:
            result.append((nx, ny))
    return result


def _all_neighbors(cell: Cell, cols: int, rows: int, diagonal: bool) -> List[Cell]:
    deltas = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if diagonal:
        deltas += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    x, y = cell
    out = []
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if 0 <= nx < cols and 0 <= ny < rows:
            out.append((nx, ny))
    return out


class _UnionFind:
    def __init__(self, items):
        self.parent = {i: i for i in items}

    def find(self, a):
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a

    def union(self, a, b) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        self.parent[ra] = rb
        return True


def _spanning_tree(rng: random.Random, node_ids, candidate_edges):
    """Randomized Kruskal spanning tree over candidate edges."""
    edges = list(candidate_edges)
    rng.shuffle(edges)
    uf = _UnionFind(node_ids)
    tree: List[Tuple[int, int]] = []
    for a, b in edges:
        if uf.union(a, b):
            tree.append(normalize_edge(a, b))
    return tree


def _positions_from_cells(
    cells: List[Cell], cols: int, rows: int, rng: random.Random
) -> List[Tuple[float, float]]:
    """Map grid cells to normalized [0.1, 0.9] positions with light jitter."""
    positions = []
    span = max(cols - 1, 1), max(rows - 1, 1)
    jitter = 0.02
    for (cx, cy) in cells:
        px = 0.1 + 0.8 * (cx / span[0]) + rng.uniform(-jitter, jitter)
        py = 0.1 + 0.8 * (cy / span[1]) + rng.uniform(-jitter, jitter)
        positions.append((min(0.95, max(0.05, px)), min(0.95, max(0.05, py))))
    return positions


def _repair_parity(
    rng: random.Random,
    node_pos: Dict[int, Tuple[float, float]],
    edges: Set[Tuple[int, int]],
    target_odd: int,
    next_id: int,
) -> int:
    """Mutate ``edges``/``node_pos`` so odd-degree count == target_odd.

    Returns the updated ``next_id`` after any midpoint nodes were inserted.
    """

    def degree_of(nid: int) -> int:
        return sum(1 for e in edges if nid in e)

    def odd_nodes() -> List[int]:
        return sorted(n for n in node_pos if degree_of(n) % 2 == 1)

    odds = odd_nodes()
    while len(odds) > target_odd:
        u = odds[0]
        # Prefer pairing with an odd node not already directly connected.
        partner = None
        for v in odds[1:]:
            if normalize_edge(u, v) not in edges:
                partner = v
                break
        if partner is not None:
            edges.add(normalize_edge(u, partner))
        else:
            # All other odds already adjacent to u: insert a midpoint node.
            v = odds[1]
            w = next_id
            next_id += 1
            ux, uy = node_pos[u]
            vx, vy = node_pos[v]
            node_pos[w] = (
                min(0.95, max(0.05, (ux + vx) / 2 + rng.uniform(-0.03, 0.03))),
                min(0.95, max(0.05, (uy + vy) / 2 + rng.uniform(-0.03, 0.03))),
            )
            edges.add(normalize_edge(u, w))
            edges.add(normalize_edge(w, v))
        odds = odd_nodes()
    return next_id


def generate_graph(seed: int, config: GenConfig) -> Optional[Graph]:
    """Generate a validated, Eulerian graph or ``None`` on rare failure."""
    # Seeding with a deterministic string keeps generation reproducible across
    # processes (str seeds are hashed deterministically by random, unlike the
    # process-randomized builtin hash()).
    rng = random.Random(f"{GENERATOR_VERSION}|{config.n_cells}|{config.target_odd}|{seed}")
    n = max(3, config.n_cells)
    cols = max(2, math.ceil(math.sqrt(n)))
    rows = max(2, math.ceil(n / cols))

    cells = _grow_region(rng, n, cols, rows)
    if len(cells) < 3:
        return None

    cell_to_id = {cell: i for i, cell in enumerate(cells)}
    node_ids = list(cell_to_id.values())

    # Candidate edges from grid adjacency among selected cells.
    candidate: Set[Tuple[int, int]] = set()
    cell_set = set(cells)
    for cell in cells:
        for nb in _all_neighbors(cell, cols, rows, config.allow_diagonal):
            if nb in cell_set:
                candidate.add(normalize_edge(cell_to_id[cell], cell_to_id[nb]))

    tree = _spanning_tree(rng, node_ids, candidate)
    edges: Set[Tuple[int, int]] = set(tree)

    remaining = [e for e in candidate if e not in edges]
    rng.shuffle(remaining)
    extra_count = int(round(config.extra_edge_ratio * len(tree)))
    for e in remaining[:extra_count]:
        edges.add(e)

    positions = _positions_from_cells(cells, cols, rows, rng)
    node_pos: Dict[int, Tuple[float, float]] = {i: positions[i] for i in node_ids}

    next_id = _repair_parity(rng, node_pos, edges, config.target_odd, len(node_ids))

    nodes = [Node(nid, node_pos[nid][0], node_pos[nid][1]) for nid in sorted(node_pos)]
    try:
        graph = Graph(nodes, edges)
    except ValueError:
        return None
    if not graph.has_eulerian_trail():
        return None
    return graph


def generate_level(seed: int, config: GenConfig) -> Optional[Level]:
    """Generate a fully specified, self-validated :class:`Level` (id = 0).

    The caller assigns the final campaign id during curation.
    """
    graph = generate_graph(seed, config)
    if graph is None:
        return None

    solution = find_eulerian_trail(graph)
    if solution is None:
        return None

    metrics = compute_difficulty(graph)
    thresholds = default_thresholds(graph.edge_count)

    level = Level(
        id=0,
        nodes=graph.nodes,
        edges=graph.edges,
        tier=metrics.tier,
        difficulty_score=metrics.score,
        seed=seed,
        solution_length=graph.edge_count,
        star_thresholds=thresholds,
        reference_solution=solution,
    )

    # Self-check: the emitted dict must pass the shared validator.
    result = validate_level_dict(level.to_dict())
    if not result.ok:
        return None
    return level
