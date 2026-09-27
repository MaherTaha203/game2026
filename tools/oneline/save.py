"""Reference save-data model for ONE LINE (versioned, validated, migratable).

This is the *authoritative reference* for save semantics (MASTER_PROMPT §11,
§44, §70). The Godot ``SaveManager`` mirrors this shape and migration chain. The
logic here is pure and fully unit-tested so the migration/corruption behavior has
real evidence even though the mobile file I/O itself is exercised on-device.

Robustness guarantees:
* A missing save yields clean defaults.
* Corrupted / unparseable data never raises to the caller — it recovers to
  defaults and flags recovery.
* An older save is migrated forward; a newer (unknown future) save is handled
  without a crash by falling back to defaults while preserving nothing unsafe.
* Valid progress is never silently destroyed by a load of well-formed data.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple

from .version import APP_VERSION, SAVE_DATA_VERSION


def default_settings() -> Dict[str, Any]:
    return {
        "sound": True,
        "music": True,
        "haptics": True,
        "reduced_motion": False,
        "high_contrast": False,
        "language": "en",
    }


def default_stats() -> Dict[str, Any]:
    return {
        "puzzles_completed": 0,
        "total_stars": 0,
        "perfect_completions": 0,
        "current_streak": 0,
        "best_streak": 0,
        "total_play_seconds": 0,
    }


def default_daily() -> Dict[str, Any]:
    return {"last_date": None, "streak": 0, "best_streak": 0, "completed_dates": []}


def default_save() -> Dict[str, Any]:
    """A clean first-run save with level 1 unlocked (docs/GAME_RULES.md §7)."""
    return {
        "save_data_version": SAVE_DATA_VERSION,
        "app_version": APP_VERSION,
        "progress": {"unlocked_max": 1, "levels": {}},
        "settings": default_settings(),
        "stats": default_stats(),
        "daily": default_daily(),
    }


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def validate_save(data: Any) -> Tuple[bool, List[str]]:
    """Return ``(ok, errors)`` for a *current-version* save dict."""
    errors: List[str] = []
    if not isinstance(data, dict):
        return False, ["save is not an object"]
    if data.get("save_data_version") != SAVE_DATA_VERSION:
        errors.append(
            f"unexpected save_data_version: {data.get('save_data_version')}"
        )
    progress = data.get("progress")
    if not isinstance(progress, dict):
        errors.append("missing/invalid 'progress'")
    else:
        if not isinstance(progress.get("unlocked_max"), int) or progress["unlocked_max"] < 1:
            errors.append("invalid 'progress.unlocked_max'")
        if not isinstance(progress.get("levels"), dict):
            errors.append("invalid 'progress.levels'")
        else:
            for k, v in progress["levels"].items():
                if not _valid_level_record(v):
                    errors.append(f"invalid level record for {k!r}")
    for key, checker in (
        ("settings", _valid_settings),
        ("stats", _valid_stats),
        ("daily", _valid_daily),
    ):
        if not checker(data.get(key)):
            errors.append(f"missing/invalid '{key}'")
    return (len(errors) == 0), errors


def _valid_level_record(v: Any) -> bool:
    if not isinstance(v, dict):
        return False
    if not isinstance(v.get("completed"), bool):
        return False
    if not isinstance(v.get("best_stars"), int) or not (0 <= v["best_stars"] <= 3):
        return False
    if not isinstance(v.get("best_mistakes"), int) or v["best_mistakes"] < 0:
        return False
    return True


def _valid_settings(v: Any) -> bool:
    if not isinstance(v, dict):
        return False
    for k in ("sound", "music", "haptics", "reduced_motion", "high_contrast"):
        if not isinstance(v.get(k), bool):
            return False
    return isinstance(v.get("language"), str)


def _valid_stats(v: Any) -> bool:
    if not isinstance(v, dict):
        return False
    for k in default_stats():
        if not isinstance(v.get(k), int) or v[k] < 0:
            return False
    return True


def _valid_daily(v: Any) -> bool:
    if not isinstance(v, dict):
        return False
    if not (v.get("last_date") is None or isinstance(v.get("last_date"), str)):
        return False
    for k in ("streak", "best_streak"):
        if not isinstance(v.get(k), int) or v[k] < 0:
            return False
    return isinstance(v.get("completed_dates"), list)


# --------------------------------------------------------------------------
# Migration
# --------------------------------------------------------------------------
def _migrate_1_to_2(data: Dict[str, Any]) -> Dict[str, Any]:
    """v1 had no stats/daily and settings lacked haptics/reduced_motion/high_contrast."""
    data = copy.deepcopy(data)
    settings = data.get("settings")
    if not isinstance(settings, dict):
        settings = {}
    merged = default_settings()
    for k in ("sound", "music", "language"):
        if k in settings:
            merged[k] = settings[k]
    data["settings"] = merged
    data.setdefault("stats", default_stats())
    data.setdefault("daily", default_daily())
    if not isinstance(data.get("progress"), dict):
        data["progress"] = {"unlocked_max": 1, "levels": {}}
    data["save_data_version"] = 2
    return data


# Ordered chain: version N -> N+1.
_MIGRATIONS: Dict[int, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    1: _migrate_1_to_2,
}


def migrate(data: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate ``data`` up to :data:`SAVE_DATA_VERSION`.

    Raises ``ValueError`` if a required migration step is missing (caller
    decides whether to recover to defaults).
    """
    version = data.get("save_data_version")
    if not isinstance(version, int):
        raise ValueError("save_data_version missing or not an integer")
    if version > SAVE_DATA_VERSION:
        raise ValueError(f"future save version {version} > {SAVE_DATA_VERSION}")
    while version < SAVE_DATA_VERSION:
        step = _MIGRATIONS.get(version)
        if step is None:
            raise ValueError(f"no migration from version {version}")
        data = step(data)
        version = data["save_data_version"]
    return data


