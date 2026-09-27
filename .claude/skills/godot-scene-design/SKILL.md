---
name: godot-scene-design
description: Godot 4.x scene (.tscn) authoring for UI-driven games — text scene format, Control/Node2D hierarchies, container layout, UI node selection, groups, scene instancing, and animation setup. Use when creating or editing .tscn files or planning node hierarchies for ONE LINE's screens.
---

# Godot Scene Design Skill

> Adapted for ONE LINE from
> [godot-claude-skills](https://github.com/alexmeckes/godot-claude-skills)
> (MIT — see `LICENSE` in this folder). Platformer/3D/enemy/physics-body,
> tilemap, dialogue and collision-layer sections were removed because ONE LINE is
> a Control/Node2D puzzle with no physics; the UI/scene guidance below is what
> this project uses.

You are an expert at Godot 4.x scenes (`.tscn`), node hierarchies and UI layout.
ONE LINE keeps scene files thin (a root node + script) and builds most UI
procedurally in GDScript; use this when editing a `.tscn` or choosing node types.

## Scene File Format (TSCN)

Godot uses a readable, text-based scene format.

```ini
[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/ui/main_menu.gd" id="1"]

[node name="MainMenu" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
script = ExtResource("1")
```

Sections:
1. **Header** — `[gd_scene load_steps=N format=3]` (N = resources + 1).
2. **External resources** — scripts, textures, other scenes.
3. **Sub-resources** — inline resources (styleboxes, animations).
4. **Nodes** — the tree, with `parent="..."` references.
5. **Connections** — signal wiring (this project prefers connecting in code).

## Common UI Scene Patterns

### UI Screen (the ONE LINE pattern)
```
Screen (Control)                 # full-rect root, script attached
└── (built in code) CenterContainer / VBoxContainer
    ├── Title (Label)
    ├── Buttons (VBoxContainer)
    │   ├── PlayButton (Button)
    │   └── SettingsButton (Button)
```

### HUD / overlay
```
HUD (CanvasLayer)                # keeps UI independent of any world camera
└── Control
    └── MarginContainer
        └── HBoxContainer
            └── Label
```

## Node Selection Guide (UI-focused)

| Node | Use case |
|------|----------|
| `Control` | Base container / screen root |
| `Label` / `RichTextLabel` | Text display |
| `Button` / `TextureButton` / `CheckButton` | Clickable / toggles |
| `HBoxContainer` / `VBoxContainer` | Auto-layout rows/columns |
| `GridContainer` | Grids (e.g. level select) |
| `MarginContainer` | Padding / safe-area insets |
| `CenterContainer` | Centering |
| `PanelContainer` | Styled backgrounds |
| `ScrollContainer` | Scrollable content |
| `ColorRect` | Solid background fills |
| `Line2D` / `Polygon2D` | Custom 2D drawing (or use `_draw()` as PuzzleView does) |
| `AudioStreamPlayer` | Global SFX/music |
| `Timer` | Delays, cooldowns |
| `AnimationPlayer` | Authored property animation |

## Layout & Containers

- Prefer containers (`VBox/HBox/Grid/Margin/Center`) over hard-coded positions,
  so layouts adapt across aspect ratios (a core ONE LINE requirement).
- Use `size_flags_horizontal/vertical = SIZE_EXPAND_FILL` to let elements grow.
- Apply safe-area insets via a `MarginContainer` fed by
  `DisplayServer.get_display_safe_area()` (see `scripts/ui/main.gd`).

## Groups for Organization
```ini
[node name="Cell" type="Button" groups=["level_cells"]]
```
Query at runtime with `get_tree().get_nodes_in_group("level_cells")`.

## Scene Instancing
```ini
[ext_resource type="PackedScene" path="res://scenes/Gameplay.tscn" id="game"]

[node name="Game" parent="." instance=ExtResource("game")]
```
In code, ScreenManager loads screens with `load(path).instantiate()` and keeps
only one screen alive at a time.

## Property Overrides
```ini
[node name="Game" parent="." instance=ExtResource("game")]
some_exported_property = 42  # override an @export from the packed scene
```

## Animation Setup (AnimationPlayer)
```ini
[sub_resource type="Animation" id="Animation_fade"]
length = 0.3
tracks/0/type = "value"
tracks/0/path = NodePath(".:modulate:a")
```
For simple transitions this project uses code `Tween`s (respecting the
`reduced_motion` setting) rather than authored AnimationPlayers.

## Tips

1. Choose the root node by purpose — **`Control` for UI screens**, `Node2D` for a
   2D play area, `CanvasLayer` for HUD/overlays.
2. Build hierarchy logically; put UI elements inside containers.
3. Name nodes descriptively ("PlayButton", not "Button").
4. Use groups for runtime queries.
5. Instance reusable scenes instead of duplicating trees.
6. Parents process before children; use `z_index` for 2D layering.
7. Keep `.tscn` files minimal when the UI is built in code (the ONE LINE style).
