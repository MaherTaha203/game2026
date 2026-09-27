extends Control
class_name PuzzleView
## Renders a level and drives touch/mouse interaction (MASTER_PROMPT §3, §19-§20,
## §34). Rendering is pure presentation; all rules come from PuzzleEngine.
##
## Interaction model (one-stroke):
##   * press on a node          -> start the line there
##   * drag over an adjacent    -> commit that edge and advance the head
##     node via an unused edge
##   * invalid attempts         -> feedback (flash + sound + haptic), no state change
##   * release                  -> line stays; player may continue, undo or restart
##
## The same code path serves mouse (desktop QA) and touch (mobile).

signal completed(mistakes: int)
signal invalid()
signal progressed()

var level: Level
var graph: PuzzleGraph
var engine: PuzzleEngine

var _pointer := Vector2.ZERO
var _dragging := false
var _hint_node := -1
var _flash := 0.0            # invalid-move flash timer
var _pad := 40.0

func setup(lv: Level) -> void:
	level = lv
	graph = lv.to_graph()
	engine = PuzzleEngine.new(graph)
	engine.completed.connect(func(): completed.emit(engine.mistakes))
	queue_redraw()

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	set_process(false)

# --------------------------------------------------------------------------
# Geometry
# --------------------------------------------------------------------------
func _play_origin_and_side() -> Array:
	var r := size
	var side: float = minf(r.x, r.y) - _pad * 2.0
	side = maxf(side, 32.0)
	var origin := Vector2((r.x - side) * 0.5, (r.y - side) * 0.5)
	return [origin, side]

func _node_px(nid: int) -> Vector2:
	var o = _play_origin_and_side()
	var pos: Vector2 = level.positions()[nid]
	return o[0] + pos * o[1]

func _nearest_node(point: Vector2, max_dist: float) -> int:
	var best := -1
	var best_d := max_dist
	for nid in graph.node_ids:
		var d := point.distance_to(_node_px(nid))
		if d < best_d:
			best_d = d
			best = nid
	return best

# --------------------------------------------------------------------------
# Input
# --------------------------------------------------------------------------
func _gui_input(event: InputEvent) -> void:
	if engine == null:
		return
	if event is InputEventScreenTouch:
		if event.pressed:
			_begin(event.position)
		else:
			_end()
	elif event is InputEventScreenDrag:
		_drag(event.position)
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if event.pressed:
			_begin(event.position)
		else:
			_end()
	elif event is InputEventMouseMotion and _dragging:
		_drag(event.position)

func _begin(pos: Vector2) -> void:
	_dragging = true
	_pointer = pos
	set_process(true)
	_hint_node = -1
	var hit := _nearest_node(pos, Style.NODE_RADIUS * 1.8)
	if hit >= 0:
		if not engine.started():
			engine.move_to(hit)  # start
			AudioManager.play("node")
			Haptics.light()
			progressed.emit()
		else:
			_try_advance(hit)
	queue_redraw()

func _drag(pos: Vector2) -> void:
	_pointer = pos
	if not _dragging or not engine.started():
		queue_redraw()
		return
	var hit := _nearest_node(pos, Style.NODE_RADIUS * 1.6)
	if hit >= 0 and hit != engine.current():
		_try_advance(hit)
	queue_redraw()

func _end() -> void:
	_dragging = false
	set_process(false)
	queue_redraw()

func _try_advance(node_id: int) -> void:
	var result := engine.move_to(node_id)
	match result:
		PuzzleEngine.MoveResult.OK, PuzzleEngine.MoveResult.OK_COMPLETED:
			AudioManager.play("connect")
			Haptics.light()
			_hint_node = -1
			progressed.emit()
		PuzzleEngine.MoveResult.INVALID_SAME_NODE:
			pass  # ignore re-touching current node
		_:
			_on_invalid()

func _on_invalid() -> void:
	AudioManager.play("invalid")
	Haptics.warning()
	invalid.emit()
	if not Style.reduced_motion():
		_flash = 0.35
		set_process(true)
	queue_redraw()

# --------------------------------------------------------------------------
# Public controls (wired from the gameplay header)
# --------------------------------------------------------------------------
func do_undo() -> void:
	if engine.undo():
		AudioManager.play("button")
		queue_redraw()

func do_restart() -> void:
	engine.restart()
	_hint_node = -1
	AudioManager.play("button")
	queue_redraw()

func show_hint() -> void:
	var used := engine.used_edges
	var completion := PuzzleSolver.find_completion(graph, used, engine.current())
	if completion.is_empty():
		_hint_node = -1
		invalid.emit()  # gameplay shows "no valid move — undo or restart"
	else:
		_hint_node = completion[0]
	queue_redraw()

# --------------------------------------------------------------------------
# Process (only while dragging or flashing) and drawing
# --------------------------------------------------------------------------
func _process(delta: float) -> void:
	if _flash > 0.0:
		_flash = maxf(0.0, _flash - delta)
		queue_redraw()
	if not _dragging and _flash <= 0.0:
		set_process(false)

func _draw() -> void:
	if engine == null:
		return
	# Edges (unused faint, used accent).
	for e in graph.edges:
		var used := engine.used_edges.has(e)
		var col := Style.line_color() if used else Style.node_color()
		var w := Style.LINE_WIDTH if used else Style.LINE_WIDTH * 0.5
		draw_line(_node_px(e.x), _node_px(e.y), col, w, true)

	# Preview segment from head to finger while dragging.
	if _dragging and engine.started():
		draw_line(_node_px(engine.current()), _pointer,
			Style.accent() * Color(1, 1, 1, 0.5), Style.LINE_WIDTH * 0.6, true)

	# Nodes.
	for nid in graph.node_ids:
		var p := _node_px(nid)
		var visited := _node_is_visited(nid)
		var col := Style.node_visited() if visited else Style.node_color()
		draw_circle(p, Style.NODE_RADIUS, col)
		# Current head: ring (shape cue, not color-only).
		if nid == engine.current():
			draw_arc(p, Style.NODE_RADIUS + 8.0, 0, TAU, 32, Style.ink(), 4.0, true)
		# Hint: dashed ring.
		if nid == _hint_node:
			draw_arc(p, Style.NODE_RADIUS + 14.0, 0, TAU, 24, Style.STAR, 4.0, true)

	# Invalid flash overlay (shape/brightness, not color-only).
	if _flash > 0.0:
		var a := _flash / 0.35 * 0.25
		draw_rect(Rect2(Vector2.ZERO, size), Style.DANGER * Color(1, 1, 1, a))

func _node_is_visited(nid: int) -> bool:
	for e in engine.used_edges.keys():
		if e.x == nid or e.y == nid:
			return true
	return nid == engine.current()
