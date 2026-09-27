# ONE LINE

A minimalist, premium, **offline-first** one-stroke puzzle game for Android and
iOS, built with **Godot 4.x** and **GDScript**. Draw a single continuous line that
covers every connection exactly once.

One-time purchase · no ads · no subscriptions · no in-app purchases · no accounts ·
no backend · works fully offline.

## Status

Software and content complete and verified where the environment allows; store
submission and on-device QA require a human (see
[`docs/HUMAN_ACTION_REQUIRED.md`](docs/HUMAN_ACTION_REQUIRED.md) and
[`docs/FINAL_ACCEPTANCE.md`](docs/FINAL_ACCEPTANCE.md)).

Verified in CI-equivalent runs: **59** Python tests pass · **210/210** levels
validate · **210/210** solved & runtime-accepted · GDScript **23/23** conformance ·
clean headless boot. Interactive/visual/on-device and signed builds are
**UNVERIFIED** (need a display / devices / credentials).

## What the game is

The canonical rules (one-stroke / Eulerian trail, star model, hints, daily puzzle)
are in [`docs/GAME_RULES.md`](docs/GAME_RULES.md). Design intent is in
[`docs/GAME_DESIGN.md`](docs/GAME_DESIGN.md).

## Repository layout

```
project.godot            Godot 4.x project (portrait, mobile)
export_presets.cfg       Android/iOS export config (placeholders, no secrets)
scenes/                  Thin scene wrappers (Main + 6 screens)
scripts/
  core/                  PuzzleGraph, PuzzleEngine, StarRules, PuzzleSolver
  data/                  Level, LevelLoader, LevelValidator
  state/                 GameState (autoload)
  persistence/           SaveManager (autoload)
  services/              AudioManager, Haptics, DailyPuzzle
  ui/                    Style, ScreenManager, screens, PuzzleView
  i18n/                  Localization (autoload)
levels/                  210 curated JSON levels + index.json
assets/                  Original icon (SVG) + procedural SFX (WAV)
tools/                   Python engine (oneline/) + CLIs (generate/validate/solve/…)
tests/
  python/                59 unit tests (stdlib unittest)
  gdscript/              Godot headless conformance suite
docs/                    Rules, design, architecture, release, privacy, audits
.github/workflows/ci.yml CI (Python + Godot headless)
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the layered design and the
"one rule set, two engines" approach.

## How to run

Open the project in **Godot 4.3** and press Play, or headless:

```bash
godot --headless --editor --quit --path .   # first time: imports assets
godot --path .                              # run the game
```

## How to test

```bash
# Python engine, level validation, playtesting (no third-party deps):
python3 -m unittest discover -s tests/python -t .
python3 tools/validate_levels.py
python3 tools/solve_levels.py
python3 tools/difficulty_report.py

# GDScript runtime conformance (needs a Godot 4.3 binary):
godot --headless --path . --script tests/gdscript/run_tests.gd
```

## How to generate / validate levels

```bash
python3 tools/generate_levels.py        # deterministic: writes levels/ + index.json
python3 tools/validate_levels.py        # structural + solvability validation
python3 tools/solve_levels.py           # solver/playtester (runtime-rule check)
python3 tools/gen_audio.py              # regenerate original SFX
```
Generation is reproducible from `(generator version, seed, config)`; CI diffs a
fresh campaign against the committed `index.json`.

## How to export (Android / iOS)

See [`docs/RELEASE.md`](docs/RELEASE.md). You provide signing credentials (never
committed); placeholders live in `export_presets.cfg`.

## Documentation

Rules & standards: `GAME_RULES`, `ARCHITECTURE_RULES`, `TESTING_STRATEGY`,
`LEVEL_QUALITY`, `QUALITY_GATES`, `DEFINITION_OF_DONE`, `RELEASE_RULES`.
Implementation & release: `GAME_DESIGN`, `ARCHITECTURE`, `RELEASE`, `PRIVACY`,
`THIRD_PARTY_LICENSES`, `STORE_LISTING`, `STORE_ASSETS`, `DEVICE_TEST_MATRIX`,
`FINAL_ACCEPTANCE`, `RELEASE_HISTORY`, `HUMAN_ACTION_REQUIRED`.

## License / privacy

The game collects no personal data and makes no network connections; see
[`docs/PRIVACY.md`](docs/PRIVACY.md). Third-party components (Godot engine, MIT)
are audited in [`docs/THIRD_PARTY_LICENSES.md`](docs/THIRD_PARTY_LICENSES.md).
