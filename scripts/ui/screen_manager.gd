extends Node
## Autoload: screen navigation with light fade transitions.
##
## Screens live under a container node provided by Main.gd. Transitions respect
## the reduced-motion setting (MASTER_PROMPT §41). Only one screen is alive at a
## time to avoid state/handler accumulation (MASTER_PROMPT §74).

const SCREENS := {
	"menu": "res://scenes/MainMenu.tscn",
	"levels": "res://scenes/LevelSelect.tscn",
	"game": "res://scenes/Gameplay.tscn",
	"complete": "res://scenes/LevelComplete.tscn",
	"settings": "res://scenes/Settings.tscn",
	"stats": "res://scenes/Stats.tscn",
}

var _container: Control = null
var _current: Control = null

func set_container(node: Control) -> void:
	_container = node

func goto(screen_name: String) -> void:
	if _container == null:
		push_error("ScreenManager: no container set")
		return
	if not SCREENS.has(screen_name):
		push_error("ScreenManager: unknown screen '%s'" % screen_name)
		return
	var packed: PackedScene = load(SCREENS[screen_name])
	if packed == null:
		push_error("ScreenManager: failed to load %s" % SCREENS[screen_name])
		return
	var inst := packed.instantiate()
	if not (inst is Control):
		push_error("ScreenManager: screen root must be a Control")
		return

	var new_screen := inst as Control
	new_screen.set_anchors_preset(Control.PRESET_FULL_RECT)
	_container.add_child(new_screen)

	var old_screen := _current
	_current = new_screen

	if Style.reduced_motion():
		if old_screen != null and is_instance_valid(old_screen):
			old_screen.queue_free()
		return

	new_screen.modulate.a = 0.0
	var tween := create_tween()
	tween.tween_property(new_screen, "modulate:a", 1.0, Style.T_MED)
	if old_screen != null and is_instance_valid(old_screen):
		tween.parallel().tween_property(old_screen, "modulate:a", 0.0, Style.T_FAST)
		tween.tween_callback(old_screen.queue_free)
