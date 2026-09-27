import unittest

from tools.oneline.graph import Graph
from tools.oneline.rules import (
    MoveResult,
    PuzzleState,
    StarThresholds,
    compute_stars,
    default_thresholds,
    trail_is_valid_solution,
)


def path_graph():
    # 0-1-2-3
    return Graph.from_positions(
        [(0, 0), (0.3, 0), (0.6, 0), (0.9, 0)], [(0, 1), (1, 2), (2, 3)]
    )


def triangle():
    return Graph.from_positions([(0, 0), (1, 0), (0.5, 1)], [(0, 1), (1, 2), (0, 2)])


class TestRules(unittest.TestCase):
    def test_start_and_valid_moves(self):
        st = PuzzleState(path_graph())
        self.assertFalse(st.started)
        self.assertEqual(st.start(0), MoveResult.OK)
        self.assertTrue(st.started)
        self.assertEqual(st.current, 0)
        self.assertEqual(st.move_to(1), MoveResult.OK)
        self.assertEqual(st.move_to(2), MoveResult.OK)
        self.assertEqual(st.move_to(3), MoveResult.OK_COMPLETED)
        self.assertTrue(st.is_complete)

    def test_invalid_no_edge(self):
        st = PuzzleState(path_graph())
        st.start(0)
        self.assertEqual(st.move_to(3), MoveResult.INVALID_NO_EDGE)
        self.assertEqual(st.mistakes, 1)
        self.assertFalse(st.is_complete)

    def test_invalid_edge_reuse(self):
        st = PuzzleState(path_graph())
        st.start(0)
        st.move_to(1)
        # Go back to 0 is a valid different edge? edge 1-0 already used -> invalid.
        self.assertEqual(st.move_to(0), MoveResult.INVALID_EDGE_USED)
        self.assertEqual(st.mistakes, 1)

    def test_invalid_same_node(self):
        st = PuzzleState(path_graph())
        st.start(0)
        self.assertEqual(st.move_to(0), MoveResult.INVALID_SAME_NODE)

    def test_undo_counts_as_mistake_and_frees_edge(self):
        st = PuzzleState(path_graph())
        st.start(0)
        st.move_to(1)
        self.assertEqual(st.used_count, 1)
        self.assertTrue(st.undo())
        self.assertEqual(st.used_count, 0)
        self.assertEqual(st.current, 0)
        self.assertEqual(st.mistakes, 1)

    def test_restart_clears_attempt(self):
        st = PuzzleState(path_graph())
        st.start(0)
        st.move_to(1)
        st.restart()
        self.assertFalse(st.started)
        self.assertEqual(st.used_count, 0)
        self.assertEqual(st.mistakes, 0)

    def test_valid_next_nodes(self):
        st = PuzzleState(triangle())
        st.start(0)
        self.assertEqual(st.valid_next_nodes(), [1, 2])
        st.move_to(1)
        self.assertEqual(st.valid_next_nodes(), [2])  # edge 0-1 now used

    def test_star_model(self):
        th = StarThresholds(three_max_mistakes=0, two_max_mistakes=2)
        self.assertEqual(compute_stars(0, th), 3)
        self.assertEqual(compute_stars(1, th), 2)
        self.assertEqual(compute_stars(2, th), 2)
        self.assertEqual(compute_stars(3, th), 1)
        self.assertEqual(compute_stars(0, th, completed=False), 0)

    def test_default_thresholds(self):
        th = default_thresholds(8)
        self.assertEqual(th.three_max_mistakes, 0)
        self.assertEqual(th.two_max_mistakes, 2)  # ceil(8/4)
        th2 = default_thresholds(3)
        self.assertEqual(th2.two_max_mistakes, 1)  # max(1, ceil(3/4))

    def test_threshold_validation(self):
        with self.assertRaises(ValueError):
            StarThresholds(three_max_mistakes=3, two_max_mistakes=1)

    def test_trail_is_valid_solution(self):
        g = triangle()
        self.assertTrue(trail_is_valid_solution(g, [0, 1, 2, 0]))
        self.assertFalse(trail_is_valid_solution(g, [0, 1, 2]))       # too short
        self.assertFalse(trail_is_valid_solution(g, [0, 2, 1, 0, 1])) # reuses edge

    def test_stars_via_state(self):
        st = PuzzleState(triangle())
        st.start(0)
        st.move_to(1)
        st.move_to(2)
        st.move_to(0)
        self.assertTrue(st.is_complete)
        self.assertEqual(st.stars(StarThresholds(0, 1)), 3)


if __name__ == "__main__":
    unittest.main()
