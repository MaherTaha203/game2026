# ONE LINE — Phase 2 Final Audit

An independent audit whose goal was to *break* the project, fix real defects, and
prove the result with re-runnable evidence. Statuses are exactly
`PASS` / `FAIL` / `UNVERIFIED` / `HUMAN ACTION REQUIRED` and are never upgraded by
assumption.

## A. Baseline

* Baseline commit: `e4bcb3c` (see `PHASE_2_BASELINE.md`).
* Environment: Python 3.11.15; Godot 4.3 stable headless available; 210 levels.
* Baseline suites were green, which is exactly why this audit went looking for what
  green numbers miss.

## B. Findings

| ID | Severity | File(s) | Evidence | Impact | Fix | Verification |
|----|----------|---------|----------|--------|-----|--------------|
| F1 | **High** | `scripts/services/daily_puzzle.gd`, `game_state.gd`, `save_manager.gd`, `main_menu.gd` | No code ever wrote `daily.last_date/streak/best_streak/completed_dates`; the daily launched as a plain campaign level. | Daily Puzzle streak was permanently 0; feature effectively non-functional. | Implemented daily completion + streak logic (pure `DailyRules` + Python reference), wired `select_daily`/`complete_daily`, streak shown on completion, daily does not unlock campaign. | `test_daily.py` (11 cases A–K); GDScript conformance daily checks; commit `358bd37`. |
| F2 | Medium | `save_manager.gd`, `stats.gd` | `stats.current_streak/best_streak` had no writer. | Statistics streaks always displayed 0. | Daily completion mirrors the streak into `stats`. | `test_daily.py::test_stats_mirror`; commit `358bd37`. |
| F3 | **High** | `scripts/core/solver.gd`, `docs/ARCHITECTURE.md` | GDScript hint used bounded DFS/backtracking with a step budget, while docs claimed Hierholzer; hint correctness only ever tested on a triangle. | Risk of hint failing (budget exhaustion) on dense/expert levels; doc/impl mismatch. | Rewrote both solvers to Hierholzer (O(E)) for full solve and hint; no budget remains. | `test_hint_campaign.py` (all 210 × 4 prefixes); `campaign_test.gd` 836 hint checks; commit `88fca16`. |
| F4 | Medium | (new) `tests/gdscript/campaign_test.gd` | Only Python had validated the level set; the Godot `LevelLoader` path was unproven per level. | A level valid in Python could be broken in the runtime and go unnoticed. | Added headless all-210 runtime load+solve+replay+hint test; added to CI. | `campaign_test.gd`: 210 levels, 0 failures; commit `88fca16`. |
| F5 | Medium | `scripts/ui/puzzle_view.gd`, `tools/oneline/quality.py` | Fixed-pixel node radius could overlap on dense levels/small screens; no geometry gate. | Poor touch usability on ~320px screens; unreadable dense levels possible. | Added hard mobile-geometry gates (spacing/edge-length/bounds) to the pipeline; adaptive node/line sizing with a 24px touch floor; regenerated campaign. | `test_geometry.py` (all 210 pass; gate rejects degenerate); commit `907b4d1`. |
| F6 | Low | `scripts/ui/settings.gd`, `localization.gd`, docs | A "Music" toggle was shown for a feature that does not exist. | Misleading control (feature that does nothing). | Removed the control (kept minimal); removed music from user-facing docs. | Import/boot clean; commit `22f7e0a`. |
| F7 | Low | `docs/STORE_LISTING.md`, `GAME_DESIGN.md`, `PRIVACY.md` | "210 hand-curated levels" overstated the (generated + algorithmic) process. | Claim stronger than evidence. | Reworded to "deterministically generated, validated, deduplicated and algorithmically curated". | grep shows only self-referential mentions remain; commit `22f7e0a`. |
| F8 | Informational | `scripts/ui/*.gd` | A few user-facing strings were hardcoded (subtitle, "New best!", error). | Localization architecture bypassed for those strings. | Routed them through `Localization`. | Import/boot clean; commit `22f7e0a`. |

No `FAIL` remains open. No secrets, debug code, machine paths, or network/analytics
APIs were found in shipping code (scans in `full_audit.py`).

