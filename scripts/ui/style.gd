extends RefCounted
class_name Style
## Central design tokens for a single, coherent visual identity (MASTER_PROMPT §48).
## Minimalist / premium / calm. All colors, spacing, radii and animation timings
## live here so every screen looks like one product. A high-contrast variant is
## provided for accessibility (docs/GAME_RULES.md §13).
##
## State is never communicated by color alone: nodes also change size/outline and
## the current head is ringed, so the game reads correctly in high-contrast and
## for color-vision differences.

# ---- palette (standard) --------------------------------------------------
const BG := Color("12141a")
const SURFACE := Color("1b1e27")
const INK := Color("e8eaf0")
const MUTED := Color("8b90a0")
const ACCENT := Color("6ea8fe")
const SUCCESS := Color("57d9a3")
const DANGER := Color("ff6b6b")
const NODE := Color("3a4152")
const NODE_VISITED := Color("6ea8fe")
const LINE := Color("6ea8fe")
const STAR := Color("ffd166")

# ---- palette (high contrast) --------------------------------------------
const HC_BG := Color("000000")
const HC_INK := Color("ffffff")
const HC_ACCENT := Color("ffe14d")
const HC_NODE := Color("4d4d4d")
const HC_LINE := Color("ffe14d")

# ---- spacing / geometry --------------------------------------------------
const GAP_XS := 6
const GAP_S := 12
const GAP_M := 20
const GAP_L := 32
const GAP_XL := 48
const RADIUS := 14
const BUTTON_H := 64
const TITLE_SIZE := 64
const H2_SIZE := 34
const BODY_SIZE := 24
const NODE_RADIUS := 26.0
const LINE_WIDTH := 10.0

# ---- animation timings (seconds) ----------------------------------------
const T_FAST := 0.12
const T_MED := 0.22
const T_SLOW := 0.4

static func high_contrast() -> bool:
	return bool(SaveManager.settings().get("high_contrast", false))

static func reduced_motion() -> bool:
	return bool(SaveManager.settings().get("reduced_motion", false))

static func bg() -> Color:
	return HC_BG if high_contrast() else BG

static func ink() -> Color:
	return HC_INK if high_contrast() else INK

static func accent() -> Color:
	return HC_ACCENT if high_contrast() else ACCENT

static func node_color() -> Color:
	return HC_NODE if high_contrast() else NODE

static func node_visited() -> Color:
	return HC_ACCENT if high_contrast() else NODE_VISITED

static func line_color() -> Color:
	return HC_LINE if high_contrast() else LINE

## Build a primary button with consistent styling and large touch target.
static func make_button(text: String) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(0, BUTTON_H)
	b.focus_mode = Control.FOCUS_ALL
	b.add_theme_font_size_override("font_size", BODY_SIZE)
	var sb := StyleBoxFlat.new()
	sb.bg_color = SURFACE
	sb.corner_radius_top_left = RADIUS
	sb.corner_radius_top_right = RADIUS
	sb.corner_radius_bottom_left = RADIUS
	sb.corner_radius_bottom_right = RADIUS
	sb.content_margin_left = GAP_M
	sb.content_margin_right = GAP_M
	b.add_theme_stylebox_override("normal", sb)
	var hover := sb.duplicate()
	hover.bg_color = SURFACE.lightened(0.08)
	b.add_theme_stylebox_override("hover", hover)
	var pressed := sb.duplicate()
	pressed.bg_color = accent()
	b.add_theme_stylebox_override("pressed", pressed)
	b.add_theme_color_override("font_color", ink())
	return b

static func make_title(text: String, size: int = TITLE_SIZE) -> Label:
	var l := Label.new()
	l.text = text
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", ink())
	return l
