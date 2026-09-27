---
name: puzzle-design
description: Standards for designing, validating, and curating ONE LINE puzzle levels so they are not merely solvable but suitable for a commercial puzzle game. Use when creating, generating, validating, scoring difficulty, deduplicating, or approving levels.
---

# Puzzle Design Skill

## Purpose

Ensure that ONE LINE levels are not merely solvable, but suitable for a commercial puzzle game.

## Core Requirement

Every level must be:

1. Structurally valid.
2. Solvable.
3. Playable by the real game engine.
4. Non-corrupt.
5. Appropriate for its intended difficulty.
6. Distinct enough from nearby levels.
7. Free from accidental triviality unless intentionally designed.

## Validation

Validate:

* node references;
* edge references;
* duplicate edges;
* malformed graphs;
* disconnected graphs;
* invalid starting state;
* invalid goal state;
* impossible puzzles;
* unintended repeated edges;
* malformed level metadata.

## Solver

The project should contain an automated solver/playtester.

The solver must use the same fundamental puzzle rules as the game.

For every final level, record where practical:

* level identifier;
* difficulty;
* seed;
* solution existence;
* solution length;
* validation status;
* quality status.

## Difficulty

Difficulty should increase gradually.

Avoid sudden unexplained difficulty spikes.

Suggested progression:

Tutorial
Easy
Normal
Advanced
Expert

Difficulty should consider more than node count.

Possible factors:

* branching;
* forced moves;
* ambiguity;
* backtracking pressure;
* solution length;
* graph structure;
* number of plausible incorrect paths.

## Duplicate Detection

Detect substantially duplicated levels.

Do not accept hundreds of levels that are merely cosmetic variations of the same puzzle unless intentionally part of progression.

## Final Approval

A generated level is not automatically a production level.

Generation produces candidates.

Validation determines correctness.

Quality analysis determines suitability.

Final curation determines acceptance.
