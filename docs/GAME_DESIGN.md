# ONE LINE — Game Design

## Concept

ONE LINE is a minimalist **one-stroke drawing** puzzle: draw a single continuous
line that covers every connection exactly once. It is calm, premium, and fully
offline — a one-time purchase with no ads, accounts, or in-app purchases.

The canonical rules are in [`GAME_RULES.md`](GAME_RULES.md). This document covers
the design intent and player-facing systems.

## Design pillars

1. **Immediate clarity** — the rule ("draw every line once") is learned by doing,
   in the first three levels, without instructional walls of text.
2. **Calm focus** — restrained motion, a single accent color, generous spacing.
3. **Fair difficulty** — a deliberate curve from tutorial to expert, no spikes.
4. **Respectful** — no monetization pressure, no data collection, works offline.

## Core loop

Select/continue → draw the solution → earn 1–3 stars → next level unlocks → repeat.
Restart and undo are always available and never cost progress.

## Difficulty & progression

Six tiers in fixed order: **tutorial → easy → normal → advanced → hard → expert**,
assigned by edge count and ordered within/between tiers by a blended difficulty
score (edges, branching, max degree, solution multiplicity, open-vs-closed trail).
The shipped campaign has a **monotonic** difficulty curve with **no discontinuity**
greater than 20 score units (verified by `tools/difficulty_report.py`).

Current composition (210 levels): tutorial 3, easy 10, normal 75, advanced 70,
hard 36, expert 16.

## Star model

All valid solutions use the same number of moves (every edge once), so stars are
based on **mistakes** (invalid attempts + undos):

* ★ complete · ★★ `mistakes ≤ two_max` · ★★★ `mistakes = 0`

Thresholds are stored per level and are deterministic. Best rating never regresses.

## Systems

* **Hint** — reveals the next edge of a valid completion of the current partial
  trail, computed on-device; never solves the whole puzzle; free, offline.
* **Daily Puzzle** — a deterministic, date-seeded selection from the validated
  campaign; offline; local streak. Historical dailies may change across app
  versions (documented; never presented as globally synchronized).
* **Statistics** — local-only lifetime figures (completed, stars, perfect,
  streaks). Never transmitted.
* **Accessibility** — high-contrast mode, reduced-motion, sound/music/haptics
  toggles, large touch targets, and state cues that never rely on color alone.

## Visual identity

Minimalist/premium, inspired by the calm clarity of products like Linear and
Apple system design: one accent color, a dark calm ground, soft rounded surfaces,
and a single continuous accent line as the hero motif (also the app icon). All
tokens live in `scripts/ui/style.gd` for a coherent look across every screen.

## Out of scope (by design — see `.claude/CLAUDE.md` §2)

Multiplayer, accounts, backend, cloud sync, ads, subscriptions, IAP, virtual
currency, chat, online leaderboards, runtime AI, analytics. Any of these would be
a separate future product decision.
