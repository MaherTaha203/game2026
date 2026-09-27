#!/usr/bin/env python3
"""Automated solver / playtester for every level (MASTER_PROMPT §64).

For each level this tool:
  1. loads and structurally validates the level,
  2. computes an Eulerian trail with the solver,
  3. re-plays that trail through the *runtime rules* to prove acceptance,
  4. records solution length,
  5. flags suspiciously trivial or unusually hard levels,
and writes a machine-readable report. Exit code is non-zero if any level is
unsolvable or its computed solution is rejected by the runtime rules.

Usage:
    python3 tools/solve_levels.py [--dir levels] [--report reports/solver_report.json]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.oneline.difficulty import compute_difficulty
from tools.oneline.levelio import load_level_dict
from tools.oneline.rules import trail_is_valid_solution
from tools.oneline.solver import find_eulerian_trail
from tools.oneline.validator import graph_from_level_dict, validate_level_dict

TRIVIAL_EDGE_THRESHOLD = 3      # <= this many edges is flagged trivial
HARD_EDGE_THRESHOLD = 34        # >= this many edges is flagged very hard


def main() -> int:
    parser = argparse.ArgumentParser(description="Solve/playtest ONE LINE levels.")
    parser.add_argument("--dir", default="levels")
    parser.add_argument("--report", default="reports/solver_report.json")
    args = parser.parse_args()

    files = sorted(glob.glob(os.path.join(args.dir, "level_*.json")))
    results = []
    failures = 0
    trivial = 0
    very_hard = 0

    for path in files:
        data = load_level_dict(path)
        name = os.path.basename(path)
        entry = {"file": name, "id": data.get("id"), "tier": data.get("tier")}

        vr = validate_level_dict(data, require_solution=False)
        if not vr.ok:
            entry.update({"ok": False, "reason": "structural", "errors": vr.errors})
            results.append(entry)
            failures += 1
            continue

        graph = graph_from_level_dict(data)
        trail = find_eulerian_trail(graph)
        if trail is None:
            entry.update({"ok": False, "reason": "no_solution"})
            results.append(entry)
            failures += 1
            continue

        accepted = trail_is_valid_solution(graph, trail)
        edges = graph.edge_count
        metrics = compute_difficulty(graph)
        is_trivial = edges <= TRIVIAL_EDGE_THRESHOLD
        is_hard = edges >= HARD_EDGE_THRESHOLD
        if is_trivial:
            trivial += 1
        if is_hard:
            very_hard += 1

        entry.update({
            "ok": bool(accepted),
            "solution_length": edges,
            "runtime_accepted": bool(accepted),
            "difficulty_score": metrics.score,
            "trail_count_capped": metrics.trail_count_capped,
            "flag_trivial": is_trivial,
            "flag_very_hard": is_hard,
        })
        if not accepted:
            failures += 1
        results.append(entry)

    report = {
        "total": len(files),
        "solved": len(files) - failures,
        "failed": failures,
        "flagged_trivial": trivial,
        "flagged_very_hard": very_hard,
        "results": results,
    }
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")

    print(
        f"Playtested {len(files)} levels: {report['solved']} solved & runtime-accepted, "
        f"{failures} FAIL. Flags: trivial={trivial}, very_hard={very_hard}"
    )
    if failures:
        for e in results:
            if not e.get("ok"):
                print(f"  FAIL {e['file']}: {e.get('reason', 'rejected')}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
