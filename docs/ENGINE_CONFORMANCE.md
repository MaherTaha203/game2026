# ONE LINE — Engine Conformance (Python ↔ GDScript)

Two implementations of one rule set exist (`docs/ARCHITECTURE.md`). This document
is the explicit contract and records how conformance is verified. Every row is
backed by an automated test, not assertion.

## Rule contract

| Rule | Python (`tools/oneline`) | GDScript (`scripts/core`) | Verified by | Result |
|---|---|---|---|---|
| Edge normalization | `graph.normalize_edge` → `(min,max)` | `PuzzleGraph.normalize_edge` → `Vector2i(min,max)` | conformance + campaign | **PASS** |
| Edge uniqueness / no self-loop | constructor rejects | constructor skips dupes; validator rejects | `test_graph`, `test_validator`, GDScript conformance | **PASS** |
| Connectivity (ignoring isolated) | `is_connected_ignoring_isolated` | same | `test_graph`, conformance | **PASS** |
| Odd-degree vertices | `odd_degree_nodes` | same | `test_graph`, conformance | **PASS** |
| Eulerian existence (0 or 2 odd) | `has_eulerian_trail` | same | `test_graph`, conformance | **PASS** |
| Valid move / start | `PuzzleState.can_move_to` | `PuzzleEngine.can_move_to` | `test_rules`, conformance | **PASS** |
| Edge reuse forbidden | INVALID_EDGE_USED | INVALID_EDGE_USED | `test_rules`, conformance | **PASS** |
| Completion (all edges once) | `is_complete` | `is_complete` | `test_rules`, campaign replay | **PASS** |
| Undo (frees edge, counts mistake) | `undo` | `undo` | `test_rules`, conformance | **PASS** |
| Star model | `compute_stars` / `default_thresholds` | `StarRules.compute_stars` / `default_thresholds` | `test_rules`, conformance | **PASS** |
| Solve (Hierholzer) | `solver.find_eulerian_trail` | `PuzzleSolver.find_eulerian_trail` | `test_solver`, campaign | **PASS** |
| Hint completion (Hierholzer) | `solver.find_completion` | `PuzzleSolver.find_completion` | `test_hint_campaign`, campaign | **PASS** |
| Level JSON load | `levelio.Level` | `Level.from_dict` / `LevelLoader` | campaign (all 210) | **PASS** |
| Daily streak logic | `save.record_daily_completion` | `DailyRules.apply_completion` | `test_daily`, conformance | **PASS** |

## Algorithm note (audit §4)

Both engines now use **Hierholzer's algorithm** (O(E)) for the full solve *and*
for hint completion. The earlier GDScript hint used a bounded DFS/backtracking
search; this was replaced so there is no search budget that could fail on dense
or expert levels. `docs/ARCHITECTURE.md` and the solver docstrings reflect this.

## Verification evidence (re-runnable)

* **Python** — `python3 -m unittest discover -s tests/python -t .`
* **GDScript conformance** — `godot --headless --path . --script tests/gdscript/run_tests.gd`
  (pure-class rule checks, incl. daily).
* **Full campaign runtime** — `godot --headless --path . --script tests/gdscript/campaign_test.gd`
  loads all 210 levels through the runtime path, solves, replays through the
  runtime rules, and checks hints at multiple prefixes.

Latest recorded run (this environment, Godot 4.3):

```
Python: 80+ tests OK
Campaign runtime test: 210 levels, 836 hint checks, 0 failures
GDScript conformance: 35 checks, 0 failures
```

## Known conformance limitations

* The GDScript engine's *rendering and input* (PuzzleView) are not part of this
  rule contract and are verified only for parse/boot here; interactive behavior
  is **UNVERIFIED** (needs a display). See `docs/FINAL_ACCEPTANCE.md`.
* Save-file *I/O* on device (atomic rename behavior on each OS) is **UNVERIFIED**;
  the save *logic* is tested in Python and mirrored.
