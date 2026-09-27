extends Control
## Gameplay screen (MASTER_PROMPT §5, §40). Header (level, menu, restart, undo,
## hint) + the puzzle view + light tutorial text on the first levels. Loads and
## validates the level defensively before play.

var _view: PuzzleView
var _tutorial: Label

func _ready() -> void:
	var level_id := GameState.current_level_id
	var level := LevelLoader.load_level(level_id)
	if level == null or not LevelValidator.validate(level).ok:
		# Fail gracefully: never crash on bad data (MASTER_PROMPT §55).
		_show_error()
		return

	GameState.begin_session()

	var root := VBoxContainer.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.add_theme_constant_override("separation", Style.GAP_S)
	add_child(root)

	root.add_child(_header(level_id))

	_view = PuzzleView.new()
	_view.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_view.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.add_child(_view)
	_view.setup(level)
	_view.completed.connect(_on_completed)
	_view.invalid.connect(_on_invalid)
	_view.progressed.connect(_on_progressed)

	_tutorial = Label.new()
	_tutorial.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_tutorial.add_theme_color_override("font_color", Style.MUTED)
	_tutorial.add_theme_font_size_override("font_size", Style.BODY_SIZE)
	_tutorial.custom_minimum_size = Vector2(0, 40)
	root.add_child(_tutorial)
	_update_tutorial(level_id)

func _header(level_id: int) -> Control:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", Style.GAP_S)

	var menu := _icon_button(Localization.t("menu"))
	menu.pressed.connect(func(): ScreenManager.goto("menu"))
	row.add_child(menu)

	var title := Style.make_title("%s %d" % [Localization.t("level"), level_id], Style.H2_SIZE)
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(title)

	var undo := _icon_button(Localization.t("undo"))
	undo.pressed.connect(func(): _view.do_undo())
	row.add_child(undo)

	var hint := _icon_button(Localization.t("hint"))
	hint.pressed.connect(func(): _view.show_hint())
	row.add_child(hint)

	var restart := _icon_button(Localization.t("restart"))
	restart.pressed.connect(func(): _view.do_restart())
	row.add_child(restart)

	return row

func _icon_button(text: String) -> Button:
	var b := Style.make_button(text)
	b.custom_minimum_size = Vector2(0, Style.BUTTON_H)
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	b.add_theme_font_size_override("font_size", 20)
	return b

func _update_tutorial(level_id: int) -> void:
	if level_id == 1:
		_tutorial.text = Localization.t("tutorial_start")
	elif level_id == 2:
		_tutorial.text = Localization.t("tutorial_drag")
	else:
		_tutorial.text = ""

func _on_progressed() -> void:
	if _tutorial != null and _view.engine.started():
		_tutorial.text = ""

func _on_invalid() -> void:
	if _tutorial != null and _view._hint_node < 0 and _view.engine != null:
		# When a hint found no move it emits invalid; guide the player.
		var completion := PuzzleSolver.find_completion(
			_view.graph, _view.engine.used_edges, _view.engine.current())
		if completion.is_empty() and _view.engine.started():
			_tutorial.text = Localization.t("no_hint")

func _on_completed(mistakes: int) -> void:
	AudioManager.play("complete")
	Haptics.success()
	var level := LevelLoader.load_level(GameState.current_level_id)
	GameState.complete_level(
		GameState.current_level_id, mistakes,
		level.three_max_mistakes, level.two_max_mistakes)
	# Brief pause so the completion is felt before transitioning.
	var delay := 0.0 if Style.reduced_motion() else 0.45
	await get_tree().create_timer(delay).timeout
	ScreenManager.goto("complete")

func _show_error() -> void:
	var center := CenterContainer.new()
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(center)
	var col := VBoxContainer.new()
	center.add_child(col)
	var msg := Style.make_title("Level unavailable", Style.H2_SIZE)
	col.add_child(msg)
	var back := Style.make_button(Localization.t("back"))
	back.pressed.connect(func(): ScreenManager.goto("levels"))
	col.add_child(back)
