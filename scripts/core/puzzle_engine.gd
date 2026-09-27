extends RefCounted
class_name PuzzleEngine
## Runtime one-stroke puzzle engine — GDScript port of tools/oneline/rules.py
## (PuzzleState). This is the single owner of gameplay truth for the runtime and
## deliberately contains no rendering (docs/ARCHITECTURE_RULES.md).

enum MoveResult {
	OK,
	OK_COMPLETED,
	INVALID_NO_EDGE,
	INVALID_EDGE_USED,
	INVALID_SAME_NODE,
	INVALID_NOT_STARTED,
}

var graph: PuzzleGraph
var trail: Array[int] = []
var used_edges: Dictionary = {}     # Vector2i -> true
var mistakes: int = 0

signal moved(node_id: int)
signal invalid_move(node_id: int, reason: int)
signal completed()

func _init(puzzle_graph: PuzzleGraph) -> void:
	graph = puzzle_graph

func started() -> bool:
	return trail.size() > 0

func current() -> int:
	return trail[trail.size() - 1] if started() else -1

func used_count() -> int:
	return used_edges.size()

func is_complete() -> bool:
	return graph.edge_count() > 0 and used_count() == graph.edge_count()

func can_move_to(node_id: int) -> int:
	if not started():
		return MoveResult.OK if graph.has_node(node_id) else MoveResult.INVALID_NO_EDGE
	var cur := current()
	if node_id == cur:
		return MoveResult.INVALID_SAME_NODE
	if not graph.has_edge(cur, node_id):
		return MoveResult.INVALID_NO_EDGE
	if used_edges.has(PuzzleGraph.normalize_edge(cur, node_id)):
		return MoveResult.INVALID_EDGE_USED
	return MoveResult.OK

func valid_next_nodes() -> Array[int]:
	if not started():
		return graph.node_ids.duplicate()
	var cur := current()
	var out: Array[int] = []
	for nb in graph.neighbors(cur):
		if not used_edges.has(PuzzleGraph.normalize_edge(cur, nb)):
			out.append(nb)
	out.sort()
	return out

## Attempt to place/extend the line onto node_id. Emits signals and returns a
## MoveResult. Invalid attempts increment `mistakes` and do not change state.
func move_to(node_id: int) -> int:
	var result := can_move_to(node_id)
	if result != MoveResult.OK:
		mistakes += 1
		invalid_move.emit(node_id, result)
		return result
	if not started():
		trail.append(node_id)
		moved.emit(node_id)
		return MoveResult.OK
	var cur := current()
	used_edges[PuzzleGraph.normalize_edge(cur, node_id)] = true
	trail.append(node_id)
	moved.emit(node_id)
	if is_complete():
		completed.emit()
		return MoveResult.OK_COMPLETED
	return MoveResult.OK

func undo() -> bool:
	if trail.size() < 2:
		if started():
			trail.pop_back()
			return true
		return false
	var last: int = trail.pop_back()
	var prev: int = trail[trail.size() - 1]
	used_edges.erase(PuzzleGraph.normalize_edge(prev, last))
	mistakes += 1
	return true

func restart() -> void:
	trail.clear()
	used_edges.clear()
	mistakes = 0

func stars(three_max: int, two_max: int) -> int:
	return StarRules.compute_stars(mistakes, three_max, two_max, is_complete())
