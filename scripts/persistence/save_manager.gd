extends Node
## Autoload: local, versioned, corruption-resilient save system.
##
## GDScript port of tools/oneline/save.py (which is unit-tested). Data lives only
## on-device in user://. Guarantees (docs/GAME_RULES.md, MASTER_PROMPT §11/§43/§44):
##   * missing save   -> clean defaults
##   * corrupt save   -> recover to defaults, never crash
##   * older save     -> migrated forward
##   * future save    -> handled without crash (falls back to defaults)
##   * writes are atomic (temp file + rename) to survive interruption

const SAVE_PATH := "user://save.json"
const TMP_PATH := "user://save.json.tmp"

var data: Dictionary = {}

signal save_loaded(recovered: bool, migrated: bool)
signal progress_changed()

func _ready() -> void:
	load_game()

# --------------------------------------------------------------------------
# Defaults
# --------------------------------------------------------------------------
func default_settings() -> Dictionary:
	return {
		"sound": true, "music": true, "haptics": true,
		"reduced_motion": false, "high_contrast": false, "language": "en",
	}

func default_stats() -> Dictionary:
	return {
		"puzzles_completed": 0, "total_stars": 0, "perfect_completions": 0,
		"current_streak": 0, "best_streak": 0, "total_play_seconds": 0,
	}

func default_daily() -> Dictionary:
	return {"last_date": null, "streak": 0, "best_streak": 0, "completed_dates": []}

func default_save() -> Dictionary:
	return {
		"save_data_version": Versions.SAVE_DATA_VERSION,
		"app_version": Versions.APP_VERSION,
		"progress": {"unlocked_max": 1, "levels": {}},
		"settings": default_settings(),
		"stats": default_stats(),
		"daily": default_daily(),
	}

# --------------------------------------------------------------------------
# Load / save
# --------------------------------------------------------------------------
func load_game() -> void:
	var recovered := false
	var migrated := false
	if not FileAccess.file_exists(SAVE_PATH):
		data = default_save()
		save_loaded.emit(false, false)
		return
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if f == null:
		data = default_save()
		save_loaded.emit(true, false)
		return
	var text := f.get_as_text()
	f.close()

	var parsed = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		data = default_save()
		save_loaded.emit(true, false)
		return

	var version = parsed.get("save_data_version")
	if typeof(version) != TYPE_FLOAT and typeof(version) != TYPE_INT:
		data = _salvage(parsed)
		save_loaded.emit(true, false)
		return
	version = int(version)
	if version > Versions.SAVE_DATA_VERSION:
		# Unknown future version: do not risk it.
		data = default_save()
		save_loaded.emit(true, false)
		return
	if version < Versions.SAVE_DATA_VERSION:
		parsed = _migrate(parsed, version)
		migrated = true

	if _validate(parsed):
		data = parsed
	else:
		data = _salvage(parsed)
		recovered = true
	save_loaded.emit(recovered, migrated)

func save_game() -> bool:
	var text := JSON.stringify(data, "\t")
	var tmp := FileAccess.open(TMP_PATH, FileAccess.WRITE)
	if tmp == null:
		push_error("SaveManager: cannot open temp file for writing")
		return false
	tmp.store_string(text)
	tmp.flush()
	tmp.close()
	# Atomic replace.
	var err := DirAccess.rename_absolute(
		ProjectSettings.globalize_path(TMP_PATH),
		ProjectSettings.globalize_path(SAVE_PATH)
	)
	if err != OK:
		# Fallback: direct write (still better than losing data).
		var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
		if f == null:
			return false
		f.store_string(text)
		f.flush()
		f.close()
	return true

# --------------------------------------------------------------------------
# Migration (chain: v1 -> v2)
# --------------------------------------------------------------------------
func _migrate(d: Dictionary, from_version: int) -> Dictionary:
	var version := from_version
	while version < Versions.SAVE_DATA_VERSION:
		if version == 1:
			d = _migrate_1_to_2(d)
		else:
			return default_save()
		version = int(d["save_data_version"])
	return d

