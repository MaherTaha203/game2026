extends Node
## Autoload: session state and the bridge between UI screens and persistence.
##
## Owns the "currently selected level" and play-session timing, and centralizes
## completion handling so every screen records progress the same way
## (docs/ARCHITECTURE_RULES.md — Game State layer).

var current_level_id: int = 1
var total_levels: int = 0

# Last-completed result, consumed by the Level Complete screen.
var last_result: Dictionary = {}

var _session_start_ms: int = 0

func _ready() -> void:
	total_levels = LevelLoader.level_count()

func begin_session() -> void:
	_session_start_ms = Time.get_ticks_msec()

func end_session_seconds() -> int:
	if _session_start_ms == 0:
		return 0
	var secs := int((Time.get_ticks_msec() - _session_start_ms) / 1000.0)
	_session_start_ms = 0
	return secs

func select_level(level_id: int) -> void:
	current_level_id = clampi(level_id, 1, maxi(1, total_levels))

func has_next_level() -> bool:
	return current_level_id < total_levels

func next_level_id() -> int:
	return mini(current_level_id + 1, total_levels)

## Record a completed level: stars, unlock, stats, daily streak. Returns the
## result dictionary also stored in `last_result`.
func complete_level(level_id: int, mistakes: int, three_max: int, two_max: int) -> Dictionary:
	var stars := StarRules.compute_stars(mistakes, three_max, two_max, true)
	var prev_best := SaveManager.best_stars(level_id)
	SaveManager.record_completion(level_id, stars, mistakes, total_levels)

	# Accumulate play time into lifetime stats.
	var secs := end_session_seconds()
	if secs > 0:
		var st := SaveManager.stats()
		st["total_play_seconds"] = int(st["total_play_seconds"]) + secs
		SaveManager.save_game()

	last_result = {
		"level_id": level_id,
		"stars": stars,
		"mistakes": mistakes,
		"prev_best": prev_best,
		"improved": stars > prev_best,
		"has_next": has_next_level(),
	}
	return last_result
