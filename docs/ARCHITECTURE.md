# ONE LINE — Architecture (as implemented)

This describes the **actual** implementation. Governing principles are in
[`ARCHITECTURE_RULES.md`](ARCHITECTURE_RULES.md).

## Two engines, one rule set

The puzzle rules exist in exactly one authoritative specification
([`GAME_RULES.md`](GAME_RULES.md)) and two conforming implementations:

* **Python** (`tools/oneline/`) — the source of truth for tooling: generation,
  validation, solving/playtesting, difficulty and quality. It is fully unit-tested
  and runs in CI, producing real evidence that the rules behave correctly.
* **GDScript** (`scripts/core/`) — the runtime port that players actually use.
  A headless conformance suite (`tests/gdscript/run_tests.gd`) checks it against
  the same expectations, and `tests/python/test_versions.py` guards version sync.

Both consume the **same JSON level format** (`levels/*.json`), so a level
validated by the tooling is the exact data the runtime plays.

## Layers (dependency flows downward)

```
Presentation (scripts/ui, scenes/)      screens, PuzzleView rendering + input
        │  uses
State (scripts/state/game_state.gd)      current level, session, completion flow
        │  uses
Persistence (scripts/persistence)        SaveManager: versioned local save
Services (scripts/services)              AudioManager, Haptics, DailyPuzzle
        │  uses
Data (scripts/data)                      Level, LevelLoader, LevelValidator
        │  uses
Core (scripts/core)                      PuzzleGraph, PuzzleEngine, StarRules,
                                         PuzzleSolver, versions
```

Core has no dependency on presentation: the puzzle rules are testable without
rendering any UI. Presentation never owns gameplay truth — it calls `PuzzleEngine`.

## Autoloads (singletons)

Registered in `project.godot`, initialized in dependency order: `Versions`,
`Localization`, `SaveManager`, `GameState`, `AudioManager`, `Haptics`,
`ScreenManager`. Only one screen instance is alive at a time (ScreenManager frees
the previous one) to avoid handler/state accumulation across long sessions.

## Data-driven levels

Levels are JSON, never hard-coded scenes. Format (schema v1):

```json
{
  "schema_version": 1, "generator_version": "1.0.0",
  "id": 1, "name": "Level 1", "tier": "tutorial",
  "difficulty_score": 7.5, "seed": 3,
  "nodes": [{"id": 0, "x": 0.1, "y": 0.5}, ...],
  "edges": [{"a": 0, "b": 1}, ...],
  "solution_length": 3,
  "stars": {"three_max_mistakes": 0, "two_max_mistakes": 1},
  "reference_solution": [0, 1, 2, 0]
}
```

`levels/index.json` is the ordered campaign manifest read by Level Select.

## Determinism

Generation is reproducible from `(generator_version, seed, config)`; CI
regenerates the campaign and diffs `index.json` against the committed set. Star
scoring is a pure function. Four independent version numbers (app, generator,
schema, save-data) are tracked and kept in sync across languages.

## Save data

Local `user://save.json`, versioned (`save_data_version`), validated on load,
recovered on corruption, migrated forward (v1→v2 implemented), and written
atomically (temp file + rename) with a direct-write fallback. Malformed or
future-version saves never crash the game and never silently destroy valid
progress (best-effort salvage). Mirrored and unit-tested in `tools/oneline/save.py`.

## Input

`PuzzleView` handles native touch (mobile) and native mouse (desktop) directly;
pointer emulation is disabled to avoid double events. UI buttons and the puzzle
surface are separated so drawing never triggers accidental UI activation.

## Tooling (`tools/`)

`generate_levels.py` (pipeline: generate → validate → quality → dedup → curate),
`validate_levels.py`, `solve_levels.py` (playtester), `difficulty_report.py`,
`gen_audio.py` (original SFX). All are plain Python 3.11, no third-party deps.
