# ONE LINE — Claude Code Project Instructions

## 1. Project Identity

Project name: ONE LINE

ONE LINE is a minimalist, premium, offline-first mobile puzzle game.

Primary platforms:

* Android
* iOS

Primary technology:

* Godot 4.x
* GDScript

The repository is the authoritative source for the game.

---

## 2. Core Product Constraints

The following are deliberate product decisions.

ONE LINE must be:

* Offline-first.
* Playable without an account.
* Playable without a backend.
* Playable without an internet connection.
* A one-time paid game.
* Free of advertisements.
* Free of subscriptions.
* Free of in-app purchases.
* Free of virtual currencies.
* Free of online multiplayer.
* Free of online leaderboards.
* Free of chat/social systems.
* Free of runtime AI.
* Free of unnecessary permissions.
* Free of unnecessary third-party services.

Do not introduce any of these features unless the project owner explicitly changes the specification.

Do not create scope creep.

---

## 3. Engineering Principles

Priorities, in order:

1. Correctness.
2. Reliability.
3. Maintainability.
4. Testability.
5. Performance.
6. User experience.
7. Visual polish.
8. Simplicity.

Prefer simple solutions over clever solutions.

Avoid unnecessary abstractions.

Avoid unnecessary dependencies.

Do not introduce a framework merely because it is popular.

Do not replace working architecture without a documented reason.

Do not rewrite large portions of the project merely for stylistic preference.

---

## 4. Repository Safety

Before changing the repository:

* Inspect the existing repository.
* Inspect Git status.
* Inspect existing branches.
* Inspect existing documentation.
* Inspect existing project configuration.
* Inspect existing tests.
* Inspect existing assets.
* Understand existing architecture.

Never assume the repository is empty.

Never delete unrelated user work.

Never overwrite unrelated files.

If an existing implementation conflicts with the specification, determine the smallest safe change.

---

## 5. Game Rule Authority

The canonical game rules are defined in:

docs/GAME_RULES.md

Do not silently change gameplay rules.

If implementation and documented rules disagree:

1. Identify the discrepancy.
2. Determine which specification is authoritative.
3. Correct the implementation or documentation.
4. Add or update a regression test.

---

## 6. Level System

Levels are data-driven.

Do not hard-code every level into individual scenes.

Every final level must pass automated structural validation.

Every final level must be solvable.

Every final level must be playable by the actual runtime game engine.

A mathematical solver alone is not sufficient evidence of runtime correctness.

Generated levels are not automatically accepted.

Generated levels require quality validation.

---

## 7. Testing Rules

Testing is mandatory.

Use:

* Unit tests.
* Integration tests.
* Level validation tests.
* Solver/playtester tests.
* Save/load tests.
* Regression tests.
* Input tests where practical.
* Build/export tests.
* Clean-install tests where possible.

Important principle:

Implemented != Tested

Tested != Mobile Verified

Generated != Quality Approved

Exported != Release Ready

Compiles != Release Ready

---

## 8. Evidence Rules

Never fabricate evidence.

Never claim:

* a test passed if it was not run;
* a device was tested if it was not tested;
* an export works if it was not successfully exported;
* a store accepted the application;
* signing works without valid credentials;
* an external service works without verification.

Use these statuses:

PASS
FAIL
UNVERIFIED
HUMAN ACTION REQUIRED

When evidence is unavailable, use UNVERIFIED.

---

## 9. Bug-Fixing Policy

When a bug is discovered:

1. Reproduce it.
2. Identify the root cause.
3. Implement the smallest appropriate fix.
4. Add or update a regression test.
5. Run the affected tests.
6. Run the broader test suite.
7. Verify that the fix did not introduce another regression.

Do not simply patch symptoms when the root cause is known.

---

## 10. Determinism

Where deterministic behavior is required, use explicit seeds and versions.

Level generation should be reproducible from:

* generator version;
* seed;
* configuration.

Build information should record where practical:

* application version;
* build number;
* Git commit;
* Godot version;
* level data version;
* save-data version.

---