func _migrate_1_to_2(d: Dictionary) -> Dictionary:
	var settings: Dictionary = d.get("settings", {})
	var merged := default_settings()
	for k in ["sound", "music", "language"]:
		if settings.has(k):
			merged[k] = settings[k]
	d["settings"] = merged
	if not d.has("stats"):
		d["stats"] = default_stats()
	if not d.has("daily"):
		d["daily"] = default_daily()
	if not d.has("progress") or typeof(d["progress"]) != TYPE_DICTIONARY:
		d["progress"] = {"unlocked_max": 1, "levels": {}}
	d["save_data_version"] = 2
	return d

# --------------------------------------------------------------------------
# Validation / salvage
# --------------------------------------------------------------------------
func _validate(d: Dictionary) -> bool:
	if int(d.get("save_data_version", -1)) != Versions.SAVE_DATA_VERSION:
		return false
	var progress = d.get("progress")
	if typeof(progress) != TYPE_DICTIONARY:
		return false
	if int(progress.get("unlocked_max", 0)) < 1:
		return false
	if typeof(progress.get("levels")) != TYPE_DICTIONARY:
		return false
	for key in ["settings", "stats", "daily"]:
		if typeof(d.get(key)) != TYPE_DICTIONARY:
			return false
	return true

func _salvage(d: Dictionary) -> Dictionary:
	var save := default_save()
	var progress = d.get("progress")
	if typeof(progress) == TYPE_DICTIONARY and typeof(progress.get("levels")) == TYPE_DICTIONARY:
		var good := {}
		var max_completed := 1
		for k in progress["levels"].keys():
			var rec = progress["levels"][k]
			if typeof(rec) == TYPE_DICTIONARY and rec.has("best_stars"):
				good[k] = rec
				if bool(rec.get("completed", false)):
					max_completed = maxi(max_completed, int(k) + 1)
		save["progress"]["levels"] = good
		save["progress"]["unlocked_max"] = maxi(max_completed, int(progress.get("unlocked_max", 1)))
	return save

# --------------------------------------------------------------------------
# High-level accessors
# --------------------------------------------------------------------------
func settings() -> Dictionary:
	return data["settings"]

func stats() -> Dictionary:
	return data["stats"]

func daily() -> Dictionary:
	return data["daily"]

func unlocked_max() -> int:
	return int(data["progress"]["unlocked_max"])

func is_unlocked(level_id: int) -> bool:
	return level_id <= unlocked_max()

func level_record(level_id: int) -> Dictionary:
	var levels: Dictionary = data["progress"]["levels"]
	return levels.get(str(level_id), {})

func best_stars(level_id: int) -> int:
	var rec := level_record(level_id)
	return int(rec.get("best_stars", 0))

func record_completion(level_id: int, stars: int, mistakes: int, total_levels: int) -> void:
	var levels: Dictionary = data["progress"]["levels"]
	var key := str(level_id)
	var prev: Dictionary = levels.get(key, {"completed": false, "best_stars": 0, "best_mistakes": -1})
	var was_completed := bool(prev.get("completed", false))
	var new_best_stars := maxi(int(prev.get("best_stars", 0)), stars)
	var prev_mistakes := int(prev.get("best_mistakes", -1))
	var new_best_mistakes := mistakes if prev_mistakes < 0 else mini(prev_mistakes, mistakes)
	levels[key] = {"completed": true, "best_stars": new_best_stars, "best_mistakes": new_best_mistakes}

	var next_level := level_id + 1
	if next_level <= total_levels:
		data["progress"]["unlocked_max"] = maxi(unlocked_max(), next_level)

	var st: Dictionary = data["stats"]
	if not was_completed:
		st["puzzles_completed"] = int(st["puzzles_completed"]) + 1
	var total := 0
	var perfect := 0
	for k in levels.keys():
		total += int(levels[k].get("best_stars", 0))
		if int(levels[k].get("best_stars", 0)) == 3:
			perfect += 1
	st["total_stars"] = total
	st["perfect_completions"] = perfect

	save_game()
	progress_changed.emit()

func reset_progress() -> void:
	var kept_settings: Dictionary = data.get("settings", default_settings())
	data = default_save()
	data["settings"] = kept_settings
	save_game()
	progress_changed.emit()

func set_setting(key: String, value) -> void:
	data["settings"][key] = value
	save_game()
