extends Node
## Autoload: light haptic feedback, independently disableable (MASTER_PROMPT §34).
## Uses Godot's Input.vibrate_handheld on mobile; a no-op elsewhere. Never
## required for gameplay understanding.

func light() -> void:
	_buzz(20)

func success() -> void:
	_buzz(40)

func warning() -> void:
	_buzz(30)

func _buzz(ms: int) -> void:
	if not bool(SaveManager.settings().get("haptics", true)):
		return
	if OS.has_feature("mobile"):
		Input.vibrate_handheld(ms)
