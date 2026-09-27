extends SceneTree
## Full-campaign runtime regression (Phase 2 audit §5, §7).
##
## Loads EVERY shipped level through the actual Godot runtime path
## (LevelLoader -> Level -> PuzzleGraph -> LevelValidator -> PuzzleEngine),
## solves it, replays the solution through the runtime rules to confirm
## completion, and verifies the hint (PuzzleSolver.find_completion) at several
## partial-trail prefixes. This prevents a level that is valid in Python but
## broken in Godot, and proves hint reliability on all levels.
##
## Run: godot --headless --path . --script tests/gdscript/campaign_test.gd

var _failures := 0
var _levels := 0
var _hints := 0

func _init() -> void:
	var index := LevelLoader.load_index()
	if index.is_empty():
		_fail("level index empty or missing")
		_finish()
		return

	for entry in index:
		var id := int(entry["id"])
		var level := LevelLoader.load_level(id)
		if level == null:
			_fail("level %d failed to load" % id)
			continue
		var vr := LevelValidator.validate(level)
		if not vr["ok"]:
			_fail("level %d invalid in runtime: %s" % [id, str(vr["errors"])])
			continue

		var graph := level.to_graph()
		var solution := PuzzleSolver.find_eulerian_trail(graph)
		if solution.size() != graph.edge_count() + 1:
			_fail("level %d: solver did not cover all edges" % id)
			continue

		# Replay the full solution through the runtime engine.
		if not _replay_completes(graph, solution):
			_fail("level %d: solution rejected by runtime rules" % id)
			continue

		# Hint checks at a spread of prefixes.
		var e := graph.edge_count()
		var prefixes := _unique_prefixes(e)
		for k in prefixes:
			if not _check_hint_at_prefix(graph, solution, k, id):
				pass  # failure already recorded
		_levels += 1

	_finish()

func _unique_prefixes(e: int) -> Array:
	var s := {}
	for v in [0, 1, e / 2, maxi(0, e - 1)]:
		s[v] = true
	return s.keys()

func _replay_completes(graph: PuzzleGraph, seq: Array) -> bool:
	var eng := PuzzleEngine.new(graph)
	eng.move_to(seq[0])
	for i in range(1, seq.size()):
		var res := eng.move_to(seq[i])
		if res == PuzzleEngine.MoveResult.INVALID_NO_EDGE \
				or res == PuzzleEngine.MoveResult.INVALID_EDGE_USED \
				or res == PuzzleEngine.MoveResult.INVALID_SAME_NODE:
			return false
	return eng.is_complete()

func _check_hint_at_prefix(graph: PuzzleGraph, solution: Array, k: int, id: int) -> bool:
	var eng := PuzzleEngine.new(graph)
	eng.move_to(solution[0])
	for i in range(1, k + 1):
		eng.move_to(solution[i])
	var hint := PuzzleSolver.find_completion(graph, eng.used_edges, eng.current())
	if hint.is_empty():
		_fail("level %d k=%d: hint empty" % [id, k])
		return false
	if eng.can_move_to(hint[0]) != PuzzleEngine.MoveResult.OK:
		_fail("level %d k=%d: hint suggests invalid move" % [id, k])
		return false
	# Applying the whole suggested completion must finish the puzzle.
	for node in hint:
		eng.move_to(node)
	if not eng.is_complete():
		_fail("level %d k=%d: completion did not finish" % [id, k])
		return false
	_hints += 1
	return true

func _fail(msg: String) -> void:
	_failures += 1
	push_error("FAIL: " + msg)
	print("FAIL: " + msg)

func _finish() -> void:
	print("Campaign runtime test: %d levels, %d hint checks, %d failures"
		% [_levels, _hints, _failures])
	quit(1 if _failures > 0 else 0)
