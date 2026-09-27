# ONE LINE — Release History

Every release candidate must be traceable to a commit and a set of results
(MASTER_PROMPT §80). No entry may claim an artifact corresponds to a commit unless
verified.

## Unreleased — Release Candidate preparation (2026-09-27)

* **Status:** In development. **Not released. Not submitted. Not approved.**
* **Branch:** `claude/vibrant-planck-npmf3y`
* **App version:** 1.0.0 · **Generator:** 1.0.0 · **Schema:** 1 · **Save data:** 2
* **Engine:** Godot 4.3 stable (verified locally: `4.3.stable.official`)
* **Levels:** 210 (tutorial 3, easy 10, normal 75, advanced 70, hard 36, expert 16)
* **Verified in this environment (evidence-based):**
  * Python engine/tooling unit tests: **59 pass**.
  * Level validation: **210/210 PASS**.
  * Solver / playtester: **210/210 solved & runtime-accepted**.
  * Difficulty: monotonic, **0** discontinuities > 20.
  * Deterministic generation: regenerated campaign matches committed `index.json`.
  * GDScript: all scripts parse/compile (Godot 4.3 headless), conformance
    **23/23**, clean boot (**0** runtime errors).
* **UNVERIFIED (require display / devices / credentials):** interactive gameplay,
  visual QA, on-device touch/lifecycle, signed builds, store export, submission.

> When a build is actually produced, add a new entry above with: commit SHA,
> app/build versions, Godot version, export target, artifact hash, and QA results.
> Do not backfill fabricated results.
