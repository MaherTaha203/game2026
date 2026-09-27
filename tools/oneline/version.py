"""Version constants for ONE LINE.

These four version numbers are intentionally distinct (see MASTER_PROMPT §69):

* ``APP_VERSION``      — semantic product version shown to players.
* ``GENERATOR_VERSION``— bumped when level generation output can change.
* ``SCHEMA_VERSION``   — bumped when the on-disk level JSON shape changes.
* ``SAVE_DATA_VERSION``— bumped when the save-data shape changes (drives migration).

The same values are mirrored in the Godot runtime (``scripts/core/versions.gd``)
and must be kept in sync. ``tests/test_versions.py`` guards the sync where the
runtime file is present.
"""

APP_VERSION = "1.0.0"
GENERATOR_VERSION = "1.0.0"
SCHEMA_VERSION = 1
SAVE_DATA_VERSION = 2
