import json
import unittest

from tools.oneline.save import (
    LoadOutcome,
    default_save,
    dump_to_string,
    is_unlocked,
    load_from_string,
    migrate,
    record_completion,
    validate_save,
)
from tools.oneline.version import SAVE_DATA_VERSION


class TestSave(unittest.TestCase):
    def test_default_is_valid(self):
        ok, errors = validate_save(default_save())
        self.assertTrue(ok, errors)

    def test_missing_save_yields_defaults(self):
        out = load_from_string("")
        self.assertFalse(out.recovered)
        self.assertEqual(out.save["progress"]["unlocked_max"], 1)

    def test_corrupt_json_recovers(self):
        out = load_from_string("{not json!")
        self.assertTrue(out.recovered)
        ok, _ = validate_save(out.save)
        self.assertTrue(ok)

    def test_not_object_recovers(self):
        out = load_from_string("[1, 2, 3]")
        self.assertTrue(out.recovered)

    def test_roundtrip_current_version(self):
        save = default_save()
        save = record_completion(save, 1, stars=3, mistakes=0, total_levels=200)
        text = dump_to_string(save)
        out = load_from_string(text)
        self.assertFalse(out.recovered)
        self.assertFalse(out.migrated)
        self.assertEqual(out.save["progress"]["unlocked_max"], 2)

    def test_migration_v1_to_current(self):
        v1 = {
            "save_data_version": 1,
            "app_version": "0.9.0",
            "progress": {"unlocked_max": 3, "levels": {"1": {"completed": True, "best_stars": 2, "best_mistakes": 1}}},
            "settings": {"sound": False, "music": True, "language": "en"},
        }
        migrated = migrate(v1)
        self.assertEqual(migrated["save_data_version"], SAVE_DATA_VERSION)
        self.assertIn("stats", migrated)
        self.assertIn("daily", migrated)
        self.assertIn("haptics", migrated["settings"])
        self.assertFalse(migrated["settings"]["sound"])  # preserved
        ok, errors = validate_save(migrated)
        self.assertTrue(ok, errors)

    def test_load_string_migrates(self):
        v1_text = json.dumps({
            "save_data_version": 1,
            "app_version": "0.9.0",
            "progress": {"unlocked_max": 2, "levels": {}},
            "settings": {"sound": True, "music": True, "language": "en"},
        })
        out = load_from_string(v1_text)
        self.assertTrue(out.migrated)
        self.assertFalse(out.recovered)
        self.assertEqual(out.save["save_data_version"], SAVE_DATA_VERSION)

    def test_future_version_recovers(self):
        future = json.dumps({
            "save_data_version": SAVE_DATA_VERSION + 5,
            "progress": {"unlocked_max": 10, "levels": {}},
            "settings": {}, "stats": {}, "daily": {},
        })
        out = load_from_string(future)
        self.assertTrue(out.recovered)
        ok, _ = validate_save(out.save)
        self.assertTrue(ok)

    def test_salvage_keeps_valid_progress(self):
        # Well-formed progress but broken settings -> salvage keeps levels.
        broken = json.dumps({
            "save_data_version": SAVE_DATA_VERSION,
            "progress": {"unlocked_max": 5, "levels": {"3": {"completed": True, "best_stars": 3, "best_mistakes": 0}}},
            "settings": {"sound": "yes"},  # invalid type
            "stats": {}, "daily": {},
        })
        out = load_from_string(broken)
        self.assertTrue(out.recovered)
        self.assertIn("3", out.save["progress"]["levels"])
        self.assertGreaterEqual(out.save["progress"]["unlocked_max"], 4)

    def test_record_completion_monotonic_stars(self):
        save = default_save()
        save = record_completion(save, 1, stars=3, mistakes=0, total_levels=200)
        save = record_completion(save, 1, stars=1, mistakes=9, total_levels=200)
        self.assertEqual(save["progress"]["levels"]["1"]["best_stars"], 3)
        self.assertEqual(save["progress"]["levels"]["1"]["best_mistakes"], 0)
        # replaying does not double-count completions
        self.assertEqual(save["stats"]["puzzles_completed"], 1)

    def test_record_completion_unlocks_next(self):
        save = default_save()
        self.assertTrue(is_unlocked(save, 1))
        self.assertFalse(is_unlocked(save, 2))
        save = record_completion(save, 1, stars=2, mistakes=1, total_levels=200)
        self.assertTrue(is_unlocked(save, 2))

    def test_last_level_completion_no_overflow(self):
        save = default_save()
        save = record_completion(save, 200, stars=3, mistakes=0, total_levels=200)
        self.assertEqual(save["progress"]["unlocked_max"], 1)  # no level 201 to unlock


if __name__ == "__main__":
    unittest.main()
