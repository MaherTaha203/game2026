"""Mobile-geometry gate tests (Phase 2 audit §9).

Asserts every shipped level passes the touch-friendliness/on-screen gates, and
that the gate actually rejects degenerate geometry.
"""

import glob
import os
import unittest

from tools.oneline.graph import Graph, Node
from tools.oneline.quality import (
    MIN_EDGE_LENGTH,
    MIN_NODE_DISTANCE,
    check_geometry,
)
from tools.oneline.validator import graph_from_level_dict
from tools.oneline.levelio import load_level_dict

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEVELS = sorted(glob.glob(os.path.join(REPO, "levels", "level_*.json")))


class TestGeometry(unittest.TestCase):
    def test_all_levels_pass_geometry(self):
        self.assertGreaterEqual(len(LEVELS), 200)
        bad = []
        for path in LEVELS:
            g = graph_from_level_dict(load_level_dict(path))
            ok, reasons = check_geometry(g)
            if not ok:
                bad.append((os.path.basename(path), reasons))
        self.assertEqual(bad, [], f"levels failing geometry: {bad[:5]}")

    def test_gate_rejects_too_close_nodes(self):
        g = Graph([Node(0, 0.50, 0.50), Node(1, 0.51, 0.50), Node(2, 0.9, 0.9)],
                  [(0, 1), (1, 2), (0, 2)])
        ok, reasons = check_geometry(g)
        self.assertFalse(ok)
        self.assertTrue(any("too close" in r for r in reasons))

    def test_gate_rejects_offscreen(self):
        g = Graph([Node(0, 0.0, 0.5), Node(1, 0.5, 0.5), Node(2, 0.5, 0.9)],
                  [(0, 1), (1, 2), (0, 2)])
        ok, reasons = check_geometry(g)
        self.assertFalse(ok)
        self.assertTrue(any("outside playable area" in r for r in reasons))

    def test_thresholds_reasonable(self):
        self.assertGreater(MIN_NODE_DISTANCE, 0.0)
        self.assertGreater(MIN_EDGE_LENGTH, 0.0)


if __name__ == "__main__":
    unittest.main()
