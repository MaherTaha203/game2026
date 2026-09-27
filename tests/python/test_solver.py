import unittest

from tools.oneline.graph import Graph
from tools.oneline.rules import trail_is_valid_solution
from tools.oneline.solver import count_eulerian_trails, find_eulerian_trail


class TestSolver(unittest.TestCase):
    def test_solve_path(self):
        g = Graph.from_positions([(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 2)])
        trail = find_eulerian_trail(g)
        self.assertIsNotNone(trail)
        self.assertTrue(trail_is_valid_solution(g, trail))
        self.assertEqual(len(trail), g.edge_count + 1)

    def test_solve_triangle_circuit(self):
        g = Graph.from_positions([(0, 0), (1, 0), (0.5, 1)], [(0, 1), (1, 2), (0, 2)])
        trail = find_eulerian_trail(g)
        self.assertIsNotNone(trail)
        self.assertTrue(trail_is_valid_solution(g, trail))

    def test_unsolvable_returns_none(self):
        # 4 odd vertices -> no Eulerian trail.
        g = Graph.from_positions(
            [(0, 0), (1, 0), (1, 1), (0, 1)],
            [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)],
        )
        self.assertIsNone(find_eulerian_trail(g))

    def test_determinism(self):
        g = Graph.from_positions(
            [(0, 0), (1, 0), (1, 1), (0, 1)],
            [(0, 1), (1, 2), (2, 3), (3, 0)],
        )
        self.assertEqual(find_eulerian_trail(g), find_eulerian_trail(g))

    def test_trail_count(self):
        # Triangle has multiple directed Eulerian circuits.
        g = Graph.from_positions([(0, 0), (1, 0), (0.5, 1)], [(0, 1), (1, 2), (0, 2)])
        self.assertGreaterEqual(count_eulerian_trails(g), 1)
        # Path a-b-c: one trail from each of the 2 odd endpoints (count is
        # directed and includes the reversal), so 2.
        p = Graph.from_positions([(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 2)])
        self.assertEqual(count_eulerian_trails(p), 2)


if __name__ == "__main__":
    unittest.main()
