---
name: game-development
description: Engineering rules for implementing the ONE LINE puzzle game in Godot 4.x and GDScript. Use when writing or modifying gameplay code, scenes, nodes, input handling, UI, game state, level loading, runtime gameplay, audio, animation, or mobile behavior.
---

# Game Development Skill

## Purpose

Provide the engineering rules for implementing ONE LINE in Godot 4.x.

## Responsibilities

This skill governs:

* Godot project architecture.
* GDScript.
* Scenes.
* Nodes.
* Input handling.
* UI.
* Game state.
* Level loading.
* Gameplay runtime.
* Audio.
* Animation.
* Mobile behavior.

## Rules

Prefer composition over unnecessary inheritance.

Keep gameplay logic separate from presentation where practical.

The puzzle engine should be testable independently from visual scenes.

Do not put core puzzle rules exclusively inside UI scripts.

Gameplay state must have a clear owner.

Avoid global mutable state unless justified.

Use signals/events where they simplify communication.

Avoid circular dependencies.

Do not hard-code level-specific gameplay logic.

The same gameplay rules must apply to:

* touch input;
* mouse input;
* automated tests.

## Input

Touch input must feel responsive.

Handle:

* touch start;
* continuous drag;
* node detection;
* invalid movement;
* touch release;
* restart gestures/buttons where applicable.

Mouse input should provide equivalent development behavior.

## UI

UI must adapt to different screen sizes.

Respect safe areas.

Avoid hard-coded pixel assumptions where possible.

UI text should be localization-ready.

## Performance

Avoid unnecessary per-frame allocations.

Avoid expensive operations in `_process()` unless necessary.

Do not repeatedly load the same level data unnecessarily.

Keep animations lightweight.

The game should remain responsive on supported mobile hardware.

## Completion

A gameplay feature is not considered complete until its runtime behavior and relevant tests have been verified.
