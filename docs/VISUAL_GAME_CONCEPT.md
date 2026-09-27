# ONE LINE — Visual Game Concept

## 1. Purpose

A self-contained visual artifact that lets a human see and *feel* the intended
ONE LINE player experience without running the Godot project. It is built from the
**actual implemented screens and real level data**, so it doubles as a check of
the product vision against the current implementation (Phase 2 §26 "Visual Product
Concept Review").

It is **not** a screenshot of the Godot build and **not** device QA. It does not
prove App Store / Google Play readiness.

## 2. Location

* Self-contained page (viewable in any browser): `docs/visual_concept/one_line_concept.html`
* Published viewer copy (private to the owner's Claude account):
  https://claude.ai/artifact/962sn6vPys4PBzdJN9d4D5

The HTML has no external dependencies except Google Fonts and requires no build
step or Godot.

## 3. Relationship to the implementation

Every gameplay element is driven by **real data pulled from `levels/*.json`**
(levels 5, 9, 107, 206) and the interactive demo uses the **same one-stroke rules
and Hierholzer hint** as the runtime engine (`scripts/core/*`). The menus,
level-select, settings, complete and daily screens reproduce the real screen
structure and the real design tokens from `scripts/ui/style.gd` (dark palette,
accent `#6ea8fe`, star `#ffd166`, radius 14). It is an HTML *approximation* of the
Godot rendering, not a pixel-exact capture.

## 4. Design principles

Minimalist, premium, calm, puzzle-focused. One accent colour on a dark ground, a
single continuous line as the hero motif, generous spacing, large touch targets,
restrained motion. Typography: Manrope (display) + Inter (body/data). These mirror
the game's own identity rather than introducing a new look.

## 5. Screen-by-screen

| Screen | What it shows | Status |
|---|---|---|
| Main Menu | Title, Continue (when progress exists), Play, Levels, Daily, Stats, Settings | Implemented |
| Level Select | Number, star rating, locked state (glyph + dim, not colour-only), current outline | Implemented (states illustrative; structure real) |
| Gameplay | Playable one-stroke demo (level 5): drag to connect, used vs unused edges, ringed current node, undo/hint/restart | Implemented (rules real; on-device look Unverified) |
| Level Complete | "Complete!", 1–3 stars, New best, Next/Replay/Levels | Implemented |
| Daily Puzzle | Deterministic pick from the campaign + streak dots | Implemented (accurately labelled — not a newly generated graph) |
| Settings | Sound, Haptics, Reduced Motion, High Contrast, Reset — and an explicit note that there is no Music control | Implemented |
| Difficulty examples | Easy / Advanced / Expert rendered from real levels | Implemented data; difficulty labelled algorithmic |
| Themes, Level packs | Future ideas | Concept only — not implemented |

## 6. Implemented vs concept-only

* **Implemented** (real in the repo): all six core screens, the one-stroke rules,
  stars, hints, daily selection + streak, high-contrast & reduced-motion options,
  the 210 levels.
* **Concept only** (clearly badged, not in the codebase): palette themes beyond
  high-contrast, named level-pack chapters.
* **Unverified**: the exact on-device pixel rendering, animation feel, and
  performance — this HTML is an approximation, not the Godot output.

## 7. Known visual limitations

* The demo approximates rendering in SVG/HTML; the real game draws with Godot's
  canvas, so anti-aliasing, exact node sizing and animation timing will differ.
* Level-select completion/star states in the artifact are illustrative examples
  (the grid structure and rules are real; a fresh install starts with only level
  1 unlocked and no stars).
* Difficulty cards show structural complexity only; they do **not** demonstrate
  human-perceived difficulty.

## 8. What still requires real-device visual QA

Colour/contrast on real panels, touch-target sizing on 320–430px screens, safe
areas on notch / Dynamic Island devices, animation smoothness, and performance
during rapid drawing. These are tracked in `docs/DEVICE_TEST_MATRIX.md` and
`docs/HUMAN_ACTION_REQUIRED.md` and remain **UNVERIFIED**.
