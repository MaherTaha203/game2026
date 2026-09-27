extends Control
## Main menu (MASTER_PROMPT §5). Title, Play, Continue (when progress exists),
## Levels, Daily Puzzle, Settings, Stats. Works across aspect ratios via
## containers rather than fixed coordinates.

func _ready() -> void:
	var center := CenterContainer.new()
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(center)

	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", Style.GAP_M)
	col.custom_minimum_size = Vector2(360, 0)
	center.add_child(col)

	var title := Style.make_title(Localization.t("app_title"))
	col.add_child(title)

	var subtitle := Label.new()
	subtitle.text = Localization.t("subtitle")
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_color_override("font_color", Style.MUTED)
	subtitle.add_theme_font_size_override("font_size", Style.BODY_SIZE)
	col.add_child(subtitle)

	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(0, Style.GAP_L)
	col.add_child(spacer)

	var has_progress := SaveManager.unlocked_max() > 1
	if has_progress:
		var cont := Style.make_button(Localization.t("continue"))
		cont.pressed.connect(func():
			AudioManager.play("button")
			GameState.select_level(SaveManager.unlocked_max())
			ScreenManager.goto("game"))
		col.add_child(cont)

	var play := Style.make_button(Localization.t("play"))
	play.pressed.connect(func():
		AudioManager.play("button")
		GameState.select_level(1 if not has_progress else SaveManager.unlocked_max())
		ScreenManager.goto("game"))
	col.add_child(play)

	col.add_child(_menu_button("level_select", func(): ScreenManager.goto("levels")))
	col.add_child(_menu_button("daily", func():
		var lid := DailyPuzzle.today_level_id(GameState.total_levels)
		GameState.select_daily(lid, DailyPuzzle.date_string())
		ScreenManager.goto("game")))
	col.add_child(_menu_button("stats", func(): ScreenManager.goto("stats")))
	col.add_child(_menu_button("settings", func(): ScreenManager.goto("settings")))

func _menu_button(key: String, action: Callable) -> Button:
	var b := Style.make_button(Localization.t(key))
	b.pressed.connect(func():
		AudioManager.play("button")
		action.call())
	return b