## 11. Save Data

Save data must be:

* local;
* versioned;
* validated;
* resilient to corruption;
* migration-ready.

Never assume save data is always valid.

A malformed save must not permanently prevent the game from starting.

Do not silently destroy valid player progress.

---

## 12. Mobile Requirements

The game must account for:

* touch input;
* different screen sizes;
* aspect ratios;
* safe areas;
* orientation;
* lifecycle interruption;
* background/foreground transitions;
* low-memory situations;
* accidental touch interactions;
* responsive UI.

Desktop mouse input may be used for development and automated/manual QA.

---

## 13. Accessibility

Where practical, support:

* readable text;
* adequate touch targets;
* clear visual feedback;
* color-independent gameplay information;
* reduced dependence on tiny UI elements;
* sensible contrast;
* localization-ready strings.

Accessibility must not change the core puzzle rules.

---

## 14. Localization

English is the initial language.

Architecture must remain localization-ready.

Do not scatter user-visible strings unnecessarily throughout code.

Arabic should be possible to add later without redesigning the entire UI.

---

## 15. Security and Privacy

The application should collect as little data as possible.

Do not introduce:

* unnecessary telemetry;
* hidden network requests;
* analytics SDKs;
* advertising SDKs;
* unnecessary permissions;
* embedded credentials;
* API keys;
* private signing material.

Do not commit secrets.

Use placeholders for credentials where required.

---

## 16. Dependencies

Every dependency must have a reason.

Before adding a dependency:

* determine whether Godot itself can solve the problem;
* consider maintenance cost;
* consider licensing;
* consider mobile compatibility;
* consider long-term availability.

Avoid unnecessary dependencies.

---

## 17. Git Rules

Use small, logical commits.

Commit messages should explain the purpose.

Do not commit:

* generated temporary files;
* local editor caches;
* build artifacts unless explicitly required;
* credentials;
* machine-specific paths;
* personal configuration;
* unnecessary binaries.

Keep `.gitignore` appropriate for Godot and the project.

---

## 18. Documentation

Keep documentation synchronized with implementation.

Important architectural decisions should be documented.

Do not write documentation claiming features are complete when they are not verified.

---

## 19. Quality Standard

The objective is not merely to produce a playable prototype.

The objective is a small, professional, maintainable commercial game.

A feature is not complete until:

* implementation exists;
* relevant tests exist;
* tests pass;
* integration is verified;
* documentation is updated where necessary;
* known limitations are recorded.

---

## 20. Final Rule

Do not optimize for appearing complete.

Optimize for being verifiably correct.

Evidence is more important than confidence.

---

## 21. Skills and Maintenance Tasks

These additive rules complement (do not replace) the evidence, testing, and
repository-safety rules above (§4, §7, §8, §19). They exist to keep skill and
maintenance work safe and honest.

* **Read the applicable skill before performing its task.** The available skills
  are under `.claude/skills/` (game-development, puzzle-design, qa-testing,
  code-review, mobile-release, release-audit, and the Godot-specific
  godot-code-gen and godot-scene-design).
* **Do not repeat completed phases** unless explicitly requested.
* **Inspect Git status first and preserve unrelated changes** — never reset,
  stash, discard, or overwrite user or unrelated work.
* **During a skills-only or maintenance task, do not modify game logic, level
  data, save data, or release/signing configuration.** Keep the change to the
  task's scope (e.g. `.claude/` and documentation).
* **Record the exact tested commit** alongside any test evidence, and classify
  every requirement as PASS, FAIL, or UNVERIFIED (never claim a test passed
  unless it was actually executed, and never treat a partial test as proof of a
  complete requirement).
* **Never claim release readiness while mandatory criteria remain UNVERIFIED.**
* **Request authorization before destructive changes, deployment, signing,
  publishing, or any production operation** (including `git commit`/`git push`
  when the task says changes must be authorized first).
* **Do not install** unreviewed plugins, MCP servers, agents, hooks, or binaries
  just because an upstream repository recommends them; vendored skills must keep
  their upstream license and attribution.
