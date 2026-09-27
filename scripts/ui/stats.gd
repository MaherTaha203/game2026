extends Control
## Local statistics screen (MASTER_PROMPT §39). Read-only, local-only; nothing is
## transmitted. Clean list of lifetime figures.

func _ready() -> void:
	var root := VBoxContainer.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.add_theme_constant_override("separation", Style.GAP_M)
	add_child(root)

	var header := HBoxContainer.new()
	var back := Style.make_button(Localization.t("back"))
	back.custom_minimum_size = Vector2(120, Style.BUTTON_H)
	back.pressed.connect(func():
		AudioManager.play("button")
		ScreenManager.goto("menu"))
	header.add_child(back)
	var title := Style.make_title(Localization.t("stats"), Style.H2_SIZE)
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(title)
	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(120, 0)
	header.add_child(spacer)
	root.add_child(header)

	var s := SaveManager.stats()
	root.add_child(_row("stat_completed", str(int(s.get("puzzles_completed", 0)))))
	root.add_child(_row("stat_stars", "%d / %d" % [int(s.get("total_stars", 0)), GameState.total_levels * 3]))
	root.add_child(_row("stat_perfect", str(int(s.get("perfect_completions", 0)))))
	root.add_child(_row("stat_streak", str(int(s.get("current_streak", 0)))))
	root.add_child(_row("stat_best_streak", str(int(s.get("best_streak", 0)))))

func _row(label_key: String, value: String) -> Control:
	var row := HBoxContainer.new()
	var label := Label.new()
	label.text = Localization.t(label_key)
	label.add_theme_color_override("font_color", Style.MUTED)
	label.add_theme_font_size_override("font_size", Style.BODY_SIZE)
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(label)
	var val := Label.new()
	val.text = value
	val.add_theme_color_override("font_color", Style.ink())
	val.add_theme_font_size_override("font_size", Style.BODY_SIZE)
	row.add_child(val)
	return row
