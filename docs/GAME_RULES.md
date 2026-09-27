# ONE LINE — Game Rules

## Core Concept

The player draws a continuous path through a graph.

The objective is to complete the puzzle according to the level's defined graph rules.

## Core Interaction

The player:

1. Starts on a valid node.
2. Drags through connected nodes.
3. Continues the path without lifting where required.
4. Must obey the level's edge/path constraints.
5. Completes the level when all required conditions are satisfied.

## Invalid Actions

The game must provide clear feedback when the player:

* moves to an invalid node;
* crosses an invalid connection;
* attempts a forbidden repeated edge;
* otherwise violates the level rules.

## Restart

The player must be able to restart the current puzzle.

Restarting must not corrupt progression.

## Completion

A completed puzzle must:

* be recognized by the gameplay engine;
* trigger completion feedback;
* record completion;
* calculate the applicable star result;
* unlock the appropriate next content.

## Stars

The game uses a three-star system.

The exact scoring algorithm must be deterministic and documented.

## Hints

Hints may be provided without monetization.

Hints must not require an internet connection.

## Offline Requirement

Core gameplay must function without network connectivity.

## Rule Authority

Any implementation must conform to this document unless this document is explicitly changed as part of an approved design decision.
