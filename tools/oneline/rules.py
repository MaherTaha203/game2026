"""Runtime trail rules for ONE LINE.

This module implements the *player-facing* rules exactly as specified in
``docs/GAME_RULES.md`` §3-§8: starting the line, extending it along unused
edges, undo, completion detection, and the deterministic star model.

The Godot ``PuzzleEngine`` (``scripts/core/puzzle_engine.gd``) is a direct port
of :class:`PuzzleState`; keeping this logic pure and framework-free is what lets
the automated solver/playtester exercise the *same* rules the player uses
(MASTER_PROMPT §64).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

from .graph import Graph, normalize_edge


class MoveResult(Enum):
    """Outcome of attempting to extend the line to a node."""

    OK = "ok"
    OK_COMPLETED = "ok_completed"
    INVALID_NO_EDGE = "invalid_no_edge"
    INVALID_EDGE_USED = "invalid_edge_used"
    INVALID_SAME_NODE = "invalid_same_node"
    INVALID_NOT_STARTED = "invalid_not_started"


@dataclass
class StarThresholds:
    """Per-level mistake thresholds used by the star model."""

    three_max_mistakes: int
    two_max_mistakes: int

    def __post_init__(self) -> None:
        if self.three_max_mistakes < 0 or self.two_max_mistakes < 0:
            raise ValueError("thresholds must be non-negative")
        if self.three_max_mistakes > self.two_max_mistakes:
            raise ValueError("three_max_mistakes must be <= two_max_mistakes")


def compute_stars(mistakes: int, thresholds: StarThresholds, completed: bool = True) -> int:
    """Pure star computation (docs/GAME_RULES.md §8).

    Returns 0 if not completed, else 1/2/3. Identical logic must exist in
    ``scripts/core/star_rules.gd``.
    """
    if not completed:
        return 0
    if mistakes <= thresholds.three_max_mistakes:
        return 3
    if mistakes <= thresholds.two_max_mistakes:
        return 2
    return 1


def default_thresholds(edge_count: int) -> StarThresholds:
    """Generator default thresholds (docs/GAME_RULES.md §8)."""
    two = max(1, math.ceil(edge_count / 4))
    return StarThresholds(three_max_mistakes=0, two_max_mistakes=two)


@dataclass
class PuzzleState:
    """Mutable in-progress solve of a single level.

    ``mistakes`` accumulates invalid move attempts plus undos, and feeds the
    star model on completion.
    """

    graph: Graph
    trail: List[int] = field(default_factory=list)          # node sequence
    used_edges: set = field(default_factory=set)            # set of normalized edges
    mistakes: int = 0

    # ---- queries ---------------------------------------------------------
    @property
    def started(self) -> bool:
        return len(self.trail) > 0

    @property
    def current(self) -> Optional[int]:
        return self.trail[-1] if self.trail else None

    @property
    def used_count(self) -> int:
        return len(self.used_edges)

    @property
    def is_complete(self) -> bool:
        return self.used_count == self.graph.edge_count and self.graph.edge_count > 0

    def can_move_to(self, node_id: int) -> MoveResult:
        """Classify a prospective move without mutating state."""
        if not self.started:
            # Starting the line: any existing node is a valid start.
            if not self.graph.has_node(node_id):
                return MoveResult.INVALID_NO_EDGE
            return MoveResult.OK
        cur = self.current
        if node_id == cur:
            return MoveResult.INVALID_SAME_NODE
        if not self.graph.has_edge(cur, node_id):
            return MoveResult.INVALID_NO_EDGE
        if normalize_edge(cur, node_id) in self.used_edges:
            return MoveResult.INVALID_EDGE_USED
        return MoveResult.OK

    def valid_next_nodes(self) -> List[int]:
        """Adjacent nodes reachable via an unused edge from the current head."""
        if not self.started:
            return sorted(self.graph.node_ids)
        cur = self.current
        result = []
        for nb in self.graph.neighbors(cur):
            if normalize_edge(cur, nb) not in self.used_edges:
                result.append(nb)
        return sorted(result)

    # ---- mutations -------------------------------------------------------
    def start(self, node_id: int) -> MoveResult:
        """Place the head of the line on ``node_id`` (only when not started)."""
        if self.started:
            # Treat as a normal move attempt.
            return self.move_to(node_id)
        if not self.graph.has_node(node_id):
            self.mistakes += 1
            return MoveResult.INVALID_NO_EDGE
        self.trail.append(node_id)
        return MoveResult.OK

    def move_to(self, node_id: int) -> MoveResult:
        """Attempt to extend the line to ``node_id``.

        Invalid attempts increment ``mistakes`` and do not change puzzle state.
        A valid move marks the edge used and advances the head; the return value
        signals completion.
        """
        result = self.can_move_to(node_id)
        if result is not MoveResult.OK:
            if result is not MoveResult.INVALID_NOT_STARTED:
                self.mistakes += 1
            return result
        if not self.started:
            self.trail.append(node_id)
            return MoveResult.OK
        cur = self.current
        self.used_edges.add(normalize_edge(cur, node_id))
        self.trail.append(node_id)
        if self.is_complete:
            return MoveResult.OK_COMPLETED
        return MoveResult.OK

    def undo(self) -> bool:
        """Retract the last segment. Counts as a mistake. Returns success."""
        if len(self.trail) < 2:
            # Nothing meaningful to undo (only the start node or empty).
            if self.started:
                self.trail.pop()
                return True
            return False
        last = self.trail.pop()
        prev = self.trail[-1]
        self.used_edges.discard(normalize_edge(prev, last))
        self.mistakes += 1
        return True

    def restart(self) -> None:
        """Clear the current attempt (does not touch persisted progression)."""
        self.trail.clear()
        self.used_edges.clear()
        self.mistakes = 0

    def stars(self, thresholds: StarThresholds) -> int:
        return compute_stars(self.mistakes, thresholds, completed=self.is_complete)


def trail_is_valid_solution(graph: Graph, trail: List[int]) -> bool:
    """Verify that ``trail`` is an Eulerian trail of ``graph``.

    Used by the solver/playtester to confirm that a computed solution is
    genuinely accepted by the runtime rules (MASTER_PROMPT §64 step 4).
    """
    if graph.edge_count == 0:
        return False
    if len(trail) != graph.edge_count + 1:
        return False
    state = PuzzleState(graph=graph)
    if not trail:
        return False
    if state.start(trail[0]) not in (MoveResult.OK, MoveResult.OK_COMPLETED):
        return False
    for node_id in trail[1:]:
        res = state.move_to(node_id)
        if res in (
            MoveResult.INVALID_NO_EDGE,
            MoveResult.INVALID_EDGE_USED,
            MoveResult.INVALID_SAME_NODE,
        ):
            return False
    return state.is_complete
