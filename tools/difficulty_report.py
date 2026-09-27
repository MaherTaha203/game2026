#!/usr/bin/env python3
"""Difficulty progression report for the campaign (MASTER_PROMPT §9, §36).

Emits per-tier counts, the ordered difficulty curve, and any large
discontinuities between consecutive campaign levels.

Usage:
    python3 tools/difficulty_report.py [--dir levels] [--report reports/difficulty_report.json]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.oneline.difficulty import TIERS, compute_difficulty, tier_index
from tools.oneline.levelio import load_level_dict
from tools.oneline.validator import graph_from_level_dict

MAX_JUMP = 20.0


def main() -> int:
    parser = argparse.ArgumentParser(description="ONE LINE difficulty report.")
    parser.add_argument("--dir", default="levels")
    parser.add_argument("--report", default="reports/difficulty_report.json")
    args = parser.parse_args()

    files = sorted(glob.glob(os.path.join(args.dir, "level_*.json")))
    curve = []
    tier_counts = {t: 0 for t in TIERS}

    for path in files:
        data = load_level_dict(path)
        graph = graph_from_level_dict(data)
        m = compute_difficulty(graph)
        tier_counts[m.tier] += 1
        curve.append({
            "id": data.get("id"),
            "tier": m.tier,
            "score": m.score,
            "edges": m.edge_count,
            "nodes": m.node_count,
            "branch_nodes": m.branch_nodes,
        })

    curve.sort(key=lambda c: c["id"])
    discontinuities = []
    monotonic = True
    for i in range(1, len(curve)):
        jump = curve[i]["score"] - curve[i - 1]["score"]
        if jump > MAX_JUMP:
            discontinuities.append({
                "between": [curve[i - 1]["id"], curve[i]["id"]],
                "jump": round(jump, 2),
            })
        if tier_index(curve[i]["tier"]) < tier_index(curve[i - 1]["tier"]):
            monotonic = False

    report = {
        "total": len(files),
        "tier_counts": tier_counts,
        "tier_order_monotonic": monotonic,
        "max_jump_allowed": MAX_JUMP,
        "discontinuities": discontinuities,
        "curve": curve,
    }
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")

    print(f"Difficulty report: {len(files)} levels")
    print("  " + ", ".join(f"{t}={tier_counts[t]}" for t in TIERS))
    print(f"  tier order monotonic: {monotonic}")
    print(f"  discontinuities > {MAX_JUMP}: {len(discontinuities)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
