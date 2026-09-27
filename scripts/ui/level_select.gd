extends Control
## Level select (MASTER_PROMPT §5). Scrollable grid showing level number,
## completion status and star rating. Locked levels are visually distinct via
## dimming AND a lock glyph (not color alone) and are non-interactive.

func _ready() -> void:
	var root := VBoxContainer.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.add_theme_constant_override("separation", Style.GAP_M)
	add_child(root)

	root.add_child(_header())

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	root.add_child(scroll)

	var grid := GridContainer.new()
	grid.columns = 4
	grid.add_theme_constant_override("h_separation", Style.GAP_S)
	grid.add_theme_constant_override("v_separation", Style.GAP_S)
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(grid)

	var total := GameState.total_levels
	for level_id in range(1, total + 1):
		grid.add_child(_level_cell(level_id))

func _header() -> Control:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", Style.GAP_S)
	var back := Style.make_button(Localization.t("back"))
	back.custom_minimum_size = Vector2(120, Style.BUTTON_H)
	back.pressed.connect(func():
		AudioManager.play("button")
		ScreenManager.goto("menu"))
	row.add_child(back)
	var title := Style.make_title(Localization.t("level_select"), Style.H2_SIZE)
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(title)
	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(120, 0)
	row.add_child(spacer)
	return row

func _level_cell(level_id: int) -> Control:
	var unlocked := SaveManager.is_unlocked(level_id)
	var stars := SaveManager.best_stars(level_id)

	var cell := Button.new()
	cell.custom_minimum_size = Vector2(0, 96)
	cell.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	cell.disabled = not unlocked
	cell.focus_mode = Control.FOCUS_ALL

	var sb := StyleBoxFlat.new()
	sb.bg_color = Style.SURFACE if unlocked else Style.SURFACE.darkened(0.35)
	for c in ["corner_radius_top_left", "corner_radius_top_right",
			"corner_radius_bottom_left", "corner_radius_bottom_right"]:
		sb.set(c, Style.RADIUS)
	cell.add_theme_stylebox_override("normal", sb)
	cell.add_theme_stylebox_override("disabled", sb)

	var vbox := VBoxContainer.new()
	vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	vbox.mouse_filter = Control.MOUSE_FILTER_IGNORE
	vbox.alignment = BoxContainer.ALIGNMENT_CENTER
	cell.add_child(vbox)

	var num := Label.new()
	num.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	num.add_theme_font_size_override("font_size", Style.H2_SIZE)
	if unlocked:
		num.text = str(level_id)
		num.add_theme_color_override("font_color", Style.ink())
	else:
		num.text = "✖"  # heavy multiplication x as a lock glyph
		num.add_theme_color_override("font_color", Style.MUTED)
	vbox.add_child(num)

	var stars_label := Label.new()
	stars_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	stars_label.add_theme_font_size_override("font_size", 20)
	stars_label.add_theme_color_override("font_color", Style.STAR)
	if not unlocked:
		stars_label.text = Localization.t("locked")
		stars_label.add_theme_color_override("font_color", Style.MUTED)
	elif stars > 0:
		stars_label.text = "★".repeat(stars) + "☆".repeat(3 - stars)
	else:
		stars_label.text = "☆☆☆"
		stars_label.add_theme_color_override("font_color", Style.MUTED)
	vbox.add_child(stars_label)

	if unlocked:
		cell.pressed.connect(func():
			AudioManager.play("button")
			GameState.select_level(level_id)
			ScreenManager.goto("game"))
	return cell