# --------------------------------------------------------------------------
# Loading (the resilient entry point)
# --------------------------------------------------------------------------
@dataclass
class LoadOutcome:
    """Result of a resilient load: the save plus what happened."""

    save: Dict[str, Any]
    recovered: bool          # True if defaults had to be substituted
    migrated: bool           # True if a migration ran
    note: str = ""


def load_from_string(text: str) -> LoadOutcome:
    """Resiliently load a save from raw text. Never raises."""
    if text is None or text == "":
        return LoadOutcome(default_save(), recovered=False, migrated=False, note="empty")
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return LoadOutcome(default_save(), recovered=True, migrated=False, note="corrupt json")
    if not isinstance(data, dict):
        return LoadOutcome(default_save(), recovered=True, migrated=False, note="not an object")

    migrated = False
    try:
        version = data.get("save_data_version")
        if version != SAVE_DATA_VERSION:
            data = migrate(data)
            migrated = True
    except ValueError:
        return LoadOutcome(default_save(), recovered=True, migrated=False, note="unmigratable")

    ok, _errors = validate_save(data)
    if not ok:
        # Try to preserve well-formed progress; otherwise fall back to defaults.
        salvaged = _salvage(data)
        return LoadOutcome(salvaged, recovered=True, migrated=migrated, note="salvaged")
    return LoadOutcome(data, recovered=False, migrated=migrated, note="ok")


def _salvage(data: Dict[str, Any]) -> Dict[str, Any]:
    """Best-effort recovery: keep valid level records and settings, else defaults."""
    save = default_save()
    progress = data.get("progress")
    if isinstance(progress, dict):
        levels = progress.get("levels")
        if isinstance(levels, dict):
            good: Dict[str, Any] = {}
            max_completed = 1
            for k, v in levels.items():
                if isinstance(k, str) and k.isdigit() and _valid_level_record(v):
                    good[k] = v
                    if v.get("completed"):
                        max_completed = max(max_completed, int(k) + 1)
            save["progress"]["levels"] = good
            um = progress.get("unlocked_max")
            save["progress"]["unlocked_max"] = max(
                max_completed, um if isinstance(um, int) and um >= 1 else 1
            )
    settings = data.get("settings")
    if _valid_settings(settings):
        save["settings"] = settings
    stats = data.get("stats")
    if _valid_stats(stats):
        save["stats"] = stats
    return save


def dump_to_string(save: Dict[str, Any]) -> str:
    return json.dumps(save, indent=2, sort_keys=True)


# --------------------------------------------------------------------------
# Progression helpers (pure) — mirrored in GameState.gd
# --------------------------------------------------------------------------
def record_completion(
    save: Dict[str, Any], level_id: int, stars: int, mistakes: int, total_levels: int
) -> Dict[str, Any]:
    """Apply a completion to a save (pure: returns a new dict).

    Updates best stars/mistakes (never worsens), unlocks the next level, and
    refreshes aggregate stats. ``best_stars`` is monotonic non-decreasing.
    """
    save = copy.deepcopy(save)
    key = str(level_id)
    levels = save["progress"]["levels"]
    prev = levels.get(key, {"completed": False, "best_stars": 0, "best_mistakes": None})
    new_best_stars = max(prev.get("best_stars", 0), stars)
    prev_mistakes = prev.get("best_mistakes")
    new_best_mistakes = mistakes if prev_mistakes is None else min(prev_mistakes, mistakes)
    was_completed = prev.get("completed", False)

    levels[key] = {
        "completed": True,
        "best_stars": new_best_stars,
        "best_mistakes": new_best_mistakes,
    }

    next_level = level_id + 1
    if next_level <= total_levels:
        save["progress"]["unlocked_max"] = max(
            save["progress"]["unlocked_max"], next_level
        )

    stats = save["stats"]
    if not was_completed:
        stats["puzzles_completed"] += 1
    # total_stars is the sum of best stars across levels (recomputed for safety).
    stats["total_stars"] = sum(r.get("best_stars", 0) for r in levels.values())
    stats["perfect_completions"] = sum(
        1 for r in levels.values() if r.get("best_stars", 0) == 3
    )
    return save


def is_unlocked(save: Dict[str, Any], level_id: int) -> bool:
    return level_id <= save["progress"]["unlocked_max"]
