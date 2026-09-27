extends Control
## Root boot node. Builds the background + safe-area container, registers the
## screen container with ScreenManager, and routes to the first screen.
## Handles app-lifecycle events to protect progress (MASTER_PROMPT §43).

var _safe_area_container: MarginContainer

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)

	var bg := ColorRect.new()
	bg.color = Style.bg()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)

	_safe_area_container = MarginContainer.new()
	_safe_area_container.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_safe_area_container)
	_apply_safe_area()

	var screen_host := Control.new()
	screen_host.set_anchors_preset(Control.PRESET_FULL_RECT)
	_safe_area_container.add_child(screen_host)

	# Apply saved language before any screen builds its labels.
	Localization.set_language(str(SaveManager.settings().get("language", "en")))

	ScreenManager.set_container(screen_host)
	ScreenManager.goto("menu")

	get_viewport().size_changed.connect(_apply_safe_area)

func _apply_safe_area() -> void:
	if _safe_area_container == null:
		return
	# Respect device notches / rounded corners / gesture areas.
	var safe := DisplayServer.get_display_safe_area()
	var win := DisplayServer.window_get_size()
	var left := maxi(safe.position.x, Style.GAP_S)
	var top := maxi(safe.position.y, Style.GAP_S)
	var right := maxi(win.x - (safe.position.x + safe.size.x), Style.GAP_S)
	var bottom := maxi(win.y - (safe.position.y + safe.size.y), Style.GAP_S)
	_safe_area_container.add_theme_constant_override("margin_left", left)
	_safe_area_container.add_theme_constant_override("margin_top", top)
	_safe_area_container.add_theme_constant_override("margin_right", right)
	_safe_area_container.add_theme_constant_override("margin_bottom", bottom)

func _notification(what: int) -> void:
	# Persist on background / focus loss so interruption never loses progress.
	match what:
		NOTIFICATION_APPLICATION_PAUSED, NOTIFICATION_WM_GO_BACK_REQUEST, \
		NOTIFICATION_APPLICATION_FOCUS_OUT, NOTIFICATION_WM_CLOSE_REQUEST:
			SaveManager.save_game()
