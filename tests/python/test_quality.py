import unittest

from tools.oneline.difficulty import compute_difficulty
from tools.oneline.graph import Graph
from tools.oneline.quality import DuplicateIndex, graphs_isomorphic, score_quality


def triangle(offset=0.0):
    return Graph.from_positions(
        [(0.2 + offset, 0.2), (0.8 + offset if offset == 0 else 0.8, 0.2), (0.5, 0.8)],
        [(0, 1), (1, 2), (0, 2)],
    )


class TestQuality(unittest.TestCase):
    def test_isomorphism_detects_relabeled(self):
        a = Graph.from_positions([(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 2)])
        b = Graph.from_positions([(9, 9), (5, 5), (1, 1)], [(2, 1), (1, 0)])
        self.assertTrue(graphs_isomorphic(a, b))

    def test_isomorphism_rejects_different(self):
        path = Graph.from_positions([(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 2)])
        tri = Graph.from_positions([(0, 0), (1, 0), (0.5, 1)], [(0, 1), (1, 2), (0, 2)])
        self.assertFalse(graphs_isomorphic(path, tri))

    def test_duplicate_index(self):
        idx = DuplicateIndex()
        a = Graph.from_positions([(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 2)])
        b = Graph.from_positions([(5, 5), (6, 6), (7, 7)], [(0, 1), (1, 2)])  # iso to a
        self.assertTrue(idx.add_if_new(a))
        self.assertFalse(idx.add_if_new(b))  # rejected as duplicate
        self.assertEqual(len(idx), 1)

    def test_quality_rejects_trivial_for_tier(self):
        # A large path (many edges, zero branch nodes) should be flagged above tutorial.
        n = 12
        pos = [(i / n, 0.5) for i in range(n)]
        edges = [(i, i + 1) for i in range(n - 1)]
        g = Graph.from_positions(pos, edges)
        m = compute_difficulty(g)
        q = score_quality(g, m)
        if m.tier != "tutorial":
            self.assertFalse(q.ok, q.reasons)

    def test_quality_accepts_reasonable(self):
        # 2x2 grid of squares style graph with branch points.
        pos = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]
        edges = [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]
        g = Graph.from_positions(pos, edges)
        m = compute_difficulty(g)
        q = score_quality(g, m)
        self.assertGreater(q.score, 0.0)


if __name__ == "__main__":
    unittest.main()
