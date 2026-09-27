extends RefCounted
class_name DailyRules
## Pure daily-puzzle streak logic — GDScript mirror of the daily functions in
## tools/oneline/save.py (which are unit-tested). Kept dependency-free (no
## autoloads) so it is verifiable headless in tests/gdscript/run_tests.gd.

const MAX_COMPLETED_DATES := 400

## Consecutive if cur is exactly the day after prev (ISO "YYYY-MM-DD").
## UTC-midnight unix seconds make a one-day gap exactly 86400s (DST-safe).
static func is_consecutive(prev_date: String, cur_date: String) -> bool:
	var p := Time.get_unix_time_from_datetime_string(prev_date + "T00:00:00")
	var c := Time.get_unix_time_from_datetime_string(cur_date + "T00:00:00")
	if p == 0 or c == 0:
		return false
	return int(c) - int(p) == 86400

static func already_completed(daily: Dictionary, date_str: String) -> bool:
	var completed: Array = daily.get("completed_dates", [])
	return completed.has(date_str)

## Apply a completion to the given daily+stats dictionaries (mutates them).
## Returns true if this was a new completion, false if the date was already done.
static func apply_completion(daily: Dictionary, stats: Dictionary, date_str: String) -> bool:
	var completed: Array = daily.get("completed_dates", [])
	if completed.has(date_str):
		return false

	var last = daily.get("last_date")
	var new_streak := 1
	if last != null and is_consecutive(str(last), date_str):
		new_streak = int(daily.get("streak", 0)) + 1

	daily["streak"] = new_streak
	daily["best_streak"] = maxi(int(daily.get("best_streak", 0)), new_streak)
	daily["last_date"] = date_str
	completed.append(date_str)
	if completed.size() > MAX_COMPLETED_DATES:
		completed = completed.slice(completed.size() - MAX_COMPLETED_DATES)
	daily["completed_dates"] = completed

	stats["current_streak"] = new_streak
	stats["best_streak"] = maxi(int(stats.get("best_streak", 0)), new_streak)
	return true
