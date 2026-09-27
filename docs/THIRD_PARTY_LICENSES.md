# ONE LINE — Third-Party Components & Asset Audit

_Last audited: 2026-09-27._

This is the complete audit of components and assets shipped with the application
(MASTER_PROMPT §49–§50). The dependency footprint is intentionally minimal.

## Runtime engine

| Component | Version | Source | License | Commercial use | Attribution |
|---|---|---|---|---|---|
| Godot Engine | 4.3 stable | godotengine.org | MIT | Yes | Not required (appreciated) |

Godot is the only runtime dependency. No additional Godot plugins/addons are used.

## Fonts

The game uses **Godot's built-in default font** (open-source, bundled with the
MIT-licensed engine). No third-party font files are shipped. If a custom font is
added later, it must be recorded here with its license before shipping.

## Audio

All sound effects are **original**, generated procedurally by
`tools/gen_audio.py` using only the Python standard library (`wave`, `math`,
`struct`). No third-party or copyrighted audio is included.

| File | Origin |
|---|---|
| `assets/audio/node.wav` | Original, procedurally generated |
| `assets/audio/connect.wav` | Original, procedurally generated |
| `assets/audio/invalid.wav` | Original, procedurally generated |
| `assets/audio/button.wav` | Original, procedurally generated |
| `assets/audio/complete.wav` | Original, procedurally generated (C-major triad) |

No background music track ships in v1 (the music setting is reserved for a future
update).

## Graphics

* `assets/icon.svg` — **original** geometric mark (a one-stroke path through dots),
  authored for this project. No copyrighted characters, brands, or third-party art.
* All in-game visuals are drawn procedurally by `PuzzleView` and Godot `Control`
  nodes; no image assets are shipped beyond the icon.

## Developer tooling (not shipped in the app)

Python 3.11 standard library only (no third-party packages). Node.js is available
in the dev environment but is not used by the game or its tooling.

### Vendored Claude Code skills (developer guidance, not shipped in the app)

Two Godot-4 developer skills under `.claude/skills/` are adapted from a
third-party MIT-licensed source. They are documentation used by Claude Code while
developing; no code from them ships in the game binary.

| Skill | Source | License | Adaptation |
|---|---|---|---|
| `godot-code-gen` | [alexmeckes/godot-claude-skills](https://github.com/alexmeckes/godot-claude-skills) `skills/godot-code-gen` | MIT | Added frontmatter; removed physics-body movement examples unused by this project. |
| `godot-scene-design` | [alexmeckes/godot-claude-skills](https://github.com/alexmeckes/godot-claude-skills) `skills/godot-scene-design` | MIT | Added frontmatter; trimmed platformer/3D/enemy/physics/tilemap/dialogue/collision-layer sections. |

Each skill folder retains the upstream MIT license text and an adaptation note in
its `LICENSE` file.

## Statement

No asset in this repository is claimed as original if it was obtained externally;
per the table above, all shipped non-engine assets are original to this project.
