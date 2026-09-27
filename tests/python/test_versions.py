"""Guard that the Python and GDScript version constants stay in sync.

Parses scripts/core/versions.gd and compares against tools/oneline/version.py so
the runtime and tooling can never silently diverge (MASTER_PROMPT §68-§69).
"""

import os
import re
import unittest

from tools.oneline.version import (
    APP_VERSION,
    GENERATOR_VERSION,
    SAVE_DATA_VERSION,
    SCHEMA_VERSION,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VERSIONS_GD = os.path.join(REPO_ROOT, "scripts", "core", "versions.gd")


def _const(text: str, name: str) -> str:
    m = re.search(rf'const\s+{name}\s*:?=\s*("?)([^"\n]+)\1', text)
    assert m, f"could not find const {name} in versions.gd"
    return m.group(2).strip()


class TestVersionSync(unittest.TestCase):
    def test_versions_match(self):
        self.assertTrue(os.path.exists(VERSIONS_GD), "versions.gd missing")
        with open(VERSIONS_GD, "r", encoding="utf-8") as fh:
            text = fh.read()
        self.assertEqual(_const(text, "APP_VERSION"), APP_VERSION)
        self.assertEqual(_const(text, "GENERATOR_VERSION"), GENERATOR_VERSION)
        self.assertEqual(int(_const(text, "SCHEMA_VERSION")), SCHEMA_VERSION)
        self.assertEqual(int(_const(text, "SAVE_DATA_VERSION")), SAVE_DATA_VERSION)


if __name__ == "__main__":
    unittest.main()
