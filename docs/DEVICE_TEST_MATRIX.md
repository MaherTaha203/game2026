# ONE LINE — Device Test Matrix

Tracks **actual** testing separately from assumed compatibility (MASTER_PROMPT §72).
Status values: **Tested / Failed / Unverified**. A category is only "Tested" with
real evidence (device or documented run).

_As of 2026-09-27, no physical devices and no display were available in the build
environment, so on-device categories are **Unverified**. Desktop headless checks
that were actually run are marked Tested with their evidence._

## Desktop / CI (headless)

| Environment | Check | Status | Evidence |
|---|---|---|---|
| Linux headless (Godot 4.3) | Project imports, all scripts parse | **Tested** | CI `godot-runtime` import step; 0 errors |
| Linux headless (Godot 4.3) | Core rules conformance | **Tested** | `tests/gdscript/run_tests.gd` 23/23 |
| Linux headless (Godot 4.3) | Boot (autoloads + menu) no errors | **Tested** | boot smoke test, 0 errors |
| Linux (Python 3.11) | Engine/save/generator tests | **Tested** | 59 unit tests pass |
| Linux (Python 3.11) | 210 levels validate + solve | **Tested** | validator/solver reports, 210/210 |
| Desktop with display | Mouse interaction, full playthrough | **Unverified** | needs a display |

## Android

| Category | Status | Notes |
|---|---|---|
| Small screen | Unverified | needs device/emulator + build |
| Standard screen | Unverified | |
| Large screen / tablet | Unverified | |
| High-density display | Unverified | |
| Gesture navigation / safe areas | Unverified | safe-area handling implemented; needs on-device check |
| Signed release build | Unverified | requires keystore (HUMAN ACTION) |

## iOS

| Category | Status | Notes |
|---|---|---|
| Smaller iPhone | Unverified | needs macOS + device/simulator |
| Standard iPhone | Unverified | |
| Large iPhone | Unverified | |
| Notch / Dynamic Island | Unverified | safe-area handling implemented; needs on-device check |
| Signed build | Unverified | requires Apple credentials (HUMAN ACTION) |

## How to fill this in

Run the release build per `RELEASE.md`, exercise the QA sequences in
`qa-testing` skill and `TESTING_STRATEGY.md` on each device, and update the
status + evidence columns. Do not mark a row Tested without evidence.
