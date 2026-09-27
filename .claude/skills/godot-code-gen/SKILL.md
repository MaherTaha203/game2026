---
name: godot-code-gen
description: Godot 4.x GDScript conventions — static typing, annotations, signals, state machines, resources, autoloads, async/await, tweens, scene instantiation, and input handling. Use when writing or reviewing GDScript so it follows idiomatic Godot 4 patterns. Complements the project's game-development skill with concrete code idioms.
---

# Godot Code Generation Skill

> Adapted for ONE LINE from
> [godot-claude-skills](https://github.com/alexmeckes/godot-claude-skills)
> (MIT — see `LICENSE` in this folder). Physics-body (CharacterBody2D/3D)
> movement examples were removed because ONE LINE is a Control/Node2D puzzle with
> no physics bodies; everything else is idiomatic Godot 4 and applies directly.

You are an expert Godot 4.x developer. When generating or reviewing GDScript,
follow these patterns. They match the conventions already used in this project's
`scripts/` (typed vars, `maxi/mini/maxf/minf`, `@onready`, signal `.connect`).

## GDScript 4.x Syntax

### Type Hints (always use)
```gdscript
var speed: float = 200.0
var health: int = 100
var items: Array[String] = []
var stats: Dictionary = {}

func calculate_damage(base: int, multiplier: float) -> int:
    return int(base * multiplier)
```

Note: Godot's `min()`/`max()` return Variant and break `:=` type inference; use
the typed variants `maxi/mini/maxf/minf` (a real bug fixed in this project).

### Annotations
```gdscript
@export var speed: float = 200.0            # Visible in inspector
@export_range(0, 100) var health: int = 50  # With range slider
@export_enum("Easy", "Medium", "Hard") var difficulty: int = 1

@onready var sprite: Sprite2D = $Sprite2D   # Initialized when ready

@tool          # Runs in editor
class_name MyClass  # Global class registration (enables discovery/type name)
```

### Signals (Godot 4.x style)
```gdscript
# Declaration
signal health_changed(new_health: int)
signal died

# Emission
health_changed.emit(current_health)
died.emit()

# Connection (prefer callable syntax)
button.pressed.connect(_on_button_pressed)

# With binds / one-shot
timer.timeout.connect(_on_timeout.bind(extra_arg))
signal_name.connect(callable, CONNECT_ONE_SHOT)
```

### State machine (enum + match)
```gdscript
extends Node

enum State { IDLE, WALK, RUN }

var current_state: State = State.IDLE

func change_state(new_state: State) -> void:
    if new_state == current_state:
        return
    _exit_state(current_state)
    current_state = new_state
    _enter_state(new_state)
```

### Resource pattern (data as `.tres`)
```gdscript
# item_data.gd
class_name ItemData
extends Resource

@export var name: String
@export var value: int

# Using resources
var sword: ItemData = preload("res://items/sword.tres")
```

### Autoload / singleton
```gdscript
# game_manager.gd — register under Project Settings > Autoload
extends Node

signal game_paused

var score: int = 0

func add_score(points: int) -> void:
    score += points
```
This project uses autoloads for `Versions`, `Localization`, `SaveManager`,
`GameState`, `AudioManager`, `Haptics`, `ScreenManager` (see `project.godot`).

### Async / await (replaces `yield`)
```gdscript
await get_tree().create_timer(1.0).timeout
await animation_player.animation_finished

func load_level_async(path: String) -> void:
    ResourceLoader.load_threaded_request(path)
    while ResourceLoader.load_threaded_get_status(path) == ResourceLoader.THREAD_LOAD_IN_PROGRESS:
        await get_tree().process_frame
    var scene := ResourceLoader.load_threaded_get(path)
    get_tree().change_scene_to_packed(scene)
```

### Tweens (Godot 4.x)
```gdscript
var tween := create_tween()
tween.tween_property(sprite, "modulate:a", 0.0, 1.0)

# Chained, parallel, easing
tween.tween_property(node, "position", Vector2(100, 100), 0.5)
tween.set_parallel(true)
tween.set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)
```
Respect the project's `reduced_motion` setting before animating.

### Scene instantiation
```gdscript
const EnemyScene := preload("res://scenes/enemy.tscn")  # compile-time, frequent
var inst := EnemyScene.instantiate()
add_child(inst)

var scene := load("res://scenes/enemy.tscn")            # runtime, dynamic
```

### Input handling
```gdscript
func _input(event: InputEvent) -> void:
    if event.is_action_pressed("attack"):
        attack()
    if event is InputEventMouseButton and event.pressed:
        if event.button_index == MOUSE_BUTTON_LEFT:
            shoot()

func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("pause"):
        toggle_pause()
```
For touch + mouse together (as in `PuzzleView`), handle `InputEventScreenTouch`/
`InputEventScreenDrag` and mouse events directly and keep pointer emulation off to
avoid double-firing.

## Best Practices

1. Always use type hints — performance and early error detection.
2. Use `@onready` for node references.
3. Prefer signals over direct calls for loose coupling.
4. Use Resources for data.
5. Prefer composition over inheritance.
6. Private members start with `_`.
7. PascalCase for classes, snake_case for functions/variables.
8. Document with `##` comments (in-editor docs).

## Common Gotchas

- `yield` is gone — use `await`.
- `connect("sig", self, "method")` is gone — use `signal.connect(callable)`.
- `instance()` is now `instantiate()`.
- `export`/`onready`/`tool` are now `@export`/`@onready`/`@tool`.
- `min()`/`max()` return Variant — use `maxi/mini/maxf/minf` with `:=`.
