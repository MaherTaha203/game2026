import unittest

from tools.oneline.validator import validate_level_dict


def base_level(nodes, edges, **extra):
    data = {
        "id": 1,
        "nodes": [{"id": i, "x": x, "y": y} for i, (x, y) in enumerate(nodes)],
        "edges": [{"a": a, "b": b} for (a, b) in edges],
    }
    data.update(extra)
    return data


class TestValidator(unittest.TestCase):
    def test_valid_triangle(self):
        d = base_level([(0.2, 0.2), (0.8, 0.2), (0.5, 0.8)], [(0, 1), (1, 2), (0, 2)])
        r = validate_level_dict(d)
        self.assertTrue(r.ok, r.errors)
        self.assertEqual(r.solution_length, 3)

    def test_disconnected(self):
        d = base_level(
            [(0.1, 0.1), (0.2, 0.1), (0.8, 0.8), (0.9, 0.8)], [(0, 1), (2, 3)]
        )
        r = validate_level_dict(d)
        self.assertFalse(r.ok)
        self.assertTrue(any("disconnected" in e for e in r.errors))

    def test_unknown_node_reference(self):
        d = base_level([(0.1, 0.1), (0.2, 0.1)], [(0, 5)])
        r = validate_level_dict(d)
        self.assertFalse(r.ok)
        self.assertTrue(any("unknown node" in e for e in r.errors))

    def test_duplicate_edge(self):
        d = base_level([(0.1, 0.1), (0.2, 0.1)], [(0, 1), (1, 0)])
        r = validate_level_dict(d)
        self.assertFalse(r.ok)
        self.assertTrue(any("duplicate edge" in e for e in r.errors))

    def test_self_loop(self):
        d = base_level([(0.1, 0.1), (0.2, 0.1)], [(0, 0), (0, 1)])
        r = validate_level_dict(d)
        self.assertFalse(r.ok)
        self.assertTrue(any("self-loop" in e for e in r.errors))

    def test_no_eulerian_trail_four_odd(self):
        # Square with both diagonals: 4 corners degree 3 -> 4 odd vertices.
        d = base_level(
            [(0.1, 0.1), (0.9, 0.1), (0.9, 0.9), (0.1, 0.9)],
            [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)],
        )
        r = validate_level_dict(d)
        self.assertFalse(r.ok)
        self.assertTrue(any("Eulerian" in e for e in r.errors))

    def test_position_out_of_range(self):
        d = base_level([(0.1, 0.1), (1.5, 0.1)], [(0, 1)])
        r = validate_level_dict(d)
        self.assertFalse(r.ok)
        self.assertTrue(any("out of range" in e for e in r.errors))

    def test_malformed_missing_lists(self):
        r = validate_level_dict({"id": 1, "nodes": "x", "edges": []})
        self.assertFalse(r.ok)

    def test_stored_solution_length_mismatch(self):
        d = base_level(
            [(0.2, 0.2), (0.8, 0.2), (0.5, 0.8)],
            [(0, 1), (1, 2), (0, 2)],
            solution_length=99,
        )
        r = validate_level_dict(d)
        self.assertFalse(r.ok)
        self.assertTrue(any("solution_length" in e for e in r.errors))


if __name__ == "__main__":
    unittest.main()
