# ONE LINE — Release Guide

Governing rules: [`RELEASE_RULES.md`](RELEASE_RULES.md). Human-only steps are
tracked in [`HUMAN_ACTION_REQUIRED.md`](HUMAN_ACTION_REQUIRED.md).

## Prerequisites

* **Godot 4.3** (stable), matching `project.godot`'s feature tag.
* **Godot export templates** for 4.3 (installed via the editor: *Editor → Manage
  Export Templates*).
* **Android**: Android SDK + build tools, a debug/release **keystore** (you
  provide; never committed).
* **iOS**: a macOS machine with Xcode, an Apple Developer account, signing
  certificate and provisioning profile (you provide).
* **Python 3.11** (for level tooling / CI parity).

## Clean-room rebuild (verifies portability, MASTER_PROMPT §75)

```bash
git clone <repo> && cd game2026
# 1. Level tooling (no third-party deps):
python3 -m unittest discover -s tests/python -t .
python3 tools/validate_levels.py
python3 tools/solve_levels.py
python3 tools/difficulty_report.py
# 2. Open in Godot 4.3 once to import assets (generates .godot/ and *.import):
godot --headless --editor --quit --path .
# 3. Runtime conformance:
godot --headless --path . --script tests/gdscript/run_tests.gd
```

## Regenerating levels (deterministic)

```bash
python3 tools/generate_levels.py          # writes levels/ + index.json
python3 tools/gen_audio.py                # regenerates original SFX (rarely needed)
```
Bump `GENERATOR_VERSION` in both `tools/oneline/version.py` and
`scripts/core/versions.gd` if generation output intentionally changes.

## Versioning (keep these four distinct — MASTER_PROMPT §69)

| Meaning | Location | Current |
|---|---|---|
| App version (semver) | `version.py` / `versions.gd` `APP_VERSION` | 1.0.0 |
| Generator version | `GENERATOR_VERSION` | 1.0.0 |
| Level schema version | `SCHEMA_VERSION` | 1 |
| Save-data version | `SAVE_DATA_VERSION` | 2 |
| Android version code | `export_presets.cfg` `version/code` | 1 |
| iOS build | `export_presets.cfg` `application/version` | 1 |

## Android build

1. In Godot: *Project → Export → Android*. Set your keystore (debug for testing,
   release for store) — **do not commit it**.
2. Confirm package id (`com.example.oneline` is a placeholder — change to your own).
3. Confirm portrait orientation and that no INTERNET permission is requested.
4. Export the `.aab` to `build/android/` (gitignored).
5. Run the release-build QA checklist (below) on the exported artifact.

## iOS build

1. On macOS with Xcode: *Project → Export → iOS*.
2. Set bundle identifier, team, and provisioning (yours; not committed).
3. Confirm portrait-only orientation.
4. Export and open the generated Xcode project; archive and validate in Xcode.
5. Run the release-build QA checklist on a device/simulator.

## Release-build QA checklist (MASTER_PROMPT §53)

Verify on the exported build (not just the editor): startup, menu navigation,
gameplay, completion, save/load across restarts, settings persistence, audio,
touch, performance, absence of debug UI/dev-only behavior. Record results in
`DEVICE_TEST_MATRIX.md` and `FINAL_ACCEPTANCE.md`.

## Store submission

Follow `STORE_LISTING.md` and `STORE_ASSETS.md`. Re-check current Apple/Google
requirements at submission time (they change). Record the built commit, versions,
and results in `RELEASE_HISTORY.md`.
