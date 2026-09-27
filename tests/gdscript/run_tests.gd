extends SceneTree
## Headless GDScript conformance tests for the ONE LINE core engine.
##
## Run with a Godot 4.x binary (not required to ship, used in CI where available):
##     godot --headless --path . --script tests/gdscript/run_tests.gd
##
## Exercises the pure engine classes (no autoloads) so it verifies that the
## GDScript runtime rules agree with the authoritative Python engine
## (docs/GAME_RULES.md §13). Exit code is non-zero on any failure.

var _failures := 0
var _checks := 0

func _init() -> void:
	_test_graph()
	_test_engine()
	_test_stars()
	_test_solver()
	_test_daily()
	print("GDScript conformance: %d checks, %d failures" % [_checks, _failures])
	quit(1 if _failures > 0 else 0)

func _check(cond: bool, msg: String) -> void:
	_checks += 1
	if not cond:
		_failures += 1
		push_error("FAIL: " + msg)
		print("FAIL: " + msg)

func _triangle() -> PuzzleGraph:
	var pos := {0: Vector2(0.2, 0.2), 1: Vector2(0.8, 0.2), 2: Vector2(0.5, 0.8)}
	return PuzzleGraph.new(pos, [Vector2i(0, 1), Vector2i(1, 2), Vector2i(0, 2)])

func _path() -> PuzzleGraph:
	var pos := {0: Vector2(0, 0), 1: Vector2(0.5, 0), 2: Vector2(1, 0)}
	return PuzzleGraph.new(pos, [Vector2i(0, 1), Vector2i(1, 2)])

func _test_graph() -> void:
	var t := _triangle()
	_check(t.edge_count() == 3, "triangle edge count")
	_check(t.has_eulerian_trail(), "triangle has eulerian trail")
	_check(t.odd_degree_nodes().size() == 0, "triangle no odd nodes")
	var p := _path()
	_check(p.odd_degree_nodes().size() == 2, "path has 2 odd nodes")
	_check(p.has_eulerian_trail(), "path has eulerian trail")
	# 4 odd -> no trail (square + both diagonals).
	var pos := {0: Vector2(0, 0), 1: Vector2(1, 0), 2: Vector2(1, 1), 3: Vector2(0, 1)}
	var g := PuzzleGraph.new(pos, [Vector2i(0, 1), Vector2i(1, 2), Vector2i(2, 3),
		Vector2i(0, 3), Vector2i(0, 2), Vector2i(1, 3)])
	_check(not g.has_eulerian_trail(), "4-odd graph has no trail")

func _test_engine() -> void:
	var e := PuzzleEngine.new(_triangle())
	_check(e.move_to(0) == PuzzleEngine.MoveResult.OK, "start on node 0")
	_check(e.move_to(1) == PuzzleEngine.MoveResult.OK, "0->1")
	_check(e.move_to(0) == PuzzleEngine.MoveResult.INVALID_EDGE_USED, "reuse edge invalid")
	_check(e.mistakes == 1, "mistake counted")
	_check(e.move_to(2) == PuzzleEngine.MoveResult.OK, "1->2")
	_check(e.move_to(0) == PuzzleEngine.MoveResult.OK_COMPLETED, "2->0 completes")
	_check(e.is_complete(), "triangle complete")
	# undo frees an edge and counts a mistake
	var e2 := PuzzleEngine.new(_path())
	e2.move_to(0)
	e2.move_to(1)
	_check(e2.used_count() == 1, "one edge used")
	_check(e2.undo(), "undo ok")
	_check(e2.used_count() == 0, "edge freed after undo")

func _test_stars() -> void:
	_check(StarRules.compute_stars(0, 0, 2, true) == 3, "0 mistakes -> 3 stars")
	_check(StarRules.compute_stars(2, 0, 2, true) == 2, "2 mistakes -> 2 stars")
	_check(StarRules.compute_stars(5, 0, 2, true) == 1, "5 mistakes -> 1 star")
	_check(StarRules.compute_stars(0, 0, 2, false) == 0, "not complete -> 0 stars")
	var th := StarRules.default_thresholds(8)
	_check(th["two_max"] == 2, "default two_max for 8 edges")

func _test_solver() -> void:
	var trail := PuzzleSolver.find_eulerian_trail(_triangle())
	_check(trail.size() == 4, "solver trail length E+1")
	var completion := PuzzleSolver.find_completion(_triangle(), {}, -1)
	_check(completion.size() >= 1, "completion suggests a start")

func _fresh_daily() -> Dictionary:
	return {"last_date": null, "streak": 0, "best_streak": 0, "completed_dates": []}

func _test_daily() -> void:
	_check(DailyRules.is_consecutive("2026-09-25", "2026-09-26"), "consecutive days")
	_check(not DailyRules.is_consecutive("2026-09-25", "2026-09-27"), "gap not consecutive")
	_check(DailyRules.is_consecutive("2026-02-28", "2026-03-01"), "month rollover")

	var daily := _fresh_daily()
	var stats := {"current_streak": 0, "best_streak": 0}
	_check(DailyRules.apply_completion(daily, stats, "2026-09-25"), "first completion is new")
	DailyRules.apply_completion(daily, stats, "2026-09-26")
	DailyRules.apply_completion(daily, stats, "2026-09-27")
	_check(int(daily["streak"]) == 3, "streak builds to 3")
	_check(int(daily["best_streak"]) == 3, "best streak 3")
	_check(int(stats["current_streak"]) == 3, "stats streak mirrored")

	# Same-day replay is a no-op.
	_check(not DailyRules.apply_completion(daily, stats, "2026-09-27"), "same day not new")
	_check(int(daily["streak"]) == 3, "same-day replay no bump")

	# Gap resets current but keeps best.
	DailyRules.apply_completion(daily, stats, "2026-09-30")
	_check(int(daily["streak"]) == 1, "gap resets streak")
	_check(int(daily["best_streak"]) == 3, "best streak preserved after gap")

	# Backward date resets, does not crash.
	DailyRules.apply_completion(daily, stats, "2026-09-20")
	_check(int(daily["streak"]) == 1, "backward date resets")
