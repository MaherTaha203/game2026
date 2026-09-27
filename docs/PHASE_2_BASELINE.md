# ONE LINE — Phase 2 Baseline

Recorded before any Phase 2 changes, so fixes can be measured against it. This is
data, not a claim of correctness — Phase 2 exists to find what these numbers miss.

## Environment

* **Baseline commit:** `e4bcb3c61f05988972779d49991bc3e8005e92cb`
* **Branch:** `claude/vibrant-planck-npmf3y`
* **Git status:** clean (ignoring `.godot/`)
* **Python:** 3.11.15
* **Godot:** 4.3.stable.official (headless binary available in this environment)
* **Levels:** 210 JSON files + `index.json`

## Structure present

`project.godot`, `scenes/` (7), `scripts/` (24 `.gd`), `levels/` (210),
`tools/` (Python engine + 5 CLIs), `tests/python` (8 files, 59 tests),
`tests/gdscript/run_tests.gd`, `.github/workflows/ci.yml`.

## Baseline test results (as run)

| Suite | Result |
|---|---|
| Python unit tests | 59 pass |
| Level validation | 210/210 PASS |
| Solver / playtest | 210/210 solved & runtime-accepted (3 trivial flags = tutorials) |
| Difficulty | monotonic, 0 discontinuities > 20 |
| GDScript conformance | 23/23 |

## Claims to scrutinize in Phase 2 (not yet verified independently)

1. **Daily Puzzle** stores `last_date`/`streak`/`best_streak`/`completed_dates`,
   but does completion actually mutate them? (Suspected: no writer exists.)
2. **Hint** verified only on a triangle in conformance — unproven on all 210,
   and the GDScript solver uses bounded DFS, not the documented Hierholzer.
3. **All-210 Godot load**: only Python validated the set; the Godot `LevelLoader`
   path is unproven per-level.
4. **Level quality**: validity/solvability proven, but no mobile-geometry gates
   (node spacing, edge length, bounding box).
5. **Music setting** exists in UI/settings but no music is implemented.
6. Documentation wording (e.g. "hand-curated") vs. the reality (generated +
   algorithmic curation).

Findings and fixes are tracked in `PHASE_2_FINAL_AUDIT.md`.
