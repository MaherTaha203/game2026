"""ONE LINE — authoritative puzzle tooling package.

This package is the single source of truth for the ONE LINE puzzle rules
(see ``docs/GAME_RULES.md``). The runtime Godot/GDScript engine is a direct
port of these rules and consumes the same JSON level format produced here.

Modules:
    version     Version constants (generator / schema / save data).
    graph       Immutable graph model + structural helpers.
    rules       Runtime trail rules: move validation, completion, stars.
    validator   Structural and solvability validation of level data.
    solver      Hierholzer Eulerian-trail solver + trail counting.
    difficulty  Difficulty scoring, tiers, and star-threshold defaults.
    quality     Quality scoring and duplicate / near-duplicate detection.
    generator   Deterministic, seeded level generation.
    levelio     Level (de)serialization and schema handling.
    save        Reference save-data model with versioning + migration.
"""

from .version import (
    GENERATOR_VERSION,
    SCHEMA_VERSION,
    SAVE_DATA_VERSION,
    APP_VERSION,
)

__all__ = [
    "GENERATOR_VERSION",
    "SCHEMA_VERSION",
    "SAVE_DATA_VERSION",
    "APP_VERSION",
]
