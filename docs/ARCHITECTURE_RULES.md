# ONE LINE — Architecture Rules

## Principle

Keep the game simple.

The architecture should support:

* maintainability;
* testing;
* deterministic behavior;
* level expansion;
* mobile performance.

## Logical Layers

The project should separate, where practical:

### Puzzle Domain

Responsible for:

* graph representation;
* path rules;
* validation;
* completion;
* scoring.

### Level Data

Responsible for:

* level definitions;
* metadata;
* difficulty;
* seeds;
* versioning.

### Level Services

Responsible for:

* loading;
* validation;
* generation;
* solver/playtesting.

### Game State

Responsible for:

* current level;
* progression;
* stars;
* settings;
* session state.

### Presentation

Responsible for:

* scenes;
* UI;
* animations;
* visual feedback;
* audio.

### Persistence

Responsible for:

* save;
* load;
* migration;
* corruption handling.

The exact implementation may differ if there is a documented reason.

## Dependency Direction

Presentation should not become the only source of gameplay truth.

Core puzzle rules should be testable without rendering the complete UI.

## Data-Driven Levels

Levels should be represented as data.

Avoid creating a unique scene for every level.

## Determinism

Generation and scoring should be deterministic when their inputs are identical.

## Extensibility

The architecture should allow the project to grow from 200 to 500+ levels without architectural redesign.

## Simplicity

Do not build infrastructure for hypothetical future requirements that are not currently needed.
