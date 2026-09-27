#!/usr/bin/env python3
"""Validate every level in a directory and emit a machine-readable report.

Exit code is non-zero if any level fails, so this doubles as a CI gate
(MASTER_PROMPT §7, §24). Usage:

    python3 tools/validate_levels.py [--dir levels] [--report reports/validation_report.json]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.oneline.levelio import load_level_dict
from tools.oneline.validator import validate_level_dict


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ONE LINE levels.")
    parser.add_argument("--dir", default="levels")
    parser.add_argument("--report", default="reports/validation_report.json")
    args = parser.parse_args()

    files = sorted(glob.glob(os.path.join(args.dir, "level_*.json")))
    results = []
    failures = 0
    for path in files:
        data = load_level_dict(path)
        result = validate_level_dict(data)
        entry = result.to_dict()
        entry["file"] = os.path.basename(path)
        results.append(entry)
        if not result.ok:
            failures += 1

    report = {
        "total": len(files),
        "passed": len(files) - failures,
        "failed": failures,
        "results": results,
    }
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")

    print(f"Validated {len(files)} levels: {report['passed']} PASS, {failures} FAIL")
    if failures:
        for entry in results:
            if not entry["ok"]:
                print(f"  FAIL {entry['file']}: {entry['errors']}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
