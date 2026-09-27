extends Control
## Settings screen (MASTER_PROMPT §5, §41). Sound, Music, Haptics, Reduced Motion,
## High Contrast toggles + Reset Progress (with confirmation). All persist
## immediately via SaveManager.

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
	var title := Style.make_title(Localization.t("settings"), Style.H2_SIZE)
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(title)
	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(120, 0)
	header.add_child(spacer)
	root.add_child(header)

	# Note: no "music" toggle — no music track ships in v1 (a control for a
	# non-existent feature is misleading). The save key is retained for a future
	# update but is not shown.
	root.add_child(_toggle("sound", "sound"))
	root.add_child(_toggle("haptics", "haptics"))
	root.add_child(_toggle("reduced_motion", "reduced_motion"))
	root.add_child(_toggle("high_contrast", "high_contrast"))

	var gap := Control.new()
	gap.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(gap)

	var reset := Style.make_button(Localization.t("reset_progress"))
	reset.add_theme_color_override("font_color", Style.DANGER)
	reset.pressed.connect(_confirm_reset)
	root.add_child(reset)

func _toggle(setting_key: String, label_key: String) -> Control:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", Style.GAP_S)

	var label := Label.new()
	label.text = Localization.t(label_key)
	label.add_theme_color_override("font_color", Style.ink())
	label.add_theme_font_size_override("font_size", Style.BODY_SIZE)
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(label)

	var check := CheckButton.new()
	check.button_pressed = bool(SaveManager.settings().get(setting_key, true))
	check.toggled.connect(func(pressed: bool):
		AudioManager.play("button")
		SaveManager.set_setting(setting_key, pressed)
		if setting_key == "high_contrast":
			# Rebuild the screen so tokens apply immediately.
			ScreenManager.goto("settings"))
	row.add_child(check)
	return row

func _confirm_reset() -> void:
	var dialog := ConfirmationDialog.new()
	dialog.dialog_text = Localization.t("reset_confirm")
	dialog.ok_button_text = Localization.t("confirm")
	dialog.cancel_button_text = Localization.t("cancel")
	add_child(dialog)
	dialog.confirmed.connect(func():
		SaveManager.reset_progress()
		GameState.total_levels = LevelLoader.level_count()
		ScreenManager.goto("menu"))
	dialog.popup_centered()
