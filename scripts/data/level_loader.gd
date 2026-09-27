extends RefCounted
class_name LevelLoader
## Loads campaign levels from res://levels/ (the JSON produced by the Python
## pipeline). Fails gracefully: a malformed or missing file is reported, never
## crashes the game (docs/GAME_RULES.md §12, MASTER_PROMPT §55).

const LEVELS_DIR := "res://levels/"
const INDEX_PATH := "res://levels/index.json"

## Returns the ordered campaign index array of {id, file, tier, ...} or [].
static func load_index() -> Array:
	var text := _read_text(INDEX_PATH)
	if text == "":
		push_warning("LevelLoader: index.json missing or empty")
		return []
	var parsed = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY or not parsed.has("levels"):
		push_warning("LevelLoader: index.json malformed")
		return []
	return parsed["levels"]

## Total number of campaign levels (0 if index unavailable).
static func level_count() -> int:
	return load_index().size()

## Load a single level by campaign id. Returns null on failure.
static func load_level(level_id: int) -> Level:
	var path := "%slevel_%04d.json" % [LEVELS_DIR, level_id]
	var text := _read_text(path)
	if text == "":
		push_warning("LevelLoader: missing level file %s" % path)
		return null
	var parsed = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		push_warning("LevelLoader: malformed level %s" % path)
		return null
	return Level.from_dict(parsed)

static func _read_text(path: String) -> String:
	if not FileAccess.file_exists(path):
		return ""
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return ""
	var text := f.get_as_text()
	f.close()
	return text
