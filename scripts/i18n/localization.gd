extends Node
## Autoload: localization-ready string table (docs/GAME_RULES.md §14,
## MASTER_PROMPT §56). All user-facing strings go through `t()`, so adding a
## language later means adding a table — no UI code changes. English ships in v1;
## Arabic (RTL) is prepared for but NOT shipped (see docs/PRIVACY.md / README).
##
## Longer translations must not break layout; screens use containers, not fixed
## widths, to satisfy this.

var language := "en"

const STRINGS := {
	"en": {
		"app_title": "ONE LINE",
		"play": "Play",
		"continue": "Continue",
		"level_select": "Levels",
		"settings": "Settings",
		"daily": "Daily Puzzle",
		"back": "Back",
		"menu": "Menu",
		"restart": "Restart",
		"undo": "Undo",
		"hint": "Hint",
		"level": "Level",
		"locked": "Locked",
		"complete_title": "Complete!",
		"replay": "Replay",
		"next": "Next",
		"sound": "Sound",
		"music": "Music",
		"haptics": "Haptics",
		"reduced_motion": "Reduced Motion",
		"high_contrast": "High Contrast",
		"reset_progress": "Reset Progress",
		"reset_confirm": "Reset all progress? This cannot be undone.",
		"cancel": "Cancel",
		"confirm": "Reset",
		"tutorial_start": "Tap a dot to start",
		"tutorial_drag": "Drag to connect every line once",
		"no_hint": "No valid move — undo or restart",
		"stats": "Statistics",
		"stat_completed": "Puzzles completed",
		"stat_stars": "Total stars",
		"stat_perfect": "Perfect (3★)",
		"stat_streak": "Current streak",
		"stat_best_streak": "Best streak",
	},
	# Arabic table intentionally left for a future, reviewed release.
	"ar": {},
}

func set_language(code: String) -> void:
	if STRINGS.has(code):
		language = code

func t(key: String) -> String:
	var table: Dictionary = STRINGS.get(language, {})
	if table.has(key):
		return table[key]
	# Fall back to English, then to the key itself (never blank UI).
	var en: Dictionary = STRINGS["en"]
	return en.get(key, key)

func is_rtl() -> bool:
	return language == "ar"
