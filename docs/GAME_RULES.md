# ONE LINE — Game Rules (Canonical)

This document is the **authoritative** specification of ONE LINE gameplay.
The runtime engine (GDScript) and the tooling engine (Python) MUST both conform
to it. If code and this document disagree, follow the discrepancy procedure in
`.claude/CLAUDE.md` §5.

---

## 1. Core Concept

ONE LINE is a **one-stroke drawing puzzle** (also known as *Eulerian trail* or
*"draw without lifting the pen"*).

Each level is an **undirected graph** of **nodes** connected by **edges**. The
player draws a single continuous line that must cover **every edge exactly
once**.

## 2. Definitions

* **Node** — a point in the puzzle, with a normalized 2D position `(x, y)` where
  each coordinate is in `[0.0, 1.0]` (resolution-independent; see
  `docs/ARCHITECTURE_RULES.md`).
* **Edge** — an unordered pair of distinct node ids `{a, b}`. There is at most
  one edge between any pair of nodes (no parallel edges) and no self-loops
  (`a != b`) in schema version 1.
* **Degree** — the number of edges incident to a node.
* **Trail** — a walk that repeats no edge. The player's drawn line is a trail.

## 3. The Objective

A level is **complete** when the player's trail has traversed **every edge in the
graph exactly once**. Nodes may be visited any number of times; the objective is
defined over edges, not nodes.

## 4. Interaction

1. The player starts the line by pressing on any node.
2. The player extends the line by dragging to an **adjacent** node (a node
   connected to the current node by an **unused** edge). On release over a valid
   adjacent node, that edge becomes **used** and the current node advances.
3. The line is continuous: the next segment always begins at the current node.
4. An edge that has already been used **cannot** be used again. (Schema v1 has no
   reusable edges. The format reserves a per-edge `reusable` flag for future
   mechanics; the v1 engine treats every edge as single-use.)
5. The player may **undo** the last segment (retract the line by one edge) and
   may **restart** the level at any time.
6. The level completes the moment the last unused edge is traversed.

## 5. Valid vs. Invalid Moves

Given the current node `c`:

* **Valid move** to node `n`: an edge `{c, n}` exists AND that edge is unused.
* **Invalid move**: no edge to `n`, the edge to `n` is already used, or `n == c`.

Invalid moves must not change puzzle state and must produce immediate,
color-independent visual feedback (see `docs/GAME_RULES.md` §9 and
`docs/LEVEL_QUALITY.md`). Invalid attempts are counted for the star model.

## 6. Solvability (authoritative theorem)

A connected graph (ignoring isolated vertices, of which schema v1 has none) has
an **Eulerian trail** if and only if the number of vertices of **odd degree** is
**exactly 0 or 2**.

* 0 odd vertices → an Eulerian **circuit** exists; the trail may start at any
  node and ends where it began.
* 2 odd vertices → the trail must **start at one odd vertex and end at the
  other**.

The level validator enforces this. The solver (`tools/oneline/solver.py`) uses
**Hierholzer's algorithm** to produce an actual covering trail; a level is only
accepted if such a trail is found.

## 7. Restart & Progression

* Restarting clears the current trail but never affects saved progression.
* Completing a level records completion, computes stars (§8), and unlocks the
  next level in campaign order.
* Level 1 is unlocked on a fresh install; every other campaign level unlocks
  when its predecessor is completed.

## 8. Star Model (deterministic)

Every valid solution uses exactly `E` edges (where `E` is the edge count), so
solution *length* is constant and cannot differentiate performance. Stars are
therefore based on **mistakes** — the count of invalid move attempts plus undos
during the attempt that completed the level.

For a level with per-level thresholds `three_max_mistakes` and
`two_max_mistakes` (`three_max_mistakes <= two_max_mistakes`):

* ★☆☆ (1 star) — the level was completed. Always awarded on completion.
* ★★☆ (2 stars) — completed AND `mistakes <= two_max_mistakes`.
* ★★★ (3 stars) — completed AND `mistakes <= three_max_mistakes`.

Defaults chosen by the generator (see `tools/oneline/difficulty.py`):

* `three_max_mistakes = 0` (a clean, mistake-free solve).
* `two_max_mistakes = max(1, ceil(E / 4))`.

The star computation is pure and deterministic given `(mistakes, thresholds)`
and is unit-tested identically in Python and specified for GDScript.

The player's **best** star rating for a level is the maximum ever achieved and
is never reduced by a later, worse attempt.

## 9. Feedback Requirements

The game must clearly communicate, without relying on color alone:

* which node is the current head of the line;
* which nodes/edges have been visited/used;
* that an invalid move was attempted;
* that the level is complete.

## 10. Hints (offline, non-monetized)

A hint reveals the **next edge** of a known valid completion of the current
partial trail, computed on-device with no network, account, currency, or
purchase. A hint never solves the whole puzzle and never permanently alters it.
If the current partial trail cannot be completed (the player has walked into a
dead end), the hint system advises a restart or undo rather than fabricating a
move.

## 11. Daily Puzzle (offline, deterministic)

The Daily Puzzle is generated from a **date-based seed** combined with the
generator version. For a given date and app version the puzzle is identical. It
requires no network, server, or account; completion and streak are stored
locally. Because the puzzle depends on the generator version, changing the
generation algorithm between app versions may change historical Daily Puzzles;
this is documented and the game never claims cross-version global synchronization.

## 12. Offline Requirement

All of the above functions with no network connectivity. The game opens no
network connections during normal play.

## 13. Rule Authority

Any implementation must conform to this document unless it is explicitly changed
as part of an approved design decision, accompanied by updated tests.
