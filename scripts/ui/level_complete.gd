extends Control
## Level Complete screen (MASTER_PROMPT §5). Shows earned stars with a reveal
## animation, plus Replay / Next / Level Select.

func _ready() -> void:
	var result := GameState.last_result
	var stars := int(result.get("stars", 1))

	var center := CenterContainer.new()
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(center)

	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", Style.GAP_M)
	col.custom_minimum_size = Vector2(360, 0)
	center.add_child(col)

	col.add_child(Style.make_title(Localization.t("complete_title")))

	var stars_row := HBoxContainer.new()
	stars_row.alignment = BoxContainer.ALIGNMENT_CENTER
	stars_row.add_theme_constant_override("separation", Style.GAP_S)
	col.add_child(stars_row)
	_build_stars(stars_row, stars)

	if bool(result.get("improved", false)):
		var improved := Label.new()
		improved.text = "New best!"
		improved.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		improved.add_theme_color_override("font_color", Style.SUCCESS)
		improved.add_theme_font_size_override("font_size", Style.BODY_SIZE)
		col.add_child(improved)

	if bool(result.get("is_daily", false)):
		var streak := Label.new()
		var days := int(result.get("streak", 0))
		streak.text = "%s: %d" % [Localization.t("stat_streak"), days]
		streak.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		streak.add_theme_color_override("font_color", Style.accent())
		streak.add_theme_font_size_override("font_size", Style.BODY_SIZE)
		col.add_child(streak)

	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(0, Style.GAP_M)
	col.add_child(spacer)

	if bool(result.get("has_next", false)):
		var next := Style.make_button(Localization.t("next"))
		next.pressed.connect(func():
			AudioManager.play("button")
			GameState.select_level(GameState.next_level_id())
			ScreenManager.goto("game"))
		col.add_child(next)

	var replay := Style.make_button(Localization.t("replay"))
	replay.pressed.connect(func():
		AudioManager.play("button")
		ScreenManager.goto("game"))
	col.add_child(replay)

	var levels := Style.make_button(Localization.t("level_select"))
	levels.pressed.connect(func():
		AudioManager.play("button")
		ScreenManager.goto("levels"))
	col.add_child(levels)

func _build_stars(row: HBoxContainer, earned: int) -> void:
	for i in range(3):
		var star := Label.new()
		star.add_theme_font_size_override("font_size", 72)
		var filled := i < earned
		star.text = "★" if filled else "☆"
		star.add_theme_color_override("font_color", Style.STAR if filled else Style.MUTED)
		row.add_child(star)
		if filled and not Style.reduced_motion():
			star.scale = Vector2.ZERO
			star.pivot_offset = Vector2(36, 36)
			var tw := create_tween()
			tw.tween_interval(0.15 * i)
			tw.tween_property(star, "scale", Vector2.ONE, Style.T_MED)\
				.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