## C. Fixes applied

All findings above were fixed in code (not merely recommended) across commits
`358bd37`, `88fca16`, `907b4d1`, `22f7e0a`, plus this reporting commit. New tooling:
`tools/full_audit.py` (one-command re-verification) and two Godot headless test
scripts. New docs: `PHASE_2_BASELINE.md`, `ENGINE_CONFORMANCE.md`,
`VISUAL_GAME_CONCEPT.md`, this report.

## D. Tests (final, re-run)

| Test | Result | Evidence |
|------|--------|----------|
| Python unit tests | **PASS** | 77 tests OK |
| Levels — validation | **PASS** | 210/210 |
| Solver / playtest | **PASS** | 210/210 solved & runtime-accepted |
| Hints | **PASS** | Python all-levels + `campaign_test.gd` 836 checks, 0 failures |
| Daily | **PASS** | 11 Python cases + GDScript conformance |
| Save/migration/corruption | **PASS** | `test_save.py` |
| Geometry | **PASS** | `test_geometry.py`, all 210 pass |
| Difficulty progression | **PASS** | monotonic, 0 discontinuities |
| Deterministic regeneration | **PASS** | regen `index.json` matches committed |
| GDScript parse/compile | **PASS** | Godot import: 0 errors |
| GDScript conformance | **PASS** | 35/35 |
| Godot all-210 runtime load | **PASS** | `campaign_test.gd` |
| Godot boot | **PASS** | boot smoke, 0 runtime errors |
| CI | **PASS (config)** | `.github/workflows/ci.yml` fails on any of the above |

`python3 tools/full_audit.py` with Godot available: **PASS=12, FAIL=0, UNVERIFIED=0**.

## E. Remaining limitations (UNVERIFIED / HUMAN ACTION REQUIRED)

* Human playtesting / human-perceived difficulty — **UNVERIFIED**.
* Interactive gameplay feel, visual QA, animations on a real device — **UNVERIFIED**.
* Real Android device, real iPhone/iPad, safe areas on hardware — **UNVERIFIED**.
* Save-file I/O atomicity on each OS — **UNVERIFIED** (logic tested).
* App Store / Google Play submission, signing, store compliance — **HUMAN ACTION
  REQUIRED** (see `HUMAN_ACTION_REQUIRED.md`).

## F. Claims audit

Claims reduced to match evidence: "hand-curated" → "generated + algorithmically
curated"; music references removed (no music ships); the Daily Puzzle is documented
as a *deterministic pick from the campaign*, not a newly generated daily graph;
difficulty is labelled *algorithmic*, with human difficulty explicitly UNVERIFIED.
No claim of store approval, device testing, signing, or successful export is made.

## G. Final status

* Everything internally testable in this environment: **PASS** (with real evidence).
* Device/visual/human items: **UNVERIFIED**.
* Store/credentials/signing/submission: **HUMAN ACTION REQUIRED**.

The project is **not** declared "production ready": device and store requirements
remain UNVERIFIED / HUMAN ACTION REQUIRED. What can be verified in software has been,
and the evidence above is re-runnable via `python3 tools/full_audit.py`.

## VISUAL PRODUCT CONCEPT REVIEW

* **What the artifact demonstrates** — the intended look and feel across all six
  core screens plus difficulty examples, with a genuinely playable one-stroke demo
  driven by real level data and the runtime rules
  (`docs/visual_concept/one_line_concept.html`).
* **Directly corresponds to the implementation** — the six screens, one-stroke
  rules, stars, hints, daily selection + streak, high-contrast/reduced-motion, and
  the real level geometry.
* **Concept-only (badged)** — palette themes beyond high-contrast, named
  level-pack chapters.
* **Unverified** — exact on-device pixel rendering, animation feel, and
  performance; the artifact is an HTML approximation, not the Godot output and not
  device QA.
* **Discrepancies discovered** — building the artifact re-confirmed F1/F6/F7: the
  daily needed real completion recording, the music control had to go, and the
  "hand-curated" wording had to be corrected. The artifact reflects the fixed state.
