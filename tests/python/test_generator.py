import unittest

from tools.oneline.generator import GenConfig, generate_graph, generate_level
from tools.oneline.rules import trail_is_valid_solution
from tools.oneline.solver import find_eulerian_trail
from tools.oneline.validator import validate_level_dict


class TestGenerator(unittest.TestCase):
    def test_generated_graphs_are_solvable(self):
        produced = 0
        for seed in range(60):
            for n in (4, 6, 9, 12):
                g = generate_graph(seed, GenConfig(n_cells=n, extra_edge_ratio=0.4))
                if g is None:
                    continue
                produced += 1
                self.assertTrue(g.has_eulerian_trail())
                trail = find_eulerian_trail(g)
                self.assertIsNotNone(trail)
                self.assertTrue(trail_is_valid_solution(g, trail))
        self.assertGreater(produced, 100, "generator should produce many valid graphs")

    def test_determinism(self):
        cfg = GenConfig(n_cells=9, extra_edge_ratio=0.4, target_odd=2)
        a = generate_level(12345, cfg)
        b = generate_level(12345, cfg)
        self.assertIsNotNone(a)
        self.assertIsNotNone(b)
        self.assertEqual(a.to_dict(), b.to_dict())

    def test_seeds_produce_variety(self):
        # Use a non-saturating size (7 cells in a 3x3 grid) so region growth and
        # edge selection genuinely vary by seed. Assert the pool is not uniform.
        cfg = GenConfig(n_cells=7, extra_edge_ratio=0.35)
        signatures = set()
        for seed in range(8):
            lv = generate_level(seed, cfg)
            if lv is not None:
                signatures.add(tuple(lv.to_graph().canonical_signature()))
        self.assertGreater(len(signatures), 1, "generator should produce variety across seeds")

    def test_generated_level_passes_validator(self):
        lv = generate_level(777, GenConfig(n_cells=10, extra_edge_ratio=0.5))
        self.assertIsNotNone(lv)
        self.assertTrue(validate_level_dict(lv.to_dict()).ok)

    def test_target_odd_circuit(self):
        g = generate_graph(42, GenConfig(n_cells=9, target_odd=0))
        if g is not None:
            self.assertEqual(len(g.odd_degree_nodes()), 0)

    def test_target_odd_open_trail(self):
        found = False
        for seed in range(30):
            g = generate_graph(seed, GenConfig(n_cells=9, target_odd=2))
            if g is not None:
                self.assertEqual(len(g.odd_degree_nodes()), 2)
                found = True
                break
        self.assertTrue(found)


if __name__ == "__main__":
    unittest.main()
