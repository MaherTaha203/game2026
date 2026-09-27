#!/usr/bin/env python3
"""Generate the curated ONE LINE campaign.

Pipeline (docs/LEVEL_QUALITY.md, MASTER_PROMPT §5-§6, §35-§36):

    generate candidates -> validate -> quality-score -> de-duplicate
    -> bucket by difficulty tier -> curate an intentional progression
    -> assign campaign ids -> write levels/ + index.json

The process is fully deterministic (fixed seed sweeps), so re-running produces
the same campaign for a given generator version.

Design note: the smallest tiers (tutorial/early-easy) are intentionally small
because only a handful of *structurally distinct* puzzles exist at 2-3 edges;
the campaign draws its bulk from the structurally-rich normal/advanced/hard
tiers. Every level in the campaign is a distinct puzzle (isomorphism-deduped).

Usage:
    python3 tools/generate_levels.py [--count 210] [--out levels]
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, List

# Allow running as a script from the repo root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.oneline.difficulty import TIERS, compute_difficulty, tier_index
from tools.oneline.generator import GenConfig, generate_level
from tools.oneline.levelio import Level, level_filename, save_level, write_index
from tools.oneline.quality import DuplicateIndex, score_quality
from tools.oneline.validator import validate_level_dict

# Desired campaign distribution (sums to > 200 with headroom). Curation adapts
# to actual supply and tops up from richer tiers if a lean tier underfills.
DESIRED: Dict[str, int] = {
    "tutorial": 3,
    "easy": 10,
    "normal": 75,
    "advanced": 70,
    "hard": 36,
    "expert": 16,
}

MIN_TOTAL = 200

# Per-tier collection cap: enough headroom to pick the best by score, but bounded
# so one tier can't exhaust the run before the large-graph sweep reaches
# hard/expert. Lean tiers keep a high cap since they are supply-limited anyway.
def _tier_cap(tier: str) -> int:
    return max(DESIRED.get(tier, 0) * 3, DESIRED.get(tier, 0) + 40)

# Generation sweep: (cell-count range, extra ratios, diagonal, target_odds, seeds).
SWEEP = [
    (range(3, 5), [0.0, 0.3], False, [0, 2], range(0, 60)),
    (range(5, 8), [0.25, 0.45], False, [0, 2], range(0, 160)),
    (range(8, 12), [0.35, 0.55], False, [0, 2], range(0, 320)),
    (range(11, 16), [0.45, 0.65], True, [0, 2], range(0, 360)),
    (range(16, 26), [0.6, 0.85], True, [0, 2], range(0, 320)),
]


def build_pool() -> Dict[str, List[Level]]:
    """Generate, validate, quality-filter and de-duplicate a distinct pool."""
    dedup = DuplicateIndex()
    buckets: Dict[str, List[Level]] = {t: [] for t in TIERS}
    caps = {t: _tier_cap(t) for t in TIERS}

    for cells, ratios, diagonal, odds, seeds in SWEEP:
        for n in cells:
            for ratio in ratios:
                for target_odd in odds:
                    for seed in seeds:
                        if all(len(buckets[t]) >= caps[t] for t in TIERS):
                            return buckets
                        cfg = GenConfig(
                            n_cells=n,
                            extra_edge_ratio=ratio,
                            allow_diagonal=diagonal,
                            target_odd=target_odd,
                        )
                        lv = generate_level(seed, cfg)
                        if lv is None:
                            continue
                        graph = lv.to_graph()
                        metrics = compute_difficulty(graph)
                        if len(buckets[metrics.tier]) >= caps[metrics.tier]:
                            continue
                        quality = score_quality(graph, metrics)
                        if not quality.ok:
                            continue
                        if not dedup.add_if_new(graph):
                            continue
                        if not validate_level_dict(lv.to_dict()).ok:
                            continue
                        buckets[metrics.tier].append(lv)
    return buckets


def curate(buckets: Dict[str, List[Level]], target_total: int) -> List[Level]:
    """Compose a smooth campaign: desired per-tier counts, topped up to target.

    Within a tier levels are ordered by ascending difficulty score; the final
    campaign is sorted by (tier, score) so difficulty rises monotonically.
    """
    chosen: List[Level] = []
    for tier in TIERS:
        pool = sorted(buckets[tier], key=lambda lv: lv.difficulty_score)
        take = min(DESIRED.get(tier, 0), len(pool))
        chosen.extend(pool[:take])

    # Top up from richest tiers (normal -> advanced -> hard -> expert -> easy).
    if len(chosen) < target_total:
        chosen_ids = {id(lv) for lv in chosen}
        for tier in ("normal", "advanced", "hard", "expert", "easy", "tutorial"):
            if len(chosen) >= target_total:
                break
            pool = sorted(buckets[tier], key=lambda lv: lv.difficulty_score)
            for lv in pool:
                if id(lv) in chosen_ids:
                    continue
                chosen.append(lv)
                chosen_ids.add(id(lv))
                if len(chosen) >= target_total:
                    break

    chosen.sort(key=lambda lv: (tier_index(lv.tier), lv.difficulty_score))
    return chosen


def check_progression(levels: List[Level]) -> List[str]:
    """Flag large difficulty discontinuities between consecutive levels."""
    warnings: List[str] = []
    max_jump = 20.0
    for i in range(1, len(levels)):
        jump = levels[i].difficulty_score - levels[i - 1].difficulty_score
        if jump > max_jump:
            warnings.append(
                f"difficulty jump {jump:.1f} between campaign #{i} and #{i + 1} "
                f"({levels[i - 1].tier}->{levels[i].tier})"
            )
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the ONE LINE campaign.")
    parser.add_argument("--count", type=int, default=sum(DESIRED.values()))
    parser.add_argument("--out", default="levels")
    args = parser.parse_args()

    print("Generating candidate pool...", flush=True)
    buckets = build_pool()
    for tier in TIERS:
        print(f"  {tier:9s}: {len(buckets[tier])} distinct")

    campaign = curate(buckets, args.count)
    total = len(campaign)
    print(f"Curated campaign: {total} levels")

    if total < MIN_TOTAL:
        print(f"ERROR: only {total} levels curated (need >= {MIN_TOTAL}).", file=sys.stderr)
        return 1

    out_dir = args.out
    os.makedirs(out_dir, exist_ok=True)
    # Clear any previous generation to avoid stale files.
    for existing in os.listdir(out_dir):
        if existing.startswith("level_") and existing.endswith(".json"):
            os.remove(os.path.join(out_dir, existing))

    for i, lv in enumerate(campaign, start=1):
        lv.id = i
        lv.name = f"Level {i}"
        save_level(lv, os.path.join(out_dir, level_filename(i)))
    write_index(campaign, os.path.join(out_dir, "index.json"))

    # Report per-tier composition of the final campaign.
    comp: Dict[str, int] = {t: 0 for t in TIERS}
    for lv in campaign:
        comp[lv.tier] += 1
    print("Final composition:", ", ".join(f"{t}={comp[t]}" for t in TIERS))

    warnings = check_progression(campaign)
    if warnings:
        print(f"Progression warnings ({len(warnings)}):")
        for w in warnings[:10]:
            print(f"  - {w}")
    else:
        print("Progression: smooth (no discontinuity > 20 score units).")

    print(f"Wrote {total} levels to {out_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
