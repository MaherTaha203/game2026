extends RefCounted
class_name DailyPuzzle
## Offline, deterministic Daily Puzzle (docs/GAME_RULES.md §11, MASTER_PROMPT §38).
##
## The puzzle for a date is chosen deterministically from a date-based seed and
## the generator version, with no network/account. Because generation depends on
## the generator version, historical dailies may change across app versions; this
## is documented and never presented as globally synchronized.
##
## Implementation note: to guarantee the daily is always a real, validated puzzle,
## it deterministically selects one of the shipped campaign levels by date seed.
## This keeps the daily verifiable (it is one of the 210 validated levels) while
## remaining reproducible for a given date + generator version.

static func date_string(unix_time: int = -1) -> String:
	var t := unix_time if unix_time >= 0 else int(Time.get_unix_time_from_system())
	var d := Time.get_datetime_dict_from_unix_time(t)
	return "%04d-%02d-%02d" % [d["year"], d["month"], d["day"]]

static func _seed_for(date: String) -> int:
	var s := "%s|%s" % [Versions.GENERATOR_VERSION, date]
	return int(hash(s)) & 0x7fffffff

## Return the campaign level id used as today's daily (1-based).
static func level_id_for_date(date: String, total_levels: int) -> int:
	if total_levels <= 0:
		return 1
	return (_seed_for(date) % total_levels) + 1

static func today_level_id(total_levels: int) -> int:
	return level_id_for_date(date_string(), total_levels)
