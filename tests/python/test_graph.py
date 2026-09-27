import unittest

from tools.oneline.graph import Graph, Node, normalize_edge


class TestGraph(unittest.TestCase):
    def test_normalize_edge(self):
        self.assertEqual(normalize_edge(2, 5), (2, 5))
        self.assertEqual(normalize_edge(5, 2), (2, 5))
        with self.assertRaises(ValueError):
            normalize_edge(3, 3)

    def test_duplicate_node_rejected(self):
        with self.assertRaises(ValueError):
            Graph([Node(0, 0, 0), Node(0, 1, 1)], [])

    def test_duplicate_edge_rejected(self):
        with self.assertRaises(ValueError):
            Graph([Node(0, 0, 0), Node(1, 1, 1)], [(0, 1), (1, 0)])

    def test_edge_unknown_node_rejected(self):
        with self.assertRaises(ValueError):
            Graph([Node(0, 0, 0), Node(1, 1, 1)], [(0, 2)])

    def test_degree_and_neighbors(self):
        g = Graph.from_positions([(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 2)])
        self.assertEqual(g.degree(1), 2)
        self.assertEqual(g.degree(0), 1)
        self.assertEqual(g.neighbors(1), {0, 2})
        self.assertEqual(g.max_degree(), 2)

    def test_connectivity(self):
        connected = Graph.from_positions([(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 2)])
        self.assertTrue(connected.is_connected_ignoring_isolated())
        disconnected = Graph.from_positions(
            [(0, 0), (1, 0), (2, 0), (3, 0)], [(0, 1), (2, 3)]
        )
        self.assertFalse(disconnected.is_connected_ignoring_isolated())

    def test_odd_degree_and_eulerian(self):
        # Path a-b-c: endpoints odd (0 and 2), b even -> Eulerian trail exists.
        path = Graph.from_positions([(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 2)])
        self.assertEqual(path.odd_degree_nodes(), [0, 2])
        self.assertTrue(path.has_eulerian_trail())

        # Triangle: all degree 2 -> Eulerian circuit.
        tri = Graph.from_positions([(0, 0), (1, 0), (0, 1)], [(0, 1), (1, 2), (0, 2)])
        self.assertEqual(tri.odd_degree_nodes(), [])
        self.assertTrue(tri.has_eulerian_trail())

    def test_no_eulerian_when_four_odd(self):
        # Star with 3 leaves + center: leaves degree1 (odd x3), center degree3 (odd)
        # -> 4 odd vertices -> no Eulerian trail.
        star = Graph.from_positions(
            [(0.5, 0.5), (0, 0), (1, 0), (0.5, 1)], [(0, 1), (0, 2), (0, 3)]
        )
        self.assertEqual(len(star.odd_degree_nodes()), 4)
        self.assertFalse(star.has_eulerian_trail())

    def test_canonical_signature_relabel_invariant(self):
        a = Graph.from_positions([(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 2)])
        # Same path, different ids/positions (mirrored/translated).
        b = Graph([Node(5, 9, 9), Node(7, 8, 8), Node(9, 7, 7)], [(5, 7), (7, 9)])
        self.assertEqual(a.canonical_signature(), b.canonical_signature())


if __name__ == "__main__":
    unittest.main()
