"""Daily Puzzle streak/completion tests (Phase 2 audit §2, cases A-K).

These exercise the pure reference logic in tools/oneline/save.py, which the
GDScript SaveManager mirrors. The deterministic *selection* of the daily level is
tested separately (it is a pure function of date + generator version).
"""

import unittest

from tools.oneline.save import (
    daily_already_completed,
    default_save,
    record_daily_completion,
    validate_save,
    load_from_string,
    dump_to_string,
    _is_consecutive,
)


class TestDailyStreak(unittest.TestCase):
    def test_consecutive_helper(self):
        self.assertTrue(_is_consecutive("2026-09-25", "2026-09-26"))
        self.assertFalse(_is_consecutive("2026-09-25", "2026-09-27"))
        self.assertFalse(_is_consecutive("2026-09-25", "2026-09-25"))
        self.assertFalse(_is_consecutive("2026-09-25", "2026-09-24"))  # backward
        self.assertTrue(_is_consecutive("2026-02-28", "2026-03-01"))   # month roll

    def test_C_D_E_completion_records_and_streak_builds(self):
        # C: completion recorded; D: completed_dates updated; E: streak counts.
        s = default_save()
        s = record_daily_completion(s, "2026-09-25")
        s = record_daily_completion(s, "2026-09-26")
        s = record_daily_completion(s, "2026-09-27")
        self.assertEqual(s["daily"]["streak"], 3)
        self.assertEqual(s["daily"]["last_date"], "2026-09-27")
        self.assertEqual(
            s["daily"]["completed_dates"], ["2026-09-25", "2026-09-26", "2026-09-27"]
        )

    def test_E_gap_breaks_streak(self):
        s = default_save()
        s = record_daily_completion(s, "2026-09-25")
        s = record_daily_completion(s, "2026-09-27")  # skipped the 26th
        self.assertEqual(s["daily"]["streak"], 1)

    def test_F_best_streak_preserved(self):
        s = default_save()
        for d in ["2026-09-25", "2026-09-26", "2026-09-27"]:
            s = record_daily_completion(s, d)
        self.assertEqual(s["daily"]["best_streak"], 3)
        s = record_daily_completion(s, "2026-09-30")  # gap resets current to 1
        self.assertEqual(s["daily"]["streak"], 1)
        self.assertEqual(s["daily"]["best_streak"], 3)  # best kept

    def test_G_reopen_same_day_no_double(self):
        s = default_save()
        s = record_daily_completion(s, "2026-09-27")
        self.assertTrue(daily_already_completed(s, "2026-09-27"))
        s2 = record_daily_completion(s, "2026-09-27")  # same day again
        self.assertEqual(s2["daily"]["streak"], 1)
        self.assertEqual(len(s2["daily"]["completed_dates"]), 1)

    def test_H_replay_same_day_no_streak_bump(self):
        s = default_save()
        s = record_daily_completion(s, "2026-09-26")
        s = record_daily_completion(s, "2026-09-27")
        streak_before = s["daily"]["streak"]
        s = record_daily_completion(s, "2026-09-27")  # replay
        self.assertEqual(s["daily"]["streak"], streak_before)

    def test_I_backward_date_resets_not_crashes(self):
        s = default_save()
        s = record_daily_completion(s, "2026-09-27")
        s = record_daily_completion(s, "2026-09-20")  # clock moved back
        self.assertEqual(s["daily"]["streak"], 1)
        ok, _ = validate_save(s)
        self.assertTrue(ok)

    def test_J_persists_through_save_roundtrip(self):
        s = default_save()
        s = record_daily_completion(s, "2026-09-26")
        s = record_daily_completion(s, "2026-09-27")
        out = load_from_string(dump_to_string(s))
        self.assertFalse(out.recovered)
        self.assertEqual(out.save["daily"]["streak"], 2)
        self.assertEqual(out.save["daily"]["completed_dates"], ["2026-09-26", "2026-09-27"])

    def test_stats_mirror(self):
        s = default_save()
        s = record_daily_completion(s, "2026-09-26")
        s = record_daily_completion(s, "2026-09-27")
        self.assertEqual(s["stats"]["current_streak"], 2)
        self.assertEqual(s["stats"]["best_streak"], 2)

    def test_completion_does_not_unlock_campaign(self):
        s = default_save()
        before = s["progress"]["unlocked_max"]
        s = record_daily_completion(s, "2026-09-27")
        self.assertEqual(s["progress"]["unlocked_max"], before)

    def test_result_is_valid_save(self):
        s = default_save()
        s = record_daily_completion(s, "2026-09-27")
        ok, errors = validate_save(s)
        self.assertTrue(ok, errors)


if __name__ == "__main__":
    unittest.main()
